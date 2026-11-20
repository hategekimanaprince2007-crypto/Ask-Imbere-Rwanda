
# ==========================================
# IMBERE_RWANDA AI
# KNOWLEDGE SEARCH ENGINE
# ==========================================

from pathlib import Path

import chromadb
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent

# Connect to AI and database
ai_client = OpenAI()

db = chromadb.PersistentClient(
    path=str(BASE_DIR / "data" / "chroma_db")
)

collection = db.get_collection(
    name="imbere_rwanda_knowledge"
)

print("================================")
print(" IMBERE_RWANDA KNOWLEDGE SEARCH")
print("================================")

if collection.count() == 0:
    print("The database is empty.")
    raise SystemExit

while True:

    question = input("\nAsk about Rwanda: ").strip()

    if question.lower() == "exit":
        print("Thank you for using Imbere_Rwanda!")
        break

    if not question:
        continue

    # Convert question into an embedding
    response = ai_client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )

    question_embedding = response.data[0].embedding

    # Search the knowledge database
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(5, collection.count())
    )

    print("\nRELEVANT KNOWLEDGE")
    print("------------------------------")

    for i, document in enumerate(results["documents"][0]):

        metadata = results["metadatas"][0][i]

        print("\nTitle:", metadata["title"])
        print("Category:", metadata["category"])
        print("Language:", metadata["language"])
        print("Source:", metadata["source_title"])
        print("Reference:", metadata["source_url"])
        print("\nInformation:")
        print(document)

        print("------------------------------")
