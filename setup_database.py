
import sqlite3
from pathlib import Path

# Create the data folder
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Database file
DB_PATH = DATA_DIR / "imbere_rwanda.db"

# Six knowledge categories
CATEGORIES = [
    ("agriculture", "Agriculture and Rural Development"),
    ("healthcare", "Healthcare and Public Health"),
    ("culture", "Culture and Traditions"),
    ("genocide_1994", "1994 Genocide against the Tutsi"),
    ("education", "Education"),
    ("tourism", "Tourism and Heritage"),
]

def setup_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            organization TEXT,
            source_url TEXT,
            publication_date TEXT,
            source_type TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            source_id INTEGER,
            title TEXT NOT NULL,
            language TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (source_id) REFERENCES sources(id)
        )
    """)

    cursor.executemany("""
        INSERT OR IGNORE INTO categories (code, name)
        VALUES (?, ?)
    """, CATEGORIES)

    connection.commit()

    print("Imbere_Rwanda database created successfully!")
    print("\nKnowledge categories:")

    cursor.execute("SELECT code, name FROM categories")

    for code, name in cursor.fetchall():
        print(f"- {name} ({code})")

    connection.close()


if __name__ == "__main__":
    setup_database()
