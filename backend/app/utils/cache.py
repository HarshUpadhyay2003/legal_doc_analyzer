from functools import lru_cache
import hashlib
import json

class QACache:
    def __init__(self, max_size=1000):
        self.max_size = max_size
        self._cache = {}
    
    def _generate_key(self, question, context):
        # Create a unique key based on question and context
        content = f"{question}:{context}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, question, context):
        key = self._generate_key(question, context)
        return self._cache.get(key)
    
    def set(self, question, context, answer):
        key = self._generate_key(question, context)
        if len(self._cache) >= self.max_size:
            # Remove the oldest item if cache is full
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = answer
    
    def clear(self):
        self._cache.clear()

# Create a global cache instance
qa_cache = QACache()

# Decorator for caching QA results
def cache_qa_result(func):
    def wrapper(question, context):
        # Try to get from cache first
        cached_result = qa_cache.get(question, context)
        if cached_result is not None:
            return cached_result
        
        # If not in cache, compute and cache the result
        result = func(question, context)
        qa_cache.set(question, context, result)
        return result
    return wrapper 