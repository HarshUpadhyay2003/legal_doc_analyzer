# All sqlite3 and local DB logic will be removed and replaced with SQLAlchemy/Postgres in the next step.
# This file will be refactored to use SQLAlchemy models and sessions.

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
import os
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import re

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
print("DEBUG: DATABASE_URL from os.environ:", os.environ.get('DATABASE_URL'))

# SQLAlchemy setup
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL or DATABASE_URL.strip() == "":
    raise ValueError("DATABASE_URL is not set or is empty. Please set it as an environment variable or in your .env file for NeonDB.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    phone = Column(String)
    company = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    documents = relationship('Document', back_populates='user')
    question_answers = relationship('QuestionAnswer', back_populates='user')

# Document model
class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    full_text = Column(Text)
    summary = Column(Text)
    clauses = Column(Text)
    features = Column(Text)
    context_analysis = Column(Text)
    file_data = Column(LargeBinary)  # Store file content in DB
    file_size = Column(Integer)  # Add this
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='documents')
    question_answers = relationship('QuestionAnswer', back_populates='document')

# QuestionAnswer model
class QuestionAnswer(Base):
    __tablename__ = 'question_answers'
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    document = relationship('Document', back_populates='question_answers')
    user = relationship('User', back_populates='question_answers')

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def get_db_session():
    return SessionLocal()

# --- Document CRUD ---
def save_document(title, full_text, summary, clauses, features, context_analysis, file_data, user_id):
    session = get_db_session()
    try:
        doc = Document(
            title=title,
            full_text=full_text,
            summary=summary,
            clauses=str(clauses),
            features=str(features),
            context_analysis=str(context_analysis),
            file_data=file_data,
            file_size=len(file_data) if file_data else 0,  # Store file size
            user_id=user_id
        )
        session.add(doc)
        session.commit()
        return doc.id
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def get_all_documents(user_id=None):
    session = get_db_session()
    try:
        query = session.query(Document)
        if user_id is not None:
            query = query.filter(Document.user_id == user_id)
        documents = query.order_by(Document.upload_time.desc()).all()
        result = []
        for doc in documents:
            d = doc.__dict__.copy()
            d.pop('_sa_instance_state', None)
            d.pop('file_data', None)  # Don't return file data in list
            # Do NOT pop 'summary'; keep it in the result
            # file_size is included
            result.append(d)
        return result
    finally:
        session.close()

def get_document_by_id(doc_id, user_id=None):
    session = get_db_session()
    try:
        query = session.query(Document).filter(Document.id == doc_id)
        if user_id is not None:
            query = query.filter(Document.user_id == user_id)
        doc = query.first()
        if doc:
            d = doc.__dict__.copy()
            d.pop('_sa_instance_state', None)
            # Don't return file_data by default
            d.pop('file_data', None)
            return d
        return None
    finally:
        session.close()

def delete_document(doc_id):
    session = get_db_session()
    try:
        doc = session.query(Document).filter(Document.id == doc_id).first()
        if doc:
            session.delete(doc)
            session.commit()
        return True
    finally:
        session.close()

def search_documents(query, search_type='all'):
    session = get_db_session()
    try:
        results = []
        if query.isdigit():
            docs = session.query(Document).filter(Document.id == int(query)).all()
        else:
            docs = session.query(Document).filter(Document.title.ilike(f'%{query}%')).order_by(Document.id.desc()).all()
        for doc in docs:
            results.append({
                "id": doc.id,
                "title": doc.title,
                "summary": doc.summary or "",
                "upload_time": doc.upload_time,
                "match_score": 1.0
            })
        return results
    finally:
        session.close()

# --- Q&A ---
def search_questions_answers(query, user_id=None):
    session = get_db_session()
    try:
        q = session.query(QuestionAnswer)
        if user_id is not None:
            q = q.filter(QuestionAnswer.user_id == user_id)
        q = q.filter((QuestionAnswer.question.ilike(f'%{query}%')) | (QuestionAnswer.answer.ilike(f'%{query}%')))
        q = q.order_by(QuestionAnswer.created_at.desc())
        results = []
        for row in q.all():
            results.append({
                'id': row.id,
                'document_id': row.document_id,
                'question': row.question,
                'answer': row.answer,
                'created_at': row.created_at.isoformat() if row.created_at else None,
            })
        return results
    finally:
        session.close()

def clean_answer(answer):
    # Remove patterns like (3), extra spaces, and leading/trailing punctuation
    answer = re.sub(r'\(\d+\)', '', answer)
    answer = re.sub(r'\s+', ' ', answer)
    answer = answer.strip(' ,.;:')
    return answer

def save_question_answer(document_id, user_id, question, answer, score):
    score = float(score)  # Convert np.float64 to Python float
    answer = clean_answer(answer)  # Clean up answer format
    session = get_db_session()
    try:
        qa = QuestionAnswer(
            document_id=document_id,
            user_id=user_id,
            question=question,
            answer=answer,
            score=score
        )
        session.add(qa)
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

# --- User Profile ---
def get_user_profile(username):
    session = get_db_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        if user:
            return {
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'company': user.company
            }
        return None
    finally:
        session.close()

def update_user_profile(username, email, phone, company):
    session = get_db_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        if user:
            user.email = email
            user.phone = phone
            user.company = company
            session.commit()
            return True
        return False
    finally:
        session.close()

def change_user_password(username, current_password, new_password):
    session = get_db_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return False, 'User not found'
        if not check_password_hash(user.password_hash, current_password):
            return False, 'Current password is incorrect'
        user.password_hash = generate_password_hash(new_password)
        session.commit()
        return True, 'Password updated successfully'
    finally:
        session.close()
