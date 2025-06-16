import re
from typing import Dict, List, Any
from functools import lru_cache

class ContextUnderstanding:
    def __init__(self):
        # Initialize cache for context analysis
        self._cache = {}
        
        # Define relationship patterns
        self.relationship_patterns = {
            'obligation': re.compile(r'(?:shall|must|will|should)\s+([^\.]+)'),
            'prohibition': re.compile(r'(?:shall\s+not|must\s+not|may\s+not)\s+([^\.]+)'),
            'condition': re.compile(r'(?:if|when|unless|provided\s+that)\s+([^\.]+)'),
            'exception': re.compile(r'(?:except|unless|however|notwithstanding)\s+([^\.]+)'),
            'definition': re.compile(r'(?:means|refers\s+to|shall\s+mean)\s+([^\.]+)')
        }
        
    def analyze_context(self, text: str) -> Dict[str, Any]:
        """Analyze the context of a legal document."""
        # Check cache first
        if text in self._cache:
            return self._cache[text]
        
        # Get relevant sections
        sections = self._get_relevant_sections(text)
        
        # Extract relationships
        relationships = self._extract_relationships(text)
        
        # Analyze implications
        implications = self._analyze_implications(text)
        
        # Analyze consequences
        consequences = self._analyze_consequences(text)
        
        # Analyze conditions
        conditions = self._analyze_conditions(text)
        
        # Combine results
        analysis = {
            "sections": sections,
            "relationships": relationships,
            "implications": implications,
            "consequences": consequences,
            "conditions": conditions
        }
        
        # Cache results
        self._cache[text] = analysis
        
        return analysis
    
    def _get_relevant_sections(self, text: str) -> List[Dict[str, str]]:
        """Get relevant sections from the text."""
        sections = []
        # Pattern for section headers
        section_pattern = re.compile(r'(?:Section|Article|Clause)\s+(\d+[\.\d]*)[:\.]\s*([^\n]+)')
        
        for match in section_pattern.finditer(text):
            section_number = match.group(1)
            section_title = match.group(2).strip()
            sections.append({
                "number": section_number,
                "title": section_title
            })
            
        return sections
    
    def _extract_relationships(self, text: str) -> Dict[str, List[str]]:
        """Extract relationships from the text."""
        relationships = {}
        
        for rel_type, pattern in self.relationship_patterns.items():
            matches = pattern.finditer(text)
            relationships[rel_type] = [match.group(1).strip() for match in matches]
            
        return relationships
    
    def _analyze_implications(self, text: str) -> List[Dict[str, str]]:
        """Analyze implications in the text."""
        implications = []
        # Pattern for implications like "if X, then Y"
        implication_pattern = re.compile(r'(?:if|when)\s+([^,]+),\s+(?:then|therefore)\s+([^\.]+)')
        
        for match in implication_pattern.finditer(text):
            condition = match.group(1).strip()
            result = match.group(2).strip()
            implications.append({
                "condition": condition,
                "result": result
            })
            
        return implications
    
    def _analyze_consequences(self, text: str) -> List[Dict[str, str]]:
        """Analyze consequences in the text."""
        consequences = []
        # Pattern for consequences like "failure to X shall result in Y"
        consequence_pattern = re.compile(r'(?:failure\s+to|non-compliance\s+with)\s+([^,]+),\s+(?:shall|will)\s+result\s+in\s+([^\.]+)')
        
        for match in consequence_pattern.finditer(text):
            action = match.group(1).strip()
            result = match.group(2).strip()
            consequences.append({
                "action": action,
                "result": result
            })
            
        return consequences
    
    def _analyze_conditions(self, text: str) -> List[Dict[str, str]]:
        """Analyze conditions in the text."""
        conditions = []
        # Pattern for conditions like "subject to X" or "conditioned upon X"
        condition_pattern = re.compile(r'(?:subject\s+to|conditioned\s+upon|contingent\s+upon)\s+([^\.]+)')
        
        for match in condition_pattern.finditer(text):
            condition = match.group(1).strip()
            conditions.append({
                "condition": condition
            })
            
        return conditions
    
    def clear_cache(self):
        """Clear the context analysis cache."""
        self._cache.clear()

# Create a singleton instance
context_understanding = ContextUnderstanding() 