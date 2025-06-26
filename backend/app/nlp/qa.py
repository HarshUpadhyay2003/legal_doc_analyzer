from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import logging
from app.utils.cache import cache_qa_result
import torch
from app.utils.enhanced_models import enhanced_model_manager

# Check GPU availability
if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    logging.info(f"GPU detected: {gpu_name} ({gpu_memory:.1f}GB) - Using GPU for QA model")
else:
    logging.warning("No GPU detected - Using CPU for QA model (this will be slower)")

# Initialize model and tokenizer
def get_qa_model():
    try:
        logging.info("Loading QA model and tokenizer...")
        model = AutoModelForSeq2SeqLM.from_pretrained("TheGod-2003/legal_QA_model")
        tokenizer = AutoTokenizer.from_pretrained("TheGod-2003/legal_QA_model", use_fast=False)
        
        # Move model to GPU if available
        if torch.cuda.is_available():
            model = model.to("cuda")
            logging.info("QA model moved to GPU successfully")
        else:
            logging.info("QA model loaded on CPU")
            
        return model, tokenizer
    except Exception as e:
        logging.error(f"Error initializing QA model: {str(e)}")
        raise

# Load legal QA model
try:
    qa_model, qa_tokenizer = get_qa_model()
    device_str = "GPU" if torch.cuda.is_available() else "CPU"
    logging.info(f"QA model loaded successfully on {device_str}")
except Exception as e:
    logging.error(f"Failed to load QA model: {str(e)}")
    qa_model = None
    qa_tokenizer = None

def get_top_n_chunks(question, context, n=3):
    # Split context into chunks, handling both paragraph and sentence-level splits
    chunks = []
    # First split by paragraphs
    paragraphs = context.split('\n\n')
    for para in paragraphs:
        # Then split by sentences if paragraph is too long
        if len(para.split()) > 100:  # If paragraph has more than 100 words
            sentences = para.split('. ')
            chunks.extend(sentences)
        else:
            chunks.append(para)
    
    # Remove empty chunks
    chunks = [chunk for chunk in chunks if chunk.strip()]
    
    # If we have very few chunks, return the whole context
    if len(chunks) <= n:
        return context
    
    # Calculate relevance scores
    vectorizer = TfidfVectorizer().fit(chunks + [question])
    scores = vectorizer.transform([question]) @ vectorizer.transform(chunks).T
    top_indices = np.argsort(scores.toarray()[0])[-n:][::-1]
    
    # Combine top chunks with proper spacing
    return " ".join([chunks[i] for i in top_indices])

@cache_qa_result
def answer_question(question, context):
    result = enhanced_model_manager.answer_question_enhanced(question, context)
    return {
        'answer': result['answer'],
        'score': result.get('confidence', 0.0),
        'start': 0,
        'end': 0
    }
