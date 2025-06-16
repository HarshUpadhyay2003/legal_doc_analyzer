import pytest
import time
from app.utils.cache import QACache, cache_qa_result
from app.nlp.qa import answer_question

def test_cache_basic():
    # Create a new cache instance
    cache = QACache(max_size=10)
    
    # Test setting and getting values
    cache.set("q1", "c1", "a1")
    assert cache.get("q1", "c1") == "a1"
    
    # Test cache miss
    assert cache.get("q2", "c2") is None

def test_cache_size_limit():
    # Create a small cache
    cache = QACache(max_size=2)
    
    # Fill the cache
    cache.set("q1", "c1", "a1")
    cache.set("q2", "c2", "a2")
    cache.set("q3", "c3", "a3")  # This should remove q1
    
    # Verify oldest item was removed
    assert cache.get("q1", "c1") is None
    assert cache.get("q2", "c2") == "a2"
    assert cache.get("q3", "c3") == "a3"

def test_qa_caching():
    # Test data with very different contexts and questions
    question1 = "What is the punishment for theft under IPC?"
    context1 = "Section 378 of IPC defines theft. The punishment for theft is imprisonment up to 3 years or fine or both."
    
    question2 = "What are the conditions for bail in a murder case?"
    context2 = "Section 437 of CrPC states that bail may be granted in non-bailable cases except for murder. The court must be satisfied that there are reasonable grounds for believing that the accused is not guilty."
    
    # First call for question1
    start_time = time.time()
    result1 = answer_question(question1, context1)
    first_call_time = time.time() - start_time
    
    # Second call for question1 (should use cache)
    start_time = time.time()
    result2 = answer_question(question1, context1)
    second_call_time = time.time() - start_time
    
    # Verify results are the same for cached question
    assert result1 == result2
    
    # Verify second call was faster (cached)
    assert second_call_time < first_call_time
    
    # Call for question2 (should not use cache)
    result3 = answer_question(question2, context2)
    
    # Verify different questions give different results
    assert result1["answer"] != result3["answer"]
    
    # Verify cache is working by calling question1 again
    start_time = time.time()
    result4 = answer_question(question1, context1)
    third_call_time = time.time() - start_time
    
    # Should still be using cache
    assert result4 == result1
    assert third_call_time < first_call_time

def test_cache_clear():
    cache = QACache()
    
    # Add some items
    cache.set("q1", "c1", "a1")
    cache.set("q2", "c2", "a2")
    
    # Clear cache
    cache.clear()
    
    # Verify cache is empty
    assert cache.get("q1", "c1") is None
    assert cache.get("q2", "c2") is None 