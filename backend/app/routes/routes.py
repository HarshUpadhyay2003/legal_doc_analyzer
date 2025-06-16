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
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.error_handler import handle_errors
from app.utils.enhanced_legal_processor import EnhancedLegalProcessor
from app.utils.legal_domain_features import LegalDomainFeatures
from app.utils.context_understanding import ContextUnderstanding
import logging

main = Blueprint("main", __name__)

# Initialize the processors
enhanced_legal_processor = EnhancedLegalProcessor()
legal_domain_processor = LegalDomainFeatures()
context_processor = ContextUnderstanding()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(BASE_DIR, 'legal_docs.db')


@main.route('/upload', methods=['POST'])
@jwt_required()
@handle_errors
def upload_file():
    # Check if file is in the request
    if 'file' not in request.files:
        return jsonify({
            "success": False,
            "error": "No file part in the request"
        }), 400
    
    file = request.files['file']
    
    # Check if file is empty
    if file.filename == '':
        return jsonify({
            "success": False,
            "error": "No file selected"
        }), 400
    
    # Check if file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({
            "success": False,
            "error": "Only PDF files are allowed"
        }), 400

    try:
        # Extract text from PDF
        text = extract_text_from_pdf(file)
        
        if not text.strip():
            return jsonify({
                "success": False,
                "error": "No text could be extracted from the PDF"
            }), 400

        # Process document using enhanced legal processor
        processed = enhanced_legal_processor.process_document(text)
        
        # Extract legal domain features
        features = legal_domain_processor.process_legal_document(text)
        
        # Analyze context
        context_analysis = context_processor.analyze_context(text)
        
        # Generate summary
        summary = generate_summary(text)
        
        # Detect clauses
        clauses = detect_clauses(text)

        # Save document with all processed information
        doc_id = save_document(
            title=file.filename,
            full_text=text,
            summary=summary,
            clauses=clauses,
            features=features,
            context_analysis=context_analysis
        )

        return jsonify({
            "success": True,
            "document_id": doc_id,
            "filename": file.filename,
            "summary": summary,
            "clauses": clauses,
            "features": features,
            "context_analysis": context_analysis
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error processing file: {str(e)}"
        }), 500


@main.route('/documents', methods=['GET'])
@jwt_required()
@handle_errors
def list_documents():
    try:
        docs = get_all_documents()
        return jsonify(docs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/get_document/<int:doc_id>', methods=['GET'])
@jwt_required()
@handle_errors
def get_document(doc_id):
    doc = get_document_by_id(doc_id)
    if doc:
        return jsonify(doc), 200
    else:
        return jsonify({"error": "Document not found"}), 404


@main.route('/search_documents', methods=['GET'])
@jwt_required()
@handle_errors
def search():
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({
            "error": "Query parameter 'q' is required",
            "status": "error"
        }), 400
    
    try:
        results = search_documents(query)
        return jsonify({
            "status": "success",
            "query": query,
            "results": results,
            "total_results": len(results)
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500


@main.route('/qa', methods=['POST'])
@jwt_required()
@handle_errors
def question_answering():
    data = request.get_json()
    doc_id = data.get("document_id")
    question = data.get("question")

    if not doc_id or not question:
        return jsonify({
            "success": False,
            "error": "Both 'document_id' and 'question' are required"
        }), 400

    document = get_document_by_id(doc_id)
    if not document:
        return jsonify({
            "success": False,
            "error": "Document not found"
        }), 404

    context = document.get("full_text", "")
    if not context:
        return jsonify({
            "success": False,
            "error": "Document has no text content"
        }), 400

    try:
        # Get answer with validation
        answer = answer_question(question, context)
        
        # Validate answer
        if not answer or not answer.get("answer"):
            return jsonify({
                "success": False,
                "error": "Could not generate a valid answer",
                "details": "The model was unable to generate a meaningful response"
            }), 400

        return jsonify({
            "success": True,
            "answer": answer["answer"],
            "confidence": answer["score"],
            "document_id": doc_id,
            "question": question
        }), 200
    except Exception as e:
        logging.error(f"QA error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to process question",
            "details": str(e)
        }), 500


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
    

@main.route('/process_document', methods=['POST'])
@handle_errors
def process_document():
    data = request.get_json()
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "Text is required"}), 400
    
    try:
        # Process document using enhanced legal processor
        processed = enhanced_legal_processor.process_document(text)
        
        # Extract legal domain features
        features = legal_domain_processor.process_legal_document(text)
        
        # Analyze context
        context_analysis = context_processor.analyze_context(text)
        
        return jsonify({
            "processed": processed,
            "features": features,
            "context_analysis": context_analysis
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/validate_answer', methods=['POST'])
@handle_errors
def validate_answer():
    data = request.get_json()
    answer = data.get("answer")
    question = data.get("question")
    context = data.get("context")

    if not all([answer, question, context]):
        return jsonify({
            "status": "error",
            "error": "Missing required fields: answer, question, and context are required"
        }), 400

    try:
        validation = answer_validator.validate_answer(answer, question, context)
        # Convert numpy float32 to Python float
        if 'confidence' in validation:
            validation['confidence'] = float(validation['confidence'])
        return jsonify({
            "status": "success",
            "validation": validation
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": "Validation failed",
            "details": str(e)
        }), 500

@main.route('/evaluate_model', methods=['POST'])
@handle_errors
def evaluate_model():
    data = request.get_json()
    test_data = data.get("test_data", [])
    
    if not test_data:
        return jsonify({"error": "Test data is required"}), 400
    
    try:
        metrics = model_evaluator.evaluate_model(answer_question, test_data, k_folds=2)
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/track_model_version', methods=['POST'])
@handle_errors
def track_model_version():
    data = request.get_json()
    version_name = data.get("version_name")
    metrics = data.get("metrics")
    
    if not all([version_name, metrics]):
        return jsonify({"error": "Version name and metrics are required"}), 400
    
    try:
        model_version_tracker.save_model_version(answer_question, version_name, metrics)
        return jsonify({"message": "Model version saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

