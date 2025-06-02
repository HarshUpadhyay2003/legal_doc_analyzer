import sqlite3
from datetime import datetime
import json

DB_NAME = "legal_docs.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            upload_time TEXT,
            full_text TEXT,
            summary TEXT,
            clauses TEXT
        )
    ''')
    c.execute('''
    CREATE VIRTUAL TABLE IF NOT EXISTS document_fts 
    USING fts5(
        title, 
        content, 
        summary, 
        content='documents', 
        content_rowid='id'
    )
''')

    conn.commit()
    conn.close()

def save_document(title, full_text, summary, clauses):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Insert into main table
    c.execute('''
        INSERT INTO documents (title, upload_time, full_text, summary, clauses)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        title,
        datetime.utcnow().isoformat(),
        full_text,
        summary,
        json.dumps(clauses)
    ))

    doc_id = c.lastrowid  # capture inserted document ID

    # Insert into FTS5 index
    c.execute('''
        INSERT INTO document_fts(rowid, title, content, summary)
        VALUES (?, ?, ?, ?)
    ''', (
        doc_id,
        title,
        full_text,
        summary
    ))

    conn.commit()
    conn.close()


def get_all_documents():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, title, upload_time FROM documents ORDER BY upload_time DESC')
    rows = c.fetchall()
    conn.close()

    return [
        {"id": row[0], "title": row[1], "upload_time": row[2]}
        for row in rows
    ]

def get_document_by_id(doc_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, title, upload_time, full_text, summary, clauses FROM documents WHERE id = ?', (doc_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "title": row[1],
            "upload_time": row[2],
            "full_text": row[3],
            "summary": row[4],
            "clauses": json.loads(row[5] or "[]")
        }
    else:
        return None

def search_documents(query):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    wildcard = f"%{query.lower()}%"
    c.execute('''
        SELECT id, title, upload_time FROM documents
        WHERE lower(title) LIKE ? OR lower(clauses) LIKE ?
    ''', (wildcard, wildcard))
    rows = c.fetchall()
    conn.close()

    return [
        {"id": row[0], "title": row[1], "upload_time": row[2]}
        for row in rows
    ]
