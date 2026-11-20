
from pathlib import Path
import random
import sqlite3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from conversation_engine import classify_message


# ==========================================
# IMBERE_RWANDA AI - MAIN BACKEND
# ==========================================

app = FastAPI(
    title="Imbere_Rwanda AI",
    description="A Rwanda-focused knowledge and conversation assistant",
    version="1.4.0"
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# DATABASE AND WEBSITE SETTINGS
# ==========================================

BASE_DIR = Path(__file__).parent

DB_PATH = BASE_DIR / "data" / "imbere_rwanda.db"
WEBSITE_DIR = BASE_DIR / "website"

SUPPORTED_LANGUAGES = ["en", "rw", "fr", "sw"]

CATEGORY_NAMES = {
    "agriculture": "Agriculture",
    "healthcare": "Healthcare",
    "culture": "Culture and Traditions",
    "genocide_1994": "History",
    "education": "Education",
    "tourism": "Tourism and Heritage"
}


# ==========================================
# CHAT REQUEST MODEL
# ==========================================

class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    category: str | None = None


# ==========================================
# CONVERSATION ENGINE INTEGRATION
# ==========================================

def detect_conversation(message: str, selected_category=None):
    """
    Connect the external conversation engine
    to the main FastAPI backend.
    """

    return classify_message(message, selected_category)


# ==========================================
# KNOWLEDGE LIBRARY SEARCH
# ==========================================

def search_knowledge(message, language, category):
    """
    Search stored documents in the SQLite database.
    Return matching documents and their sources.
    """

    if not DB_PATH.exists():
        return [], "The knowledge database could not be found."

    words = re.findall(
        r"\w+",
        message.lower(),
        flags=re.UNICODE
    )

    words = [word for word in words if len(word) >= 3][:8]

    if not words:
        return [], "Please provide a little more detail in your question."

    conditions = []
    parameters = []

    for word in words:
        conditions.append(
            "(documents.title LIKE ? OR documents.content LIKE ?)"
        )

        parameters.extend([
            f"%{word}%",
            f"%{word}%"
        ])

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
    """

    query += " OR ".join(conditions) + ")"

    if language in SUPPORTED_LANGUAGES:
        query += " AND documents.language = ?"
        parameters.append(language)

    if category:
        if category not in CATEGORY_NAMES:
            return [], "That knowledge category is not recognized."

        query += " AND categories.code = ?"
        parameters.append(category)

    query += " ORDER BY documents.id DESC LIMIT 5"

    try:
        connection = sqlite3.connect(DB_PATH)

        try:
            cursor = connection.cursor()
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

        finally:
            connection.close()

    except sqlite3.Error as error:
        return [], f"Database search failed: {error}"

    results = []

    for row in rows:
        results.append({
            "title": row[0],
            "language": row[1],
            "category": row[2],
            "content": row[3],
            "source_title": row[4],
            "organization": row[5],
            "source_url": row[6]
        })

    return results, None


# ==========================================
# STANDARD RESPONSE HELPER
# ==========================================

def create_response(intent, answer, category=None):
    """
    Create a consistent response structure.
    """

    return {
        "intent": intent,
        "category": category,
        "answer": answer
    }


# ==========================================
# HOMEPAGE ENDPOINT
# ==========================================

@app.get("/")
def home():

    homepage = WEBSITE_DIR / "index.html"

    if not homepage.exists():
        return {
            "name": "Imbere_Rwanda",
            "status": "running",
            "message": "Website homepage could not be found."
        }

    return FileResponse(homepage)


# ==========================================
# HEALTH CHECK ENDPOINT
# ==========================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "database_found": DB_PATH.exists(),
        "website_found": WEBSITE_DIR.exists(),
        "conversation_engine": "connected"
    }


# ==========================================
# CHAT ENDPOINT
# ==========================================

@app.post("/chat")
def chat(request: ChatRequest):

    message = request.message.strip()
    language = request.language.lower()

    # --------------------------------------
    # 1. EMPTY MESSAGE
    # --------------------------------------

    if not message:
        return create_response(
            "empty",
            "Please enter a message."
        )

    # --------------------------------------
    # 2. VALIDATE LANGUAGE
    # --------------------------------------

    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    # --------------------------------------
    # 3. VALIDATE CATEGORY
    # --------------------------------------

    if request.category and request.category not in CATEGORY_NAMES:
        return create_response(
            "invalid_category",
            "That knowledge category is not recognized."
        )

    # --------------------------------------
    # 4. CLASSIFY USER MESSAGE
    # --------------------------------------

    try:
        classification = detect_conversation(
            message,
            request.category
        )

        intent = classification["intent"]
        category = classification.get("category")

    except (KeyError, TypeError, AttributeError):
        return create_response(
            "classification_error",
            "I could not understand your message. Please try again."
        )

    # --------------------------------------
    # 5. GREETING
    # --------------------------------------

    if intent == "greeting":

        return create_response(
            intent,
            (
                "Hello! Welcome to Imbere_Rwanda. "
                "What would you like to explore today?"
            ),
            category
        )

    # --------------------------------------
    # 6. FAREWELL
    # --------------------------------------

    if intent == "farewell":

        return create_response(
            intent,
            (
                "Goodbye! Thank you for visiting "
                "Imbere_Rwanda. Have a wonderful day!"
            ),
            category
        )

    # --------------------------------------
    # 7. THANK YOU
    # --------------------------------------

    if intent == "thanks":

        return create_response(
            intent,
            (
                "You're welcome! I'm happy to help "
                "you explore Rwanda."
            ),
            category
        )

    # --------------------------------------
    # 8. EVERYDAY CONVERSATION
    # --------------------------------------

    if intent == "casual_chat":

        return create_response(
            intent,
            (
                "I'm doing well, thank you! "
                "What would you like to learn about Rwanda?"
            ),
            category
        )

    # --------------------------------------
    # 9. ASSISTANT IDENTITY
    # --------------------------------------

    if intent == "capabilities":

        return create_response(
            intent,
            (
                "I'm Imbere_Rwanda, a Rwanda-focused "
                "knowledge assistant. I can help you explore "
                "agriculture, healthcare, culture, history, "
                "education, tourism and heritage. "
                "I can also handle everyday conversations "
                "and retrieve information from my knowledge library."
            ),
            category
        )

    # --------------------------------------
    # 10. GENERAL QUESTIONS
    # --------------------------------------

    if intent == "general_question":

        return create_response(
            intent,
            (
                "That is an interesting question. "
                "My general-purpose AI knowledge model "
                "is not connected yet. However, I can "
                "retrieve information from the "
                "Imbere_Rwanda knowledge library."
            ),
            category
        )

    # --------------------------------------
    # 11. UNKNOWN MESSAGE
    # --------------------------------------

    if intent == "unknown":

        return create_response(
            intent,
            (
                "I'm not sure I understand your message. "
                "You can ask me about Rwanda's agriculture, "
                "healthcare, culture, history, education "
                "or tourism."
            ),
            category
        )

    # --------------------------------------
    # 12. SEARCH KNOWLEDGE DATABASE
    # --------------------------------------

    documents, error = search_knowledge(
        message,
        language,
        category
    )

    # --------------------------------------
    # 13. DATABASE ERROR
    # --------------------------------------

    if error:

        return {
            "intent": "knowledge",
            "category": category,
            "answer": error,
            "documents": [],
            "sources": []
        }

    # --------------------------------------
    # 14. NO MATCHING DOCUMENTS
    # --------------------------------------

    if not documents:

        return {
            "intent": "knowledge",
            "category": category,
            "answer": (
                "I couldn't find enough information in the "
                "current Imbere_Rwanda knowledge library "
                "to answer that reliably. The library may "
                "need more documents."
            ),
            "documents": [],
            "sources": []
        }

    # --------------------------------------
    # 15. RETURN KNOWLEDGE RESULTS
    # --------------------------------------

    return {
        "intent": "knowledge",
        "category": category,
        "answer": (
            "I found the following information in the "
            "Imbere_Rwanda knowledge library. "
            "Please review the information and sources below."
        ),
        "documents": documents,
        "notice": (
            "These are retrieved documents, not independently "
            "verified or newly generated AI conclusions."
        )
    }


# ==========================================
# SERVE WEBSITE FILES
# ==========================================

app.mount(
    "/",
    StaticFiles(directory=WEBSITE_DIR),
    name="website"
)
