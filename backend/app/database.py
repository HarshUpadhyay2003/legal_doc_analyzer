import sqlite3
import os
import logging
from datetime import datetime
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, 'legal_docs.db')

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
           CREATE TABLE IF NOT EXISTS users (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT UNIQUE NOT NULL,
       email TEXT UNIQUE NOT NULL,
       password_hash TEXT NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   )
        ''')

        # Create documents table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            full_text TEXT,
            summary TEXT,
            clauses TEXT,
            features TEXT,
            context_analysis TEXT,
            file_path TEXT,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        conn.close()

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database when module is imported
init_db()

def search_documents(query, search_type='all'):
    conn = sqlite3.connect(DB_PATH)
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

def save_document(title, full_text, summary, clauses, features, context_analysis, file_path):
    """Save a document to the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO documents (title, full_text, summary, clauses, features, context_analysis, file_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, full_text, summary, str(clauses), str(features), str(context_analysis), file_path))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        logging.error(f"Error saving document: {str(e)}")
        raise
    finally:
        conn.close()

def get_all_documents():
    """Get all documents from the database, including file size if available"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents ORDER BY upload_time DESC')
        documents = [dict(row) for row in cursor.fetchall()]
        for doc in documents:
            file_path = doc.get('file_path')
            if file_path and os.path.exists(file_path):
                doc['size'] = os.path.getsize(file_path)
            else:
                doc['size'] = None
        return documents
    except Exception as e:
        logging.error(f"Error fetching documents: {str(e)}")
        raise
    finally:
        conn.close()

def get_document_by_id(doc_id):
    """Get a specific document by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
        document = cursor.fetchone()
        return dict(document) if document else None
    except Exception as e:
        logging.error(f"Error fetching document {doc_id}: {str(e)}")
        raise
    finally:
        conn.close()

def delete_document(doc_id):
    """Delete a document from the database and return its file_path"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Fetch the file_path before deleting
        cursor.execute('SELECT file_path FROM documents WHERE id = ?', (doc_id,))
        row = cursor.fetchone()
        file_path = row[0] if row and row[0] else None
        # Now delete the document
        cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        conn.commit()
        return file_path
    except Exception as e:
        logging.error(f"Error deleting document {doc_id}: {str(e)}")
        raise
    finally:
        conn.close()
