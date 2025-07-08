import os
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
from app.utils.extract_text import extract_text_from_pdf
from app.utils.summarizer import generate_summary
from app.utils.clause_detector import detect_clauses
from app.database import save_document, delete_document
from app.database import get_all_documents, get_document_by_id
from app.database import search_documents, save_question_answer, search_questions_answers
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
from app.database import get_user_profile, update_user_profile, change_user_password
from app.database import SessionLocal, User
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

main = Blueprint("main", __name__)

# Initialize the processors
enhanced_legal_processor = EnhancedLegalProcessor()
legal_domain_processor = LegalDomainFeatures()
context_processor = ContextUnderstanding()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
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

def get_user_id_by_username(username):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == username).first()
        return user.id if user else None
    finally:
        session.close()

@main.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if not (file.filename.lower().endswith('.pdf')):
            return jsonify({'error': 'File type not allowed. Only PDF files are supported.'}), 400
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        identity = get_jwt_identity()
        user_id = get_user_id_by_username(identity)
        if not user_id:
            return jsonify({"success": False, "error": "User not found"}), 401
        doc_id = save_document(
            title=filename,
            full_text="",
            summary="Processing...",
            clauses="[]",
            features="{}",
            context_analysis="{}",
            file_path=file_path,
            user_id=user_id
        )
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
    try:
        docs = get_all_documents()
        return jsonify(docs), 200
    except Exception as e:
        logging.error(f"Error listing documents: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@main.route('/get_document/<int:doc_id>', methods=['GET'])
@jwt_required()
def get_document(doc_id):
    try:
        doc = get_document_by_id(doc_id)
        if doc:
            return jsonify(doc), 200
        else:
            return jsonify({"error": "Document not found"}), 404
    except Exception as e:
        logging.error(f"Error getting document {doc_id}: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@main.route('/documents/download/<filename>', methods=['GET'])
@jwt_required()
def download_document(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error downloading file {filename}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error downloading file: {str(e)}"}), 500

@main.route('/documents/view/<filename>', methods=['GET'])
@jwt_required()
def view_document(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        logging.error(f"Error viewing file {filename}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error viewing file: {str(e)}"}), 500

@main.route('/documents/<int:doc_id>', methods=['DELETE'])
@jwt_required()
def delete_document_route(doc_id):
    try:
        file_path_to_delete = delete_document(doc_id)
        if file_path_to_delete and os.path.exists(file_path_to_delete):
            os.remove(file_path_to_delete)
        return jsonify({"success": True, "message": "Document deleted successfully"}), 200
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
    session = SessionLocal()
    try:
        user = User(username=username, password_hash=hashed_pw, email=email)
        session.add(user)
        session.commit()
        return jsonify({"message": "User registered successfully", "username": username, "email": email}), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"error": "Username already exists"}), 409
    except Exception as e:
        session.rollback()
        logging.error(f"Database error during registration: {str(e)}", exc_info=True)
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        session.close()

@main.route('/login', methods=['POST'])
@handle_errors
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        logging.warning("Login attempt with missing username or password.")
        return jsonify({"error": "Username and password are required"}), 400
    session = SessionLocal()
    try:
        user = session.query(User).filter(or_(User.username == username, User.email == username)).first()
        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.username)
            return jsonify(access_token=access_token, username=user.username, email=user.email), 200
        else:
            return jsonify({"error": "Bad username or password"}), 401
    except Exception as e:
        logging.error(f"Database error during login: {str(e)}", exc_info=True)
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        session.close()

@main.route('/process-document/<int:doc_id>', methods=['POST'])
@jwt_required()
def process_document(doc_id):
    try:
        document = get_document_by_id(doc_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        file_path = document['file_path']
        text = extract_text_from_file(file_path)
        if not text:
            return jsonify({'error': 'Could not extract text from file'}), 400
        summary = generate_summary(text)
        clauses = detect_clauses(text)
        features = legal_domain_processor.process_legal_document(text)
        context_analysis = context_processor.analyze_context(text)
        # Update the document with processed content
        session = SessionLocal()
        try:
            doc = session.query(User).get(doc_id)
            if doc:
                doc.full_text = text
                doc.summary = summary
                doc.clauses = str(clauses)
                doc.features = str(features)
                doc.context_analysis = str(context_analysis)
                session.commit()
        finally:
            session.close()
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
        summary = doc.get('summary', '')
        if summary and summary.strip() and summary != 'Processing...':
            return jsonify({"summary": summary}), 200
        file_path = doc.get('file_path', '')
        if not file_path or not os.path.exists(file_path):
            return jsonify({"error": "File not found for this document"}), 404
        text = extract_text_from_file(file_path)
        if not text.strip():
            return jsonify({"error": "No text available for summarization"}), 400
        summary = generate_summary(text)
        # Save the summary to the database
        session = SessionLocal()
        try:
            document = session.query(User).get(doc_id)
            if document:
                document.summary = summary
                session.commit()
        finally:
            session.close()
        return jsonify({"summary": summary}), 200
    except Exception as e:
        return jsonify({"error": f"Error generating summary: {str(e)}"}), 500

@main.route('/ask-question', methods=['POST', 'OPTIONS'])
def ask_question():
    if request.method == 'OPTIONS':
        return '', 204
    return _ask_question_impl()

@jwt_required()
def _ask_question_impl():
    data = request.get_json()
    document_id = data.get('document_id')
    question = data.get('question', '').strip()
    if not document_id or not question:
        return jsonify({"success": False, "error": "document_id and question are required"}), 400
    if not question:
        return jsonify({"success": False, "error": "Question cannot be empty"}), 400
    identity = get_jwt_identity()
    user_id = get_user_id_by_username(identity)
    doc = get_document_by_id(document_id, user_id=user_id)
    if not doc:
        return jsonify({"success": False, "error": "Document not found or not owned by user"}), 404
    summary = doc.get('summary', '')
    if not summary or not summary.strip():
        return jsonify({"success": False, "error": "Summary not available for this document"}), 400
    try:
        result = answer_question(question, summary)
        save_question_answer(document_id, user_id, question, result.get('answer', ''), result.get('score', 0.0))
        return jsonify({"success": True, "answer": result.get('answer', ''), "score": result.get('score', 0.0)}), 200
    except Exception as e:
        logging.error(f"Error answering question: {str(e)}")
        return jsonify({"success": False, "error": f"Error answering question: {str(e)}"}), 500

@main.route('/previous-questions/<int:doc_id>', methods=['GET'])
@jwt_required()
def get_previous_questions(doc_id):
    try:
        identity = get_jwt_identity()
        user_id = get_user_id_by_username(identity)
        doc = get_document_by_id(doc_id, user_id=user_id)
        if not doc:
            return jsonify({"success": False, "error": "Document not found or not owned by user"}), 404
        qa_results = search_questions_answers('', user_id=user_id)
        questions = [q for q in qa_results if q['document_id'] == doc_id]
        return jsonify({"success": True, "questions": questions}), 200
    except Exception as e:
        logging.error(f"Error fetching previous questions: {str(e)}")
        return jsonify({"success": False, "error": f"Error fetching previous questions: {str(e)}"}), 500

@main.route('/search', methods=['GET'])
@jwt_required()
def search_all():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Query parameter "q" is required.'}), 400
        identity = get_jwt_identity()
        user_id = get_user_id_by_username(identity)
        doc_results = search_documents(query)
        qa_results = search_questions_answers(query, user_id=user_id)
        return jsonify({
            'documents': doc_results,
            'qa': qa_results
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error during search: {str(e)}'}), 500

@main.route('/user/profile', methods=['GET'])
@jwt_required()
def get_profile():
    identity = get_jwt_identity()
    profile = get_user_profile(identity)
    if profile:
        return jsonify(profile), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@main.route('/user/profile', methods=['POST'])
@jwt_required()
def update_profile():
    identity = get_jwt_identity()
    data = request.get_json()
    email = data.get('email')
    phone = data.get('phone')
    company = data.get('company')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    updated = update_user_profile(identity, email, phone, company)
    if updated:
        return jsonify({'message': 'Profile updated successfully'}), 200
    else:
        return jsonify({'error': 'Failed to update profile'}), 400

@main.route('/user/change-password', methods=['POST'])
@jwt_required()
def change_password():
    identity = get_jwt_identity()
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    if not current_password or not new_password or not confirm_password:
        return jsonify({'error': 'All password fields are required'}), 400
    if new_password != confirm_password:
        return jsonify({'error': 'New passwords do not match'}), 400
    success, msg = change_user_password(identity, current_password, new_password)
    if success:
        return jsonify({'message': msg}), 200
    else:
        return jsonify({'error': msg}), 400

@main.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    try:
        identity = get_jwt_identity()
        user_id = get_user_id_by_username(identity)
        documents = get_all_documents(user_id=user_id)
        total_documents = len(documents)
        processed_documents = sum(1 for doc in documents if doc.get('summary') and doc.get('summary') != 'Processing...')
        pending_analysis = total_documents - processed_documents
        qa_results = search_questions_answers('', user_id=user_id)
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        last_30_days = now - timedelta(days=30)
        recent_questions = sum(1 for q in qa_results if q['created_at'] and q['created_at'] >= last_30_days)
        return jsonify({
            'total_documents': total_documents,
            'processed_documents': processed_documents,
            'pending_analysis': pending_analysis,
            'recent_questions': recent_questions
        }), 200
    except Exception as e:
        logging.error(f"Error fetching dashboard stats: {str(e)}")
        return jsonify({'error': f'Error fetching dashboard stats: {str(e)}'}), 500

