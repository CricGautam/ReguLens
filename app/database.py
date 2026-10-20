
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

        # New table for structured regulatory requirements
        connection.execute("""
            CREATE TABLE IF NOT EXISTS regulatory_requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requirement_code TEXT UNIQUE NOT NULL,
                regulation_name TEXT NOT NULL,
                legal_reference TEXT NOT NULL,
                requirement_text TEXT NOT NULL,
                applicability TEXT,
                effective_date TEXT,
                expected_evidence TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

def create_regulatory_requirements_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS regulatory_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requirement_code TEXT UNIQUE NOT NULL,
            regulation_name TEXT NOT NULL,
            legal_reference TEXT NOT NULL,
            requirement_text TEXT NOT NULL,
            applicability TEXT,
            effective_date TEXT,
            expected_evidence TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def add_regulatory_requirement(
    requirement_code,
    regulation_name,
    legal_reference,
    requirement_text,
    applicability,
    effective_date,
    expected_evidence
):
    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO regulatory_requirements (
                requirement_code,
                regulation_name,
                legal_reference,
                requirement_text,
                applicability,
                effective_date,
                expected_evidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            requirement_code,
            regulation_name,
            legal_reference,
            requirement_text,
            applicability,
            effective_date,
            expected_evidence
        ))

        return cursor.lastrowid

def add_requirement_source_columns():
    with get_connection() as connection:
        existing_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(regulatory_requirements)"
            ).fetchall()
        }

        if "source_document" not in existing_columns:
            connection.execute("""
                ALTER TABLE regulatory_requirements
                ADD COLUMN source_document TEXT
            """)

        if "source_page" not in existing_columns:
            connection.execute("""
                ALTER TABLE regulatory_requirements
                ADD COLUMN source_page INTEGER
            """)

def save_regulatory_requirement(
    requirement_code,
    regulation_name,
    legal_reference,
    requirement_text,
    applicability,
    effective_date,
    expected_evidence,
    source_document,
    source_page
):
    with get_connection() as connection:

        existing = connection.execute("""
            SELECT id
            FROM regulatory_requirements
            WHERE regulation_name = ?
              AND legal_reference = ?
        """, (
            regulation_name,
            legal_reference
        )).fetchone()

        if existing:
            return {
                "status": "already_exists",
                "id": existing["id"]
            }

        cursor = connection.execute("""
            INSERT INTO regulatory_requirements (
                requirement_code,
                regulation_name,
                legal_reference,
                requirement_text,
                applicability,
                effective_date,
                expected_evidence,
                source_document,
                source_page
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            requirement_code,
            regulation_name,
            legal_reference,
            requirement_text,
            applicability,
            effective_date,
            expected_evidence,
            source_document,
            source_page
        ))

        return {
            "status": "inserted",
            "id": cursor.lastrowid
        }

def add_parent_obligation_column():
    with get_connection() as connection:
        existing_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(regulatory_requirements)"
            ).fetchall()
        }

        if "parent_obligation" not in existing_columns:
            connection.execute("""
                ALTER TABLE regulatory_requirements
                ADD COLUMN parent_obligation TEXT
            """)
            print("parent_obligation column added")
        else:
            print("parent_obligation column already exists")

def update_requirement_parent_obligation(
    regulation_name,
    legal_reference,
    parent_obligation
):
    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE regulatory_requirements
            SET parent_obligation = ?
            WHERE regulation_name = ?
              AND legal_reference = ?
        """, (
            parent_obligation,
            regulation_name,
            legal_reference
        ))

        return cursor.rowcount