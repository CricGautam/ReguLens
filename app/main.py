
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from app.pii_shield import mask_pii

from app.database import (
    initialize_database,
    register_document,
    update_document_status,
    update_document_type,
)
from app.document_processor import extract_pdf_text
from app.classifier import classify_document

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
        document_type = classify_document(extracted_text)
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
                saved_text_path.relative_to(PROJECT_ROOT)
            ),
            "message": "PDF uploaded, extracted, and classified successfully",
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
