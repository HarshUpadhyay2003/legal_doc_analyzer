from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Load legal QA model
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

def get_top_n_chunks(question, context, n=3):
    chunks = context.split('\n\n')
    vectorizer = TfidfVectorizer().fit(chunks + [question])
    scores = vectorizer.transform([question]) @ vectorizer.transform(chunks).T
    top_indices = np.argsort(scores.toarray()[0])[-n:][::-1]
    return " ".join([chunks[i] for i in top_indices])

def answer_question(question, context):
    top_chunks = get_top_n_chunks(question, context)
    result = qa_pipeline(question=question, context=top_chunks)
    if result['score'] < 0.3:
        return {"answer": "Not confident enough to answer", "score": round(result['score'], 3)}
    else:
        return {
            "answer": result['answer'],
            "score": round(result['score'], 3),
            "start": result['start'],
            "end": result['end']
        }
