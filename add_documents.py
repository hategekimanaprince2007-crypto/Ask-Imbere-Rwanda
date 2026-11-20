
# ==========================================
# IMBERE_RWANDA AI
# RWANDA KNOWLEDGE DATABASE
# ==========================================

import json
from pathlib import Path

import chromadb
from openai import OpenAI

# Project folders
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "chroma_db"
SOURCE_FILE = DATA_DIR / "sources.jsonl"

# Allowed categories and languages
CATEGORIES = {
    "agriculture",
    "healthcare",
    "culture",
    "genocide_1994",
    "education",
    "tourism"
}

LANGUAGES = {"en", "rw", "fr", "sw"}

# Connect to OpenAI
ai_client = OpenAI()

# Create persistent database
db = chromadb.PersistentClient(
    path=str(DB_DIR)
)

# Create or open knowledge collection
collection = db.get_or_create_collection(
    name="imbere_rwanda_knowledge"
)

# Read knowledge documents
documents = []
metadata_list = []
document_ids = []

with open(SOURCE_FILE, "r", encoding="utf-8") as file:

    for line_number, line in enumerate(file, start=1):

        if not line.strip():
            continue

        record = json.loads(line)

        required = [
            "id", "category", "language", "title",
            "text", "source_title", "source_url",
            "author", "publication_date", "source_type"
        ]

        for field in required:
            if not record.get(field):
                raise ValueError(
                    f"Missing {field} on line {line_number}"
                )

        if record["category"] not in CATEGORIES:
            raise ValueError("Invalid category")

        if record["language"] not in LANGUAGES:
            raise ValueError("Invalid language")

        if record["text"].startswith("REPLACE"):
            print("Skipping unfinished template.")
            continue

        if not record["source_url"].startswith("https://"):
            raise ValueError("Source must use an HTTPS URL")

        documents.append(record["text"])

        document_ids.append(record["id"])

        metadata_list.append({
            "category": record["category"],
            "language": record["language"],
            "title": record["title"],
            "source_title": record["source_title"],
            "source_url": record["source_url"],
            "author": record["author"],
            "publication_date": record["publication_date"],
            "source_type": record["source_type"]
        })

# Stop if there are no completed documents
if not documents:
    print("No completed documents found.")
    raise SystemExit

# Generate multilingual text embeddings
embedding_response = ai_client.embeddings.create(
    model="text-embedding-3-small",
    input=documents
)

embeddings = [
    item.embedding
    for item in embedding_response.data
]

# Store documents and their metadata
collection.upsert(
    ids=document_ids,
    documents=documents,
    metadatas=metadata_list,
    embeddings=embeddings
)

print("===================================")
print("IMBERE_RWANDA KNOWLEDGE DATABASE")
print("===================================")
print("Documents imported:", len(documents))
print("Total documents:", collection.count())
print("Database saved successfully!")
