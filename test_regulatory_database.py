from app.database import get_connection

with get_connection() as connection:
    rows = connection.execute("""
        SELECT
            id,
            requirement_code,
            legal_reference,
            source_document,
            source_page
        FROM regulatory_requirements
        ORDER BY id
    """).fetchall()

print(f"Existing requirements: {len(rows)}")

for row in rows:
    print(dict(row))