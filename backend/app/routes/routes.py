import os
import sqlite3
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
from app.utils.extract_text import extract_text_from_pdf
from app.utils.summarizer import generate_summary
from app.utils.clause_detector import detect_clauses
from app.database import save_document, delete_document
from app.database import get_all_documents, get_document_by_id
from app.database import search_documents
from app.nlp.qa import answer_question
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, exceptions as jwt_exceptions
from flask_jwt_extended.exceptions import JWTDecodeError as JWTError
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.error_handler import handle_errors
from app.utils.enhanced_legal_processor import EnhancedLegalProcessor
from app.utils.legal_domain_features import LegalDomainFeatures
from app.utils.context_understanding import ContextUnderstanding
import logging
import textract

main = Blueprint("main", __name__)

# Initialize the processors
enhanced_legal_processor = EnhancedLegalProcessor()
legal_domain_processor = LegalDomainFeatures()
context_processor = ContextUnderstanding()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(BASE_DIR, 'legal_docs.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path):
    ext = file_path.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['doc', 'docx']:
        try:
            text = textract.process(file_path)
            return text.decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to extract text from {ext.upper()} file: {str(e)}")
    else:
        raise Exception("Unsupported file type for text extraction.")

@main.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Only PDF, DOC, DOCX are supported.'}), 400

        # Save file first
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Create initial document entry
        doc_id = save_document(
            title=filename,
            full_text="",  # Will be updated later
            summary="Processing...",
            clauses="[]",
            features="{}",
            context_analysis="{}",
            file_path=file_path
        )

        # Return immediate response with document ID
        return jsonify({
            'message': 'File uploaded successfully',
            'document_id': doc_id,
            'title': filename,
            'status': 'processing'
        }), 200

    except Exception as e:
        logging.error(f"Error during file upload: {str(e)}")
        return jsonify({'error': str(e)}), 500


@main.route('/documents', methods=['GET'])
@jwt_required()
def list_documents():
    logging.debug("Attempting to list documents...")
    try:
        identity = get_jwt_identity()
        logging.debug(f"JWT identity for listing documents: {identity}")
        docs = get_all_documents()
        logging.info(f"Successfully fetched {len(docs)} documents.")
        return jsonify(docs), 200
    except jwt_exceptions.NoAuthorizationError as e:
        logging.error(f"No authorization token provided for list documents: {str(e)}")
        return jsonify({"success": False, "error": "Authorization token missing"}), 401
    except jwt_exceptions.InvalidHeaderError as e:
        logging.error(f"Invalid authorization header for list documents: {str(e)}")
        return jsonify({"success": False, "error": "Invalid authorization header"}), 422
    except JWTError as e: # Catch general JWT errors
        logging.error(f"JWT error for list documents: {str(e)}")
        return jsonify({"success": False, "error": f"JWT error: {str(e)}"}), 422
    except Exception as e:
        logging.error(f"Error listing documents: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@main.route('/get_document/<int:doc_id>', methods=['GET'])
@jwt_required()
def get_document(doc_id):
    logging.debug(f"Attempting to get document with ID: {doc_id}")
    try:
        identity = get_jwt_identity()
        logging.debug(f"JWT identity for getting document: {identity}")
        doc = get_document_by_id(doc_id)
        if doc:
            logging.info(f"Successfully fetched document {doc_id}")
            return jsonify(doc), 200
        else:
            logging.warning(f"Document with ID {doc_id} not found.")
            return jsonify({"error": "Document not found"}), 404
    except jwt_exceptions.NoAuthorizationError as e:
        logging.error(f"No authorization token provided for get document: {str(e)}")
        return jsonify({"success": False, "error": "Authorization token missing"}), 401
    except jwt_exceptions.InvalidHeaderError as e:
        logging.error(f"Invalid authorization header for get document: {str(e)}")
        return jsonify({"success": False, "error": "Invalid authorization header"}), 422
    except JWTError as e: # Catch general JWT errors
        logging.error(f"JWT error for get document: {str(e)}")
        return jsonify({"success": False, "error": f"JWT error: {str(e)}"}), 422
    except Exception as e:
        logging.error(f"Error getting document {doc_id}: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@main.route('/documents/download/<filename>', methods=['GET'])
@jwt_required()
def download_document(filename):
    logging.debug(f"Attempting to download file: {filename}")
    try:
        identity = get_jwt_identity()
        logging.debug(f"JWT identity for downloading document: {identity}")
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except jwt_exceptions.NoAuthorizationError as e:
        logging.error(f"No authorization token provided for download document: {str(e)}")
        return jsonify({"success": False, "error": "Authorization token missing"}), 401
    except jwt_exceptions.InvalidHeaderError as e:
        logging.error(f"Invalid authorization header for download document: {str(e)}")
        return jsonify({"success": False, "error": "Invalid authorization header"}), 422
    except JWTError as e: # Catch general JWT errors
        logging.error(f"JWT error for download document: {str(e)}")
        return jsonify({"success": False, "error": f"JWT error: {str(e)}"}), 422
    except Exception as e:
        logging.error(f"Error downloading file {filename}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error downloading file: {str(e)}"}), 500

@main.route('/documents/view/<filename>', methods=['GET'])
@jwt_required()
def view_document(filename):
    logging.debug(f"Attempting to view file: {filename}")
    try:
        identity = get_jwt_identity()
        logging.debug(f"JWT identity for viewing document: {identity}")
        return send_from_directory(UPLOAD_FOLDER, filename)
    except jwt_exceptions.NoAuthorizationError as e:
        logging.error(f"No authorization token provided for view document: {str(e)}")
        return jsonify({"success": False, "error": "Authorization token missing"}), 401
    except jwt_exceptions.InvalidHeaderError as e:
        logging.error(f"Invalid authorization header for view document: {str(e)}")
        return jsonify({"success": False, "error": "Invalid authorization header"}), 422
    except JWTError as e: # Catch general JWT errors
        logging.error(f"JWT error for view document: {str(e)}")
        return jsonify({"success": False, "error": f"JWT error: {str(e)}"}), 422
    except Exception as e:
        logging.error(f"Error viewing file {filename}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error viewing file: {str(e)}"}), 500

@main.route('/documents/<int:doc_id>', methods=['DELETE'])
@jwt_required()
def delete_document_route(doc_id):
    logging.debug(f"Attempting to delete document with ID: {doc_id}")
    try:
        identity = get_jwt_identity()
        logging.debug(f"JWT identity for deleting document: {identity}")
        file_path_to_delete = delete_document(doc_id) # This returns the file path
        if file_path_to_delete and os.path.exists(file_path_to_delete):
            os.remove(file_path_to_delete)
            logging.info(f"Successfully deleted file {file_path_to_delete} from file system.")
        logging.info(f"Document {doc_id} deleted from database.")
        return jsonify({"success": True, "message": "Document deleted successfully"}), 200
    except jwt_exceptions.NoAuthorizationError as e:
        logging.error(f"No authorization token provided for delete document: {str(e)}")
        return jsonify({"success": False, "error": "Authorization token missing"}), 401
    except jwt_exceptions.InvalidHeaderError as e:
        logging.error(f"Invalid authorization header for delete document: {str(e)}")
        return jsonify({"success": False, "error": "Invalid authorization header"}), 422
    except JWTError as e: # Catch general JWT errors
        logging.error(f"JWT error for delete document: {str(e)}")
        return jsonify({"success": False, "error": f"JWT error: {str(e)}"}), 422
    except Exception as e:
        logging.error(f"Error deleting document {doc_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": f"Error deleting document: {str(e)}"}), 500


@main.route('/register', methods=['POST'])
@handle_errors
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not username or not password:
        logging.warning("Registration attempt with missing username or password.")
        return jsonify({"error": "Username and password are required"}), 400

    hashed_pw = generate_password_hash(password)
    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", (username, hashed_pw, email))
        conn.commit()
        logging.info(f"User {username} registered successfully.")
        return jsonify({"message": "User registered successfully", "username": username, "email": email}), 201
    except sqlite3.IntegrityError:
        logging.warning(f"Registration attempt for existing username: {username}")
        return jsonify({"error": "Username already exists"}), 409
    except Exception as e:
        logging.error(f"Database error during registration: {str(e)}", exc_info=True)
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
        logging.warning("Login attempt with missing username or password.")
        return jsonify({"error": "Username and password are required"}), 400

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Allow login with either username or email
        cursor.execute(
            "SELECT password_hash, email, username FROM users WHERE username = ? OR email = ?",
            (username, username)
        )
        user = cursor.fetchone()
        conn.close()

        logging.debug(f"Login attempt for user: {username}")
        if user:
            stored_password_hash = user[0]
            user_email = user[1]
            user_username = user[2]
            password_match = check_password_hash(stored_password_hash, password)
            if password_match:
                access_token = create_access_token(identity=user_username)
                logging.info(f"User {user_username} logged in successfully.")
                return jsonify(access_token=access_token, username=user_username, email=user_email), 200
            else:
                logging.warning(f"Failed login attempt for username/email: {username} - Incorrect password.")
                return jsonify({"error": "Bad username or password"}), 401
        else:
            logging.warning(f"Failed login attempt: Username or email {username} not found.")
            return jsonify({"error": "Bad username or password"}), 401
    except Exception as e:
        logging.error(f"Database error during login: {str(e)}", exc_info=True)
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@main.route('/process-document/<int:doc_id>', methods=['POST'])
@jwt_required()
def process_document(doc_id):
    try:
        # Get the document
        document = get_document_by_id(doc_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404

        file_path = document['file_path']
        
        # Extract text
        text = extract_text_from_file(file_path)
        if not text:
            return jsonify({'error': 'Could not extract text from file'}), 400

        # Process the document
        summary = generate_summary(text)
        clauses = detect_clauses(text)
        features = legal_domain_processor.process_legal_document(text)
        context_analysis = context_processor.analyze_context(text)

        # Update the document with processed content
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE documents 
        SET full_text = ?, summary = ?, clauses = ?, features = ?, context_analysis = ?
        WHERE id = ?
        ''', (text, summary, str(clauses), str(features), str(context_analysis), doc_id))
        conn.commit()
        conn.close()

        return jsonify({
            'message': 'Document processed successfully',
            'document_id': doc_id,
            'status': 'completed'
        }), 200

    except Exception as e:
        logging.error(f"Error processing document: {str(e)}")
        return jsonify({'error': str(e)}), 500


@main.route('/documents/summary/<int:doc_id>', methods=['POST'])
@jwt_required()
def generate_document_summary(doc_id):
    try:
        doc = get_document_by_id(doc_id)
        if not doc:
            return jsonify({"error": "Document not found"}), 404
        # If summary exists and is not empty, return it
        summary = doc.get('summary', '')
        if summary and summary.strip() and summary != 'Processing...':
            return jsonify({"summary": summary}), 200
        file_path = doc.get('file_path', '')
        if not file_path or not os.path.exists(file_path):
            return jsonify({"error": "File not found for this document"}), 404
        # Extract text from file (PDF, DOC, DOCX)
        text = extract_text_from_file(file_path)
        if not text.strip():
            return jsonify({"error": "No text available for summarization"}), 400
        summary = generate_summary(text)
        # Save the summary to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE documents SET summary = ? WHERE id = ?', (summary, doc_id))
        conn.commit()
        conn.close()
        return jsonify({"summary": summary}), 200
    except Exception as e:
        return jsonify({"error": f"Error generating summary: {str(e)}"}), 500

