
import sqlite3
from pathlib import Path

DB_PATH = Path("data") / "imbere_rwanda.db"

LANGUAGES = ["en", "rw", "fr", "sw"]

def add_document():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    print("\n=== Imbere_Rwanda: Add a Knowledge Document ===")

    # Show available categories
    cursor.execute("SELECT id, code, name FROM categories")
    categories = cursor.fetchall()

    print("\nAvailable categories:")
    for category_id, code, name in categories:
        print(f"{category_id}. {name} ({code})")

    category_code = input("\nEnter the category code: ").strip().lower()

    category = next(
        (item for item in categories if item[1] == category_code),
        None
    )

    if category is None:
        print("Invalid category code.")
        connection.close()
        return

    language = input("Language (en, rw, fr, sw): ").strip().lower()

    if language not in LANGUAGES:
        print("Invalid language code.")
        connection.close()
        return

    title = input("Document title: ").strip()
    organization = input("Source organization: ").strip()
    source_title = input("Source title: ").strip()
    source_url = input("Source URL: ").strip()
    publication_date = input("Publication date (or leave blank): ").strip()
    source_type = input("Source type (official, research, book, etc.): ").strip()

    print("\nEnter your original summary or notes.")
    print("When finished, type END on a new line.")

    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    content = "\n".join(lines).strip()

    if not title or not content or not source_title or not source_url:
        print("Title, content, source title, and source URL are required.")
        connection.close()
        return

    cursor.execute("""
        INSERT INTO sources (
            title, organization, source_url,
            publication_date, source_type
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        source_title,
        organization,
        source_url,
        publication_date,
        source_type
    ))

    source_id = cursor.lastrowid
    category_id = category[0]

    cursor.execute("""
        INSERT INTO documents (
            category_id, source_id, title, language, content
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        category_id,
        source_id,
        title,
        language,
        content
    ))

    connection.commit()
    connection.close()

    print("\nDocument saved successfully!")

if __name__ == "__main__":
    add_document()
