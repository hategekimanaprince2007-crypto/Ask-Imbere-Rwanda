
import sqlite3

connection = sqlite3.connect("data/imbere_rwanda.db")
cursor = connection.cursor()

cursor.execute("""
    SELECT
        documents.title,
        documents.language,
        categories.name,
        sources.title
    FROM documents
    JOIN categories
        ON documents.category_id = categories.id
    JOIN sources
        ON documents.source_id = sources.id
""")

documents = cursor.fetchall()

print("\n=== Imbere_Rwanda Knowledge Library ===")

for document in documents:
    print("\nDocument:", document[0])
    print("Language:", document[1])
    print("Category:", document[2])
    print("Source:", document[3])

print("\nTotal documents:", len(documents))

connection.close()
