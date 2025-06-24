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


@main.route('/upload', methods=['POST'])
@jwt_required()
@handle_errors
def upload_file():
    # Check if file is in the request
    if 'file' not in request.files:
        return jsonify({
            "success": False,
            "error": "No file part"
        }), 400
    
    file = request.files['file']
    
    # Check if file is empty
    if file.filename == '':
        return jsonify({
            "success": False,
            "error": "No file selected"
        }), 400
    
    # Check if file is a PDF
    if not file.filename.lower().endswith( ('.pdf', '.doc', '.docx') ):
        return jsonify({
            "success": False,
            "error": "Only PDF, DOC, and DOCX files are allowed"
        }), 400

    try:
        # Securely save the file to the upload folder
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Extract text from PDF (or DOC/DOCX - placeholder for now)
        if filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        else:
            # Placeholder for DOC/DOCX text extraction
            text = "" # You'll need to implement actual extraction for DOC/DOCX
            logging.warning(f"DOC/DOCX text extraction not implemented for {filename}")
        
        if not text.strip():
            # If no text extracted, still save the document reference
            text = "[No text extracted]"

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
            title=filename,
            full_text=text,
            summary=summary,
            clauses=clauses,
            features=features,
            context_analysis=context_analysis,
            file_path=file_path # Save the file path
        )

        return jsonify({
            "success": True,
            "document_id": doc_id,
            "filename": filename,
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


@main.route('/documents/download/<filename>', methods=['GET'])
@jwt_required()
@handle_errors
def download_document(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"Error downloading file: {str(e)}"}), 500

@main.route('/documents/view/<filename>', methods=['GET'])
@jwt_required()
@handle_errors
def view_document(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        return jsonify({"error": f"Error viewing file: {str(e)}"}), 500

@main.route('/documents/<int:doc_id>', methods=['DELETE'])
@jwt_required()
@handle_errors
def delete_document_route(doc_id):
    try:
        file_path_to_delete = delete_document(doc_id) # This returns the file path
        if file_path_to_delete and os.path.exists(file_path_to_delete):
            os.remove(file_path_to_delete)
        return jsonify({"success": True, "message": "Document deleted successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Error deleting document: {str(e)}"}), 500

@main.route('/documents/summary/<int:doc_id>', methods=['POST'])
@jwt_required()
@handle_errors
def generate_document_summary(doc_id):
    doc = get_document_by_id(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    text = doc.get('full_text', '')
    if not text.strip():
        return jsonify({"error": "No text available for summarization"}), 400
    try:
        summary = generate_summary(text)
        return jsonify({"summary": summary}), 200
    except Exception as e:
        return jsonify({"error": f"Error generating summary: {str(e)}"}), 500 