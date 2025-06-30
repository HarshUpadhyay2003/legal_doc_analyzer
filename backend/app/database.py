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

        # Create question_answers table for persisting Q&A
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            score REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
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

def migrate_add_user_id_to_documents():
    """Add user_id column to documents table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Check if user_id column exists
        cursor.execute("PRAGMA table_info(documents)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute('ALTER TABLE documents ADD COLUMN user_id INTEGER')
            conn.commit()
            logging.info("Added user_id column to documents table.")
    except Exception as e:
        logging.error(f"Migration error: {str(e)}")
        raise
    finally:
        conn.close()

# Call migration on import
migrate_add_user_id_to_documents()

def migrate_add_phone_company_to_users():
    """Add phone and company columns to users table if they don't exist."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'phone' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN phone TEXT')
        if 'company' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN company TEXT')
        conn.commit()
    except Exception as e:
        logging.error(f"Migration error: {str(e)}")
        raise
    finally:
        conn.close()

# Call migration on import
migrate_add_phone_company_to_users()

def save_document(title, full_text, summary, clauses, features, context_analysis, file_path, user_id):
    """Save a document to the database, associated with a user_id"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO documents (title, full_text, summary, clauses, features, context_analysis, file_path, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, full_text, summary, str(clauses), str(features), str(context_analysis), file_path, user_id))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        logging.error(f"Error saving document: {str(e)}")
        raise
    finally:
        conn.close()

def get_all_documents(user_id=None):
    """Get all documents for a user from the database, including file size if available"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if user_id is not None:
            cursor.execute('SELECT * FROM documents WHERE user_id = ? ORDER BY upload_time DESC', (user_id,))
        else:
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

def get_document_by_id(doc_id, user_id=None):
    """Get a specific document by ID, optionally filtered by user_id"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if user_id is not None:
            cursor.execute('SELECT * FROM documents WHERE id = ? AND user_id = ?', (doc_id, user_id))
        else:
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

def search_questions_answers(query, user_id=None):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        sql = '''
            SELECT id, document_id, question, answer, created_at
            FROM question_answers
            WHERE (question LIKE ? OR answer LIKE ?)
        '''
        params = [f'%{query}%', f'%{query}%']
        if user_id is not None:
            sql += ' AND user_id = ?'
            params.append(user_id)
        sql += ' ORDER BY created_at DESC'
        c.execute(sql, params)
        results = []
        for row in c.fetchall():
            results.append({
                'id': row[0],
                'document_id': row[1],
                'question': row[2],
                'answer': row[3],
                'created_at': row[4]
            })
        return results
    except Exception as e:
        logging.error(f"Error searching questions/answers: {str(e)}")
        raise
    finally:
        conn.close()

def get_user_profile(username):
    """Fetch user profile details by username."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT username, email, phone, company FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logging.error(f"Error fetching user profile: {str(e)}")
        raise
    finally:
        conn.close()

def update_user_profile(username, email, phone, company):
    """Update user profile details."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET email = ?, phone = ?, company = ? WHERE username = ?
        ''', (email, phone, company, username))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logging.error(f"Error updating user profile: {str(e)}")
        raise
    finally:
        conn.close()

def change_user_password(username, current_password, new_password):
    """Change user password if current password matches."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if not row:
            return False, 'User not found'
        from werkzeug.security import check_password_hash, generate_password_hash
        if not check_password_hash(row[0], current_password):
            return False, 'Current password is incorrect'
        new_hash = generate_password_hash(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (new_hash, username))
        conn.commit()
        return True, 'Password updated successfully'
    except Exception as e:
        logging.error(f"Error changing password: {str(e)}")
        raise
    finally:
        conn.close()
