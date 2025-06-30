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
    
    def generate_enhanced_summary(self, text: str, max_length: int = 4096, min_length: int = 200) -> Dict[str, Any]:
        """
        Generate enhanced summary using ensemble approach with multiple models
        """
        try:
            summaries = []
            weights = []
            cleaned_text = self._preprocess_text(text)
            
            # Handle long documents with improved chunking
            cleaned_text = self._handle_long_documents(cleaned_text)
            
            # Only legal summarizer
            if 'legal_summarizer' in self.models:
                try:
                    # Improved parameters for LED-16384 model
                    summary = self.models['legal_summarizer'](
                        cleaned_text,
                        max_length=max_length,
                        min_length=min_length,
                        num_beams=5,  # Increased for better quality
                        length_penalty=1.2,  # Slightly favor longer summaries
                        repetition_penalty=1.5,  # Reduced to avoid over-penalization
                        no_repeat_ngram_size=2,  # Reduced for legal text
                        early_stopping=False,  # Disabled to prevent premature stopping
                        do_sample=True,  # Enable sampling for better diversity
                        temperature=0.7,  # Add some randomness
                        top_p=0.9,  # Nucleus sampling
                        pad_token_id=self.models['legal_summarizer'].tokenizer.eos_token_id,
                        eos_token_id=self.models['legal_summarizer'].tokenizer.eos_token_id
                    )[0]['summary_text']
                    
                    # Ensure summary is complete
                    summary = self._ensure_complete_summary(summary, cleaned_text)
                    
                    # Retry if summary is too short or incomplete
                    if len(summary.split()) < min_length or not summary.strip().endswith(('.', '!', '?')):
                        logging.info("Summary too short or incomplete, retrying with different parameters...")
                        retry_summary = self.models['legal_summarizer'](
                            cleaned_text,
                            max_length=max_length * 2,  # Double the max length
                            min_length=min_length,
                            num_beams=3,  # Reduce beams for faster generation
                            length_penalty=1.5,  # Favor longer summaries
                            repetition_penalty=1.2,
                            no_repeat_ngram_size=1,
                            early_stopping=False,
                            do_sample=False,  # Disable sampling for more deterministic output
                            pad_token_id=self.models['legal_summarizer'].tokenizer.eos_token_id,
                            eos_token_id=self.models['legal_summarizer'].tokenizer.eos_token_id
                        )[0]['summary_text']
                        
                        retry_summary = self._ensure_complete_summary(retry_summary, cleaned_text)
                        if len(retry_summary.split()) > len(summary.split()):
                            summary = retry_summary
                    
                    summaries.append(summary)
                    weights.append(1.0)
                    
                except Exception as e:
                    logging.warning(f"Legal summarizer failed: {e}")
                    # Fallback to extractive summarization
                    fallback_summary = self._extractive_summarization(cleaned_text, max_length)
                    if fallback_summary:
                        summaries.append(fallback_summary)
                        weights.append(1.0)
            
            if not summaries:
                raise Exception("No models could generate summaries")
            
            final_summary = self._ensemble_summaries(summaries, weights)
            final_summary = self._postprocess_summary(final_summary, summaries, min_sentences=8)
            
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
            # Remove common artifacts but preserve legal structure
            text = re.sub(r'[\\\n\r\u200b\u2022\u00a0_=]+', ' ', text)
            text = re.sub(r'<.*?>', ' ', text)
            
            # Preserve legal citations and numbers (don't remove them completely)
            # Instead of removing section numbers, normalize them
            text = re.sub(r'\b(SEC\.|Section|Article)\s*(\d+)\.?', r'Section \2', text, flags=re.IGNORECASE)
            
            # Clean up excessive whitespace
            text = re.sub(r'\s{2,}', ' ', text)
            
            # Preserve important legal punctuation and formatting
            text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)  # Ensure proper sentence spacing
            
            # Remove non-printable characters but keep legal symbols
            text = re.sub(r'[^\x00-\x7F]+', ' ', text)
            
            # Ensure proper spacing around legal terms
            text = re.sub(r'\b(Lessee|Lessor|Party|Parties)\b', r' \1 ', text, flags=re.IGNORECASE)
            
            return text.strip()
            
        except Exception as e:
            logging.warning(f"Text preprocessing failed: {e}")
            return text
    
    def _chunk_text_for_summarization(self, text: str, max_words: int = 8000) -> str:
        """Chunk long text for summarization while preserving legal document structure"""
        try:
            words = text.split()
            if len(words) <= max_words:
                return text
            
            # Split into sentences first
            sentences = self._split_into_sentences(text)
            
            # Take the most important sentences (first and last portions)
            total_sentences = len(sentences)
            if total_sentences <= 50:
                return text
            
            # Take first 60% and last 20% of sentences
            first_portion = int(total_sentences * 0.6)
            last_portion = int(total_sentences * 0.2)
            
            selected_sentences = sentences[:first_portion] + sentences[-last_portion:]
            chunked_text = " ".join(selected_sentences)
            
            # Ensure we don't exceed token limit
            if len(chunked_text.split()) > max_words:
                chunked_text = " ".join(chunked_text.split()[:max_words])
            
            return chunked_text
            
        except Exception as e:
            logging.warning(f"Text chunking failed: {e}")
            return text
    
    def _handle_long_documents(self, text: str) -> str:
        """Handle very long documents by using a sliding window approach"""
        try:
            # LED-16384 has a context window of ~16k tokens
            # Conservative estimate: ~12k tokens for input to leave room for generation
            max_tokens = 12000
            
            # Approximate tokens (roughly 1.3 words per token for English)
            words = text.split()
            if len(words) <= max_tokens * 0.8:  # Conservative limit
                return text
            
            # Use sliding window approach for very long documents
            sentences = self._split_into_sentences(text)
            
            if len(sentences) < 10:
                return text
            
            # Take key sections: beginning, middle, and end
            total_sentences = len(sentences)
            
            # Take first 40%, middle 20%, and last 40%
            first_end = int(total_sentences * 0.4)
            middle_start = int(total_sentences * 0.4)
            middle_end = int(total_sentences * 0.6)
            last_start = int(total_sentences * 0.6)
            
            key_sentences = (
                sentences[:first_end] + 
                sentences[middle_start:middle_end] + 
                sentences[last_start:]
            )
            
            # Ensure we don't exceed token limit
            combined_text = " ".join(key_sentences)
            words = combined_text.split()
            
            if len(words) > max_tokens * 0.8:
                # Truncate to safe limit
                combined_text = " ".join(words[:int(max_tokens * 0.8)])
            
            return combined_text
            
        except Exception as e:
            logging.warning(f"Long document handling failed: {e}")
            return text
    
    def _ensure_complete_summary(self, summary: str, original_text: str) -> str:
        """Ensure the summary is complete and not truncated mid-sentence"""
        try:
            if not summary:
                return summary
            
            # Check if summary ends with complete sentence
            if not summary.rstrip().endswith(('.', '!', '?')):
                # Find the last complete sentence
                sentences = summary.split('. ')
                if len(sentences) > 1:
                    # Remove the incomplete last sentence
                    summary = '. '.join(sentences[:-1]) + '.'
            
            # Ensure minimum length
            if len(summary.split()) < 50:
                # Try to extract more content from original text
                additional_content = self._extract_key_sentences(original_text, 100)
                if additional_content:
                    summary = summary + " " + additional_content
            
            return summary.strip()
            
        except Exception as e:
            logging.warning(f"Summary completion check failed: {e}")
            return summary
    
    def _extract_key_sentences(self, text: str, max_words: int = 100) -> str:
        """Extract key sentences from text for summary completion"""
        try:
            sentences = self._split_into_sentences(text)
            
            # Simple heuristic: take sentences with legal keywords
            legal_keywords = ['lease', 'rent', 'payment', 'term', 'agreement', 'lessor', 'lessee', 
                            'covenant', 'obligation', 'right', 'duty', 'termination', 'renewal']
            
            key_sentences = []
            word_count = 0
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in legal_keywords):
                    sentence_words = len(sentence.split())
                    if word_count + sentence_words <= max_words:
                        key_sentences.append(sentence)
                        word_count += sentence_words
                    else:
                        break
            
            return " ".join(key_sentences)
            
        except Exception as e:
            logging.warning(f"Key sentence extraction failed: {e}")
            return ""
    
    def _extractive_summarization(self, text: str, max_length: int) -> str:
        """Fallback extractive summarization using TF-IDF"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            sentences = self._split_into_sentences(text)
            
            if len(sentences) < 3:
                return text
            
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Calculate sentence importance based on TF-IDF scores
            sentence_scores = []
            for i in range(len(sentences)):
                score = tfidf_matrix[i].sum()
                sentence_scores.append((score, i))
            
            # Sort by score and take top sentences
            sentence_scores.sort(reverse=True)
            
            # Select sentences up to max_length
            selected_indices = []
            total_words = 0
            
            for score, idx in sentence_scores:
                sentence_words = len(sentences[idx].split())
                if total_words + sentence_words <= max_length // 2:  # Conservative estimate
                    selected_indices.append(idx)
                    total_words += sentence_words
                else:
                    break
            
            # Sort by original order
            selected_indices.sort()
            summary_sentences = [sentences[i] for i in selected_indices]
            
            return " ".join(summary_sentences)
            
        except Exception as e:
            logging.warning(f"Extractive summarization failed: {e}")
            return text[:max_length] if len(text) > max_length else text
    
    def _postprocess_summary(self, summary: str, all_summaries: Optional[List[str]] = None, min_sentences: int = 10) -> str:
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
        """Split text into sentences with improved handling for legal documents"""
        try:
            # More sophisticated sentence splitting for legal documents
            # Handle legal abbreviations and citations properly
            text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
            
            # Split on sentence endings, but be careful with legal citations
            sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
            
            # Clean up sentences
            cleaned_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 10:  # Filter out very short fragments
                    # Handle legal abbreviations that might have been split
                    if sentence.startswith(('Sec', 'Art', 'Clause', 'Para')):
                        # This might be a continuation, try to merge with previous
                        if cleaned_sentences:
                            cleaned_sentences[-1] = cleaned_sentences[-1] + " " + sentence
                        else:
                            cleaned_sentences.append(sentence)
                    else:
                        cleaned_sentences.append(sentence)
            
            return cleaned_sentences if cleaned_sentences else [text]
            
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