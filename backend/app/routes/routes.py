import os
import sqlite3
from flask import Blueprint, request, jsonify
from app.utils.extract_text import extract_text_from_pdf
from app.utils.summarizer import generate_summary
from app.utils.clause_detector import detect_clauses
from app.database import save_document
from app.database import get_all_documents, get_document_by_id
from app.database import search_documents
from app.nlp.qa import answer_question
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.error_handler import handle_errors


main = Blueprint("main", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(BASE_DIR, 'legal_docs.db')


@main.route('/upload', methods=['POST'])
@handle_errors
def upload_file():
    file = request.files.get('file')
    
    if file is None or file.filename == '':
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    try:
        text = extract_text_from_pdf(file)
        
        if not text.strip():
            return jsonify({"success": False, "error": "No text extracted from PDF"}), 400

        return jsonify({
            "success": True,
            "text": text,
            "length": len(text),
            "filename": file.filename
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main.route('/summarize', methods=['POST'])
@handle_errors
def summarize():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Text is required"}), 400

    summary = generate_summary(text)
    return jsonify({"summary": summary})


@main.route('/detect_clauses', methods=['POST'])
@handle_errors
def detect_clauses_route():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "Text input is required."}), 400

    results = detect_clauses(text)
    return jsonify({'clauses':results}), 200


@main.route('/save_document', methods=['POST'])
@handle_errors
def save_document_route():
    data = request.get_json()

    title = data.get("title")
    full_text = data.get("full_text")
    summary = data.get("summary")
    clauses = data.get("clauses")

    if not all([title, full_text]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        save_document(title, full_text, summary or "", clauses or [])
        return jsonify({"message": "Document saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/documents', methods=['GET'])
@handle_errors
def list_documents():
    try:
        docs = get_all_documents()
        return jsonify(docs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/get_document/<int:doc_id>', methods=['GET'])
@handle_errors
def get_document(doc_id):
    doc = get_document_by_id(doc_id)
    if doc:
        return jsonify(doc), 200
    else:
        return jsonify({"error": "Document not found"}), 404


@main.route('/search_documents', methods=['GET'])
@handle_errors
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    try:
        results = search_documents(query)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@main.route('/qa', methods=['POST'])
@handle_errors
def question_answering():
    data = request.get_json()
    doc_id = data.get("document_id")
    question = data.get("question")

    if not doc_id or not question:
        return jsonify({"error": "Both 'document_id' and 'question' are required"}), 400

    document = get_document_by_id(doc_id)
    if not document:
        return jsonify({"error": "Document not found"}), 404

    context = document.get("full_text", "")
    try:
        answer = answer_question(question, context)
        return jsonify(answer), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@main.route('/register', methods=['POST'])
@handle_errors
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_pw = generate_password_hash(password)
    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    except sqlite3.OperationalError as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()



@main.route('/login', methods=['POST'])
@handle_errors
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
    except sqlite3.OperationalError as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

    if row and check_password_hash(row[0], password):
        token = create_access_token(identity=username)
        return jsonify(access_token=token), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401
    

