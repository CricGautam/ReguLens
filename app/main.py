
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from app.pii_shield import mask_pii

from pydantic import BaseModel, Field
from app.ML.query_router_service import route_query
from app.Orchestration.compliance_graph import compliance_graph

from app.database import (
    initialize_database,
    register_document,
    update_document_status,
    update_document_type,
    get_document_by_id,
)
from app.document_processor import extract_pdf_text
from app.classifier import classify_document
from app.ML.document_classifier_service import predict_document_type

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


print("ReguLens API is ready to accept requests.")
@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="ReguLens API",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {"message": "ReguLens API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

class QueryRequest(BaseModel):
    query: str = Field(min_length=1)


@app.post("/queries/route")
def predict_query_route(request: QueryRequest):
    return route_query(request.query)


@app.post("/documents/upload")
def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    if Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted",
        )

    document_id = None
    saved_pdf_path = None
    saved_text_path = None

    try:
        # 1. Save the original PDF
        unique_id = uuid4().hex
        saved_pdf_path = RAW_DATA_DIR / f"{unique_id}.pdf"

        with saved_pdf_path.open("wb") as destination:
            while chunk := file.file.read(1024 * 1024):
                destination.write(chunk)

        # 2. Register the document
        document_id = register_document(
            filename=Path(file.filename).name,
            file_path=str(saved_pdf_path.relative_to(PROJECT_ROOT)),
            document_type=None,
        )

        update_document_status(document_id, "processing")

        # 3. Extract PDF text
        extracted_text = extract_pdf_text(saved_pdf_path)
        if not extracted_text.strip():
            raise ValueError("No extractable text found in the PDF.")
        #  Mask sensitive information
        masked_text = mask_pii(extracted_text)
        # 4. Classify the document
        document_type = classify_document(masked_text)

        # Experimental ML prediction (does not override existing classification)
        ml_prediction = predict_document_type(masked_text)
        # 5. Save the masked text
        saved_text_path = PROCESSED_DATA_DIR / f"{unique_id}.txt"
        saved_text_path.write_text(
            masked_text,
            encoding="utf-8",
        )

        # 6. Save the classification and final status
        update_document_type(document_id, document_type)
        update_document_status(document_id, "processed")

        return {
            "document_id": document_id,
            "filename": Path(file.filename).name,
            "document_type": document_type,
            "processing_status": "processed",
            "extracted_characters": len(extracted_text),
            "processed_text_path": str(
                saved_text_path.relative_to(PROJECT_ROOT),
            ),
            "ml_prediction": ml_prediction,
            "message": "PDF uploaded, extracted, and classified successfully"
        }

    except Exception as error:
        if document_id is not None:
            try:
                update_document_status(document_id, "failed")
            except Exception:
                pass

        if saved_text_path and saved_text_path.exists():
            saved_text_path.unlink()

        if document_id is None and saved_pdf_path and saved_pdf_path.exists():
            saved_pdf_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Upload or PDF processing failed. Check server logs.",
        ) from error

    finally:
        file.file.close()



class AssessmentRequest(BaseModel):
    query: str = Field(min_length=1)
    document_id: int = Field(gt=0)
    rule_number: int = Field(gt=0)


@app.post("/assessments/run")
def run_compliance_assessment(request: AssessmentRequest):

    # 1. Find the uploaded document in SQLite
    document = get_document_by_id(request.document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # 2. Only processed regulations can be assessed
    if document["processing_status"] != "processed":
        raise HTTPException(
            status_code=400,
            detail="Document is not ready for assessment"
        )

    if document["document_type"] != "regulation":
        raise HTTPException(
            status_code=400,
            detail="Selected document is not classified as a regulation"
        )

    # 3. Resolve the registered file safely
    raw_directory = RAW_DATA_DIR.resolve()
    regulation_path = (
        PROJECT_ROOT / document["file_path"]
    ).resolve()

    if (
        not regulation_path.is_relative_to(raw_directory)
        or regulation_path.suffix.lower() != ".pdf"
        or not regulation_path.is_file()
    ):
        raise HTTPException(
            status_code=400,
            detail="Registered regulation file is invalid or unavailable"
        )

    # 4. Execute our existing LangGraph workflow
    result = compliance_graph.invoke({
    "query": request.query,
    "document_id": request.document_id,
    "rule_number": request.rule_number
})

    return result["draft_report"]


