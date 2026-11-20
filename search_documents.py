
import sqlite3

DB_PATH = "data/imbere_rwanda.db"

def search_documents():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    print("\n=== IMBERE_RWANDA KNOWLEDGE SEARCH ===")

    print("\nAvailable categories:")
    print("agriculture")
    print("healthcare")
    print("culture")
    print("genocide_1994")
    print("education")
    print("tourism")

    category = input(
        "\nEnter category (or press Enter for all): "
    ).strip().lower()

    language = input(
        "Enter language (en, rw, fr, sw, or Enter for all): "
    ).strip().lower()

    search_term = input(
        "What information are you looking for? "
    ).strip()

    if not search_term:
        print("Please enter a search term.")
        connection.close()
        return

    if category:
        cursor.execute(
            "SELECT id FROM categories WHERE code = ?",
            (category,)
        )
        if cursor.fetchone() is None:
            print("Unknown category.")
            connection.close()
            return

    if language and language not in ["en", "rw", "fr", "sw"]:
        print("Unsupported language.")
        connection.close()
        return

    query = """
        SELECT
            documents.title,
            documents.language,
            categories.name,
            documents.content,
            sources.title,
            sources.organization,
            sources.source_url
        FROM documents
        JOIN categories
            ON documents.category_id = categories.id
        LEFT JOIN sources
            ON documents.source_id = sources.id
        WHERE (
            documents.title LIKE ?
            OR documents.content LIKE ?
        )
    """

    parameters = [
        f"%{search_term}%",
        f"%{search_term}%"
    ]

    if category:
        query += " AND categories.code = ?"
        parameters.append(category)

    if language:
        query += " AND documents.language = ?"
        parameters.append(language)

    query += " ORDER BY documents.id DESC"

    cursor.execute(query, parameters)
    results = cursor.fetchall()

    print("\n=== SEARCH RESULTS ===")

    if not results:
        print("No matching knowledge documents found.")
        print("Imbere_Rwanda does not have enough stored")
        print("information to answer from this search.")
    else:
        for number, result in enumerate(results, start=1):
            title, lang, cat, content, source, organization, url = result

            print(f"\nDOCUMENT {number}")
            print("Title:", title)
            print("Language:", lang)
            print("Category:", cat)
            print("\nKNOWLEDGE:")
            print(content)
            print("\nSOURCE:")
            print("Document:", source)
            print("Organization:", organization)
            print("URL:", url)

        print("\nEvidence retrieved from stored documents.")
        print("This search does not independently verify")
        print("whether the source is accurate or current.")

    connection.close()


if __name__ == "__main__":
    search_documents()
