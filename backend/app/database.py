import sqlite3
from datetime import datetime
import json
import logging

DB_NAME = "legal_docs.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Create main documents table
        c.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                upload_time TEXT,
                full_text TEXT,
                summary TEXT,
                clauses TEXT,
                features TEXT,
                context_analysis TEXT
            )
        ''')
        
        # Create FTS5 virtual table
        c.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS document_fts 
            USING fts5(
                title, 
                content, 
                summary
            )
        ''')
        
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {str(e)}")
        raise
    finally:
        conn.close()

def search_documents(query, search_type='all'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Check if query is a number (potential ID)
        is_id_search = query.isdigit()
        
        if is_id_search:
            # Search by ID
            c.execute('''
                SELECT id, title, summary, upload_time, 1.0 as match_score
                FROM documents
                WHERE id = ?
            ''', (int(query),))
        else:
            # Search by title
            c.execute('''
                SELECT id, title, summary, upload_time, 1.0 as match_score
                FROM documents
                WHERE title LIKE ?
                ORDER BY id DESC
            ''', (f'%{query}%',))
        
        results = []
        for row in c.fetchall():
            results.append({
                "id": row[0],
                "title": row[1],
                "summary": row[2] or "",
                "upload_time": row[3],
                "match_score": row[4]
            })
        
        return results
    except sqlite3.Error as e:
        logging.error(f"Search error: {str(e)}")
        raise
    finally:
        conn.close()

def save_document(title, full_text, summary, clauses, features=None, context_analysis=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Insert into main table
        c.execute('''
            INSERT INTO documents (
                title, upload_time, full_text, summary, clauses, 
                features, context_analysis
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            title,
            datetime.utcnow().isoformat(),
            full_text,
            summary,
            json.dumps(clauses),
            json.dumps(features or {}),
            json.dumps(context_analysis or {})
        ))
        
        doc_id = c.lastrowid
        
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
        return doc_id
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Save document error: {str(e)}")
        raise
    finally:
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
    c.execute('''
        SELECT id, title, upload_time, full_text, summary, clauses, 
               features, context_analysis 
        FROM documents 
        WHERE id = ?
    ''', (doc_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "title": row[1],
            "upload_time": row[2],
            "full_text": row[3],
            "summary": row[4],
            "clauses": json.loads(row[5] or "[]"),
            "features": json.loads(row[6] or "{}"),
            "context_analysis": json.loads(row[7] or "{}")
        }
    else:
        return None
