from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import logging
from app.utils.cache import cache_qa_result

# Initialize model and tokenizer
def get_qa_model():
    try:
        model = AutoModelForSeq2SeqLM.from_pretrained("TheGod-2003/legal_QA_model")
        tokenizer = AutoTokenizer.from_pretrained("TheGod-2003/legal_QA_model", use_fast=False)
        return model, tokenizer
    except Exception as e:
        logging.error(f"Error initializing QA model: {str(e)}")
        raise

# Load legal QA model
try:
    qa_model, qa_tokenizer = get_qa_model()
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
    try:
        if qa_model is None or qa_tokenizer is None:
            raise Exception("QA model not initialized")

        # Handle empty or very short context
        if not context or len(context.strip()) < 10:
            return {
                "answer": "The provided context is too short to generate a meaningful answer.",
                "score": 0.0,
                "start": 0,
                "end": 0
            }
        
        # Get relevant chunks based on context length
        context_length = len(context.split())
        n_chunks = min(3, max(1, context_length // 100))  # Adjust chunks based on context length
        top_chunks = get_top_n_chunks(question, context, n=n_chunks)
        
        # Format input for T5 model
        input_text = f"question: {question} context: {top_chunks}"
        
        # Generate answer
        inputs = qa_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        outputs = qa_model.generate(
            **inputs,
            max_length=128,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True
        )
        
        answer = qa_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Since T5 doesn't provide confidence scores, we'll use a default high score
        # for answers that are not empty
        score = 0.9 if answer.strip() else 0.0
        
        return {
            "answer": answer,
            "score": score,
            "start": 0,  # T5 doesn't provide these
            "end": 0     # T5 doesn't provide these
        }
        
    except Exception as e:
        logging.error(f"Error in answer_question: {str(e)}")
        raise  # Re-raise the exception to be handled by the route
