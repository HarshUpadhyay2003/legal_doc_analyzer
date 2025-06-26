import torch
import logging
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForQuestionAnswering
from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Dict, Any, Optional
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os

class EnhancedModelManager:
    """
    Enhanced model manager with ensemble methods, better prompting, and multiple models
    for improved accuracy in legal document analysis.
    """
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models = {}
        self.embedders = {}
        self.initialize_models()
        
    def initialize_models(self):
        """Initialize multiple models for ensemble approach"""
        try:
            # === Summarization Models ===
            logging.info("Loading summarization models...")
            # Only the legal-specific summarizer
            self.models['legal_summarizer'] = pipeline(
                "summarization",
                model="TheGod-2003/legal-summarizer",
                tokenizer="TheGod-2003/legal-summarizer",
                device=0 if self.device == "cuda" else -1
            )
            logging.info("Legal summarization model loaded successfully")
            
            # === QA Models ===
            logging.info("Loading QA models...")
            
            # Primary legal QA model
            self.models['legal_qa'] = pipeline(
                "question-answering",
                model="TheGod-2003/legal_QA_model",
                tokenizer="TheGod-2003/legal_QA_model",
                device=0 if self.device == "cuda" else -1
            )
            
            # Alternative QA models
            try:
                self.models['bert_qa'] = pipeline(
                    "question-answering",
                    model="deepset/roberta-base-squad2",
                    device=0 if self.device == "cuda" else -1
                )
            except Exception as e:
                logging.warning(f"Could not load RoBERTa QA model: {e}")
            
            try:
                self.models['distilbert_qa'] = pipeline(
                    "question-answering",
                    model="distilbert-base-cased-distilled-squad",
                    device=0 if self.device == "cuda" else -1
                )
            except Exception as e:
                logging.warning(f"Could not load DistilBERT QA model: {e}")
            
            # === Embedding Models ===
            logging.info("Loading embedding models...")
            
            # Primary embedding model
            self.embedders['mpnet'] = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
            
            # Alternative embedding models for ensemble
            try:
                self.embedders['all_minilm'] = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            except Exception as e:
                logging.warning(f"Could not load all-MiniLM embedder: {e}")
            
            try:
                self.embedders['paraphrase'] = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            except Exception as e:
                logging.warning(f"Could not load paraphrase embedder: {e}")
            
            logging.info("All models loaded successfully")
            
        except Exception as e:
            logging.error(f"Error initializing models: {e}")
            raise
    
    def generate_enhanced_summary(self, text: str, max_length: int = 2048, min_length: int = 200) -> Dict[str, Any]:
        """
        Generate enhanced summary using ensemble approach with multiple models
        """
        try:
            summaries = []
            weights = []
            cleaned_text = self._preprocess_text(text)
            # Only legal summarizer
            if 'legal_summarizer' in self.models:
                try:
                    summary = self.models['legal_summarizer'](
                        cleaned_text,
                        max_length=max_length,
                        min_length=min_length,
                        num_beams=4,
                        length_penalty=1.0,
                        repetition_penalty=2.0,
                        no_repeat_ngram_size=3,
                        early_stopping=True
                    )[0]['summary_text']
                    summaries.append(summary)
                    weights.append(1.0)
                except Exception as e:
                    logging.warning(f"Legal summarizer failed: {e}")
            if not summaries:
                raise Exception("No models could generate summaries")
            final_summary = self._ensemble_summaries(summaries, weights)
            final_summary = self._postprocess_summary(final_summary, summaries, min_sentences=10)
            return {
                'summary': final_summary,
                'model_summaries': summaries,
                'weights': weights,
                'confidence': self._calculate_summary_confidence(final_summary, cleaned_text)
            }
        except Exception as e:
            logging.error(f"Error in enhanced summary generation: {e}")
            raise
    
    def answer_question_enhanced(self, question: str, context: str) -> Dict[str, Any]:
        """
        Enhanced QA with ensemble approach and better context retrieval
        """
        try:
            # Enhanced context retrieval
            enhanced_context = self._enhance_context(question, context)
            
            answers = []
            scores = []
            weights = []
            
            # Generate answers with different models
            if 'legal_qa' in self.models:
                try:
                    result = self.models['legal_qa'](
                        question=question,
                        context=enhanced_context
                    )
                    answers.append(result['answer'])
                    scores.append(result['score'])
                    weights.append(0.5)  # Higher weight for legal-specific model
                except Exception as e:
                    logging.warning(f"Legal QA model failed: {e}")
            
            if 'bert_qa' in self.models:
                try:
                    result = self.models['bert_qa'](
                        question=question,
                        context=enhanced_context
                    )
                    answers.append(result['answer'])
                    scores.append(result['score'])
                    weights.append(0.3)
                except Exception as e:
                    logging.warning(f"RoBERTa QA model failed: {e}")
            
            if 'distilbert_qa' in self.models:
                try:
                    result = self.models['distilbert_qa'](
                        question=question,
                        context=enhanced_context
                    )
                    answers.append(result['answer'])
                    scores.append(result['score'])
                    weights.append(0.2)
                except Exception as e:
                    logging.warning(f"DistilBERT QA model failed: {e}")
            
            if not answers:
                raise Exception("No models could generate answers")
            
            # Ensemble the answers
            final_answer = self._ensemble_answers(answers, scores, weights)
            
            # Validate and enhance the answer
            enhanced_answer = self._enhance_answer(final_answer, question, enhanced_context)
            
            return {
                'answer': enhanced_answer,
                'confidence': np.average(scores, weights=weights),
                'model_answers': answers,
                'model_scores': scores,
                'context_used': enhanced_context
            }
            
        except Exception as e:
            logging.error(f"Error in enhanced QA: {e}")
            raise
    
    def _enhance_context(self, question: str, context: str) -> str:
        """Enhanced context retrieval using multiple embedding models"""
        try:
            # Split context into sentences
            sentences = self._split_into_sentences(context)
            
            if len(sentences) <= 3:
                return context
            
            # Get embeddings from multiple models
            embeddings = {}
            for name, embedder in self.embedders.items():
                try:
                    sentence_embeddings = embedder.encode(sentences, convert_to_tensor=True)
                    question_embedding = embedder.encode(question, convert_to_tensor=True)
                    similarities = util.cos_sim(question_embedding, sentence_embeddings)[0]
                    embeddings[name] = similarities.cpu().numpy()
                except Exception as e:
                    logging.warning(f"Embedding model {name} failed: {e}")
            
            if not embeddings:
                return context
            
            # Ensemble similarities
            ensemble_similarities = np.mean(list(embeddings.values()), axis=0)
            
            # Get top sentences
            top_indices = np.argsort(ensemble_similarities)[-5:][::-1]  # Top 5 sentences
            
            # Combine with semantic ordering
            relevant_sentences = [sentences[i] for i in sorted(top_indices)]
            
            return " ".join(relevant_sentences)
            
        except Exception as e:
            logging.warning(f"Context enhancement failed: {e}")
            return context
    
    def _ensemble_summaries(self, summaries: List[str], weights: List[float]) -> str:
        """Ensemble multiple summaries using semantic similarity"""
        try:
            if len(summaries) == 1:
                return summaries[0]
            
            # Normalize weights
            weights = np.array(weights) / np.sum(weights)
            
            # Use the primary model's summary as base
            base_summary = summaries[0]
            
            # For now, return the weighted combination of summaries
            # In a more sophisticated approach, you could use extractive methods
            # to combine the best parts of each summary
            
            return base_summary
            
        except Exception as e:
            logging.warning(f"Summary ensemble failed: {e}")
            return summaries[0] if summaries else ""
    
    def _ensemble_answers(self, answers: List[str], scores: List[float], weights: List[float]) -> str:
        """Ensemble multiple answers using confidence scores"""
        try:
            if len(answers) == 1:
                return answers[0]
            
            # Normalize weights
            weights = np.array(weights) / np.sum(weights)
            
            # Weighted voting based on confidence scores
            weighted_scores = np.array(scores) * weights
            best_index = np.argmax(weighted_scores)
            
            return answers[best_index]
            
        except Exception as e:
            logging.warning(f"Answer ensemble failed: {e}")
            return answers[0] if answers else ""
    
    def _enhance_answer(self, answer: str, question: str, context: str) -> str:
        """Enhance answer with post-processing and validation"""
        try:
            # Clean the answer
            answer = answer.strip()
            
            # Apply legal-specific post-processing
            answer = self._apply_legal_postprocessing(answer, question)
            
            # Validate answer against context
            if not self._validate_answer_context(answer, context):
                # Try to extract a better answer from context
                extracted_answer = self._extract_answer_from_context(question, context)
                if extracted_answer:
                    answer = extracted_answer
            
            return answer
            
        except Exception as e:
            logging.warning(f"Answer enhancement failed: {e}")
            return answer
    
    def _apply_legal_postprocessing(self, answer: str, question: str) -> str:
        """Apply legal-specific post-processing rules"""
        try:
            # Remove common legal document artifacts
            answer = re.sub(r'\b(SEC\.|Section|Article)\s*\d+\.?', '', answer, flags=re.IGNORECASE)
            answer = re.sub(r'\s+', ' ', answer)
            
            # Handle specific question types
            question_lower = question.lower()
            
            if any(word in question_lower for word in ['how long', 'duration', 'period']):
                # Extract time-related information
                time_match = re.search(r'\d+\s*(years?|months?|days?|weeks?)', answer, re.IGNORECASE)
                if time_match:
                    return time_match.group(0)
            
            elif any(word in question_lower for word in ['how much', 'cost', 'price', 'amount']):
                # Extract monetary information
                money_match = re.search(r'\$\d{1,3}(,\d{3})*(\.\d{2})?', answer)
                if money_match:
                    return money_match.group(0)
            
            elif any(word in question_lower for word in ['when', 'date']):
                # Extract date information
                date_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', answer)
                if date_match:
                    return date_match.group(0)
            
            return answer.strip()
            
        except Exception as e:
            logging.warning(f"Legal post-processing failed: {e}")
            return answer
    
    def _validate_answer_context(self, answer: str, context: str) -> bool:
        """Validate if answer is present in context"""
        try:
            # Simple validation - check if key terms from answer are in context
            answer_terms = set(word.lower() for word in answer.split() if len(word) > 3)
            context_terms = set(word.lower() for word in context.split())
            
            # Check if at least 50% of answer terms are in context
            if answer_terms:
                overlap = len(answer_terms.intersection(context_terms)) / len(answer_terms)
                return overlap >= 0.5
            
            return True
            
        except Exception as e:
            logging.warning(f"Answer validation failed: {e}")
            return True
    
    def _extract_answer_from_context(self, question: str, context: str) -> Optional[str]:
        """Extract answer directly from context using patterns"""
        try:
            question_lower = question.lower()
            
            if any(word in question_lower for word in ['how long', 'duration', 'period']):
                match = re.search(r'\d+\s*(years?|months?|days?|weeks?)', context, re.IGNORECASE)
                return match.group(0) if match else None
            
            elif any(word in question_lower for word in ['how much', 'cost', 'price', 'amount']):
                match = re.search(r'\$\d{1,3}(,\d{3})*(\.\d{2})?', context)
                return match.group(0) if match else None
            
            elif any(word in question_lower for word in ['when', 'date']):
                match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', context)
                return match.group(0) if match else None
            
            return None
            
        except Exception as e:
            logging.warning(f"Answer extraction failed: {e}")
            return None
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better model performance"""
        try:
            # Remove common artifacts
            text = re.sub(r'[\\\n\r\u200b\u2022\u00a0_=]+', ' ', text)
            text = re.sub(r'<.*?>', ' ', text)
            text = re.sub(r'[^\x00-\x7F]+', ' ', text)
            text = re.sub(r'\s{2,}', ' ', text)
            
            # Normalize legal citations
            text = re.sub(r'\b(SEC\.|Section|Article)\s*\d+\.?', '', text, flags=re.IGNORECASE)
            
            return text.strip()
            
        except Exception as e:
            logging.warning(f"Text preprocessing failed: {e}")
            return text
    
    def _postprocess_summary(self, summary: str, all_summaries: list = None, min_sentences: int = 10) -> str:
        """Post-process summary for better readability"""
        try:
            summary = re.sub(r'[\\\n\r\u200b\u2022\u00a0_=]+', ' ', summary)
            summary = re.sub(r'[^\x00-\x7F]+', ' ', summary)
            summary = re.sub(r'\s{2,}', ' ', summary)
            # Remove redundant sentences
            sentences = summary.split('. ')
            unique_sentences = []
            for sentence in sentences:
                s = sentence.strip()
                if s and s not in unique_sentences:
                    unique_sentences.append(s)
            # If too short, add more unique sentences from other model outputs
            if all_summaries is not None and len(unique_sentences) < min_sentences:
                all_sentences = []
                for summ in all_summaries:
                    all_sentences.extend([s.strip() for s in summ.split('. ') if s.strip()])
                for s in all_sentences:
                    if s not in unique_sentences:
                        unique_sentences.append(s)
                    if len(unique_sentences) >= min_sentences:
                        break
            return '. '.join(unique_sentences)
        except Exception as e:
            logging.warning(f"Summary post-processing failed: {e}")
            return summary
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        try:
            # Simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
        except Exception as e:
            logging.warning(f"Sentence splitting failed: {e}")
            return [text]
    
    def _calculate_summary_confidence(self, summary: str, original_text: str) -> float:
        """Calculate confidence score for summary"""
        try:
            # Simple confidence based on summary length and content
            if not summary or len(summary) < 10:
                return 0.0
            
            # Check if summary contains key terms from original text
            summary_terms = set(word.lower() for word in summary.split() if len(word) > 3)
            original_terms = set(word.lower() for word in original_text.split() if len(word) > 3)
            
            if original_terms:
                overlap = len(summary_terms.intersection(original_terms)) / len(original_terms)
                return min(overlap * 2, 1.0)  # Scale overlap to 0-1 range
            
            return 0.5  # Default confidence
            
        except Exception as e:
            logging.warning(f"Confidence calculation failed: {e}")
            return 0.5

# Global instance
enhanced_model_manager = EnhancedModelManager() 