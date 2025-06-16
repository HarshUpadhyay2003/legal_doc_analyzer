import pytest
import json
import os
import sys
import tempfile
import shutil
from fpdf import FPDF
import uuid

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.database import init_db

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'JWT_SECRET_KEY': 'test-secret-key',
        'DATABASE': ':memory:'
    })
    with app.app_context():
        init_db()
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Register a test user with unique username
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    register_response = client.post('/register', json={
        'username': unique_username,
        'password': 'testpass'
    })
    assert register_response.status_code == 201, "User registration failed"

    # Login to get token
    login_response = client.post('/login', json={
        'username': unique_username,
        'password': 'testpass'
    })
    assert login_response.status_code == 200, "Login failed"
    assert 'access_token' in login_response.json, "No access token in response"
    
    token = login_response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

def create_test_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add more content to make it a realistic document
    pdf.cell(200, 10, txt="Legal Document Analysis", ln=1, align="C")
    pdf.cell(200, 10, txt="This is a test document for legal processing.", ln=1, align="C")
    pdf.cell(200, 10, txt="Section 1: Introduction", ln=1, align="L")
    pdf.cell(200, 10, txt="This document contains various legal clauses and provisions.", ln=1, align="L")
    pdf.cell(200, 10, txt="Section 2: Main Provisions", ln=1, align="L")
    pdf.cell(200, 10, txt="The main provisions of this agreement include confidentiality clauses,", ln=1, align="L")
    pdf.cell(200, 10, txt="intellectual property rights, and dispute resolution mechanisms.", ln=1, align="L")
    pdf.cell(200, 10, txt="Section 3: Conclusion", ln=1, align="L")
    pdf.cell(200, 10, txt="This document serves as a comprehensive legal agreement.", ln=1, align="L")
    
    pdf.output("test.pdf")
    return "test.pdf"

# Authentication Tests
def test_register_success(client):
    unique_username = f"newuser_{uuid.uuid4().hex[:8]}"
    response = client.post('/register', json={
        'username': unique_username,
        'password': 'newpass'
    })
    assert response.status_code == 201
    assert response.json['message'] == "User registered successfully"

def test_register_duplicate_username(client):
    # First registration
    username = f"duplicate_{uuid.uuid4().hex[:8]}"
    client.post('/register', json={
        'username': username,
        'password': 'pass1'
    })
    # Second registration with same username
    response = client.post('/register', json={
        'username': username,
        'password': 'pass2'
    })
    assert response.status_code == 409
    assert 'error' in response.json

def test_login_success(client):
    # Register first
    username = f"loginuser_{uuid.uuid4().hex[:8]}"
    client.post('/register', json={
        'username': username,
        'password': 'loginpass'
    })
    # Then login
    response = client.post('/login', json={
        'username': username,
        'password': 'loginpass'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_invalid_credentials(client):
    response = client.post('/login', json={
        'username': 'nonexistent',
        'password': 'wrongpass'
    })
    assert response.status_code == 401
    assert 'error' in response.json

# Document Upload Tests
def test_upload_success(client, auth_headers):
    pdf_path = create_test_pdf()
    try:
        with open(pdf_path, 'rb') as f:
            response = client.post('/upload',
                data={'file': (f, 'test.pdf')},
                headers=auth_headers,
                content_type='multipart/form-data'
            )
        assert response.status_code == 200
        assert response.json['success'] == True
        assert 'document_id' in response.json
    finally:
        os.unlink(pdf_path)

def test_upload_no_file(client, auth_headers):
    response = client.post('/upload', headers=auth_headers)
    assert response.status_code == 400
    assert 'error' in response.json

def test_upload_unauthorized(client):
    response = client.post('/upload')
    assert response.status_code == 401

# Document Retrieval Tests
def test_list_documents_success(client, auth_headers):
    response = client.get('/documents', headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_list_documents_unauthorized(client):
    response = client.get('/documents')
    assert response.status_code == 401

def test_get_document_success(client, auth_headers):
    # First upload a document
    pdf_path = create_test_pdf()
    try:
        with open(pdf_path, 'rb') as f:
            upload_response = client.post('/upload',
                data={'file': (f, 'test.pdf')},
                headers=auth_headers,
                content_type='multipart/form-data'
            )
        doc_id = upload_response.json['document_id']
        
        # Then retrieve it
        response = client.get(f'/get_document/{doc_id}', headers=auth_headers)
        assert response.status_code == 200
        assert response.json['id'] == doc_id
    finally:
        os.unlink(pdf_path)

def test_get_document_not_found(client, auth_headers):
    response = client.get('/get_document/99999', headers=auth_headers)
    assert response.status_code == 404

# Search Tests
def test_search_success(client, auth_headers):
    response = client.get('/search_documents?q=test', headers=auth_headers)
    assert response.status_code == 200
    assert 'results' in response.json

def test_search_no_query(client, auth_headers):
    response = client.get('/search_documents', headers=auth_headers)
    assert response.status_code == 400

# QA Tests
def test_qa_success(client, auth_headers):
    # First upload a document
    pdf_path = create_test_pdf()
    try:
        with open(pdf_path, 'rb') as f:
            upload_response = client.post('/upload',
                data={'file': (f, 'test.pdf')},
                headers=auth_headers,
                content_type='multipart/form-data'
            )
        doc_id = upload_response.json['document_id']
        
        # Then ask a question
        response = client.post('/qa',
            json={
                'document_id': doc_id,
                'question': 'What is this document about?'
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert 'answer' in response.json
    finally:
        os.unlink(pdf_path)

def test_qa_missing_fields(client, auth_headers):
    response = client.post('/qa',
        json={'document_id': 1},
        headers=auth_headers
    )
    assert response.status_code == 400

# Document Processing Tests
def test_process_document_success(client):
    response = client.post('/process_document',
        json={'text': 'Test legal document content'}
    )
    assert response.status_code == 200
    assert 'processed' in response.json
    assert 'features' in response.json
    assert 'context_analysis' in response.json

def test_process_document_empty_text(client):
    response = client.post('/process_document',
        json={'text': ''}
    )
    assert response.status_code == 400