
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "regulens.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                document_type TEXT,
                file_path TEXT NOT NULL,
                processing_status TEXT NOT NULL DEFAULT 'uploaded',
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def register_document(filename: str, file_path: str, document_type: str | None = None):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO documents (filename, document_type, file_path)
            VALUES (?, ?, ?)
            """,
            (filename, document_type, file_path),
        )

        return cursor.lastrowid


def update_document_status(document_id: int, status: str):
    allowed_statuses = {
        "uploaded",
        "processing",
        "processed",
        "failed",
    }

    if status not in allowed_statuses:
        raise ValueError(f"Invalid processing status: {status}")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE documents
            SET processing_status = ?
            WHERE id = ?
            """,
            (status, document_id),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"Document ID {document_id} not found")


def update_document_type(document_id: int, document_type: str):
    allowed_types = {
        "regulation",
        "internal_policy",
        "contract",
        "audit_evidence",
        "risk_record",
        "unknown",
    }

    if document_type not in allowed_types:
        raise ValueError(f"Invalid document type: {document_type}")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE documents
            SET document_type = ?
            WHERE id = ?
            """,
            (document_type, document_id),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"Document ID {document_id} not found")