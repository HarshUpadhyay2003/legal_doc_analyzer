import re
from typing import Dict, List, Any

class EnhancedLegalProcessor:
    def __init__(self):
        # Patterns for different document elements
        self.table_pattern = re.compile(r'(\|\s*[^\n]+\s*\|(?:\n\|\s*[^\n]+\s*\|)+)')
        self.list_pattern = re.compile(r'(?:^|\n)(?:\d+\.|\*|\-)\s+[^\n]+(?:\n(?:\d+\.|\*|\-)\s+[^\n]+)*')
        self.formula_pattern = re.compile(r'\$[^$]+\$')
        self.abbreviation_pattern = re.compile(r'\b[A-Z]{2,}(?:\s+[A-Z]{2,})*\b')
        
    def process_document(self, text: str) -> Dict[str, Any]:
        """Process a legal document and extract various elements."""
        return {
            "tables": self._extract_tables(text),
            "lists": self._extract_lists(text),
            "formulas": self._extract_formulas(text),
            "abbreviations": self._extract_abbreviations(text),
            "definitions": self._extract_definitions(text),
            "cleaned_text": self._clean_text(text)
        }
    
    def _extract_tables(self, text: str) -> List[str]:
        """Extract tables from the text."""
        return self.table_pattern.findall(text)
    
    def _extract_lists(self, text: str) -> List[str]:
        """Extract lists from the text."""
        return self.list_pattern.findall(text)
    
    def _extract_formulas(self, text: str) -> List[str]:
        """Extract mathematical formulas from the text."""
        return self.formula_pattern.findall(text)
    
    def _extract_abbreviations(self, text: str) -> List[str]:
        """Extract abbreviations from the text."""
        return self.abbreviation_pattern.findall(text)
    
    def _extract_definitions(self, text: str) -> Dict[str, str]:
        """Extract definitions from the text."""
        definitions = {}
        # Pattern for "X means Y" or "X shall mean Y"
        definition_pattern = re.compile(r'([A-Z][A-Za-z\s]+)(?:\s+means|\s+shall\s+mean)\s+([^\.]+)')
        
        for match in definition_pattern.finditer(text):
            term = match.group(1).strip()
            definition = match.group(2).strip()
            definitions[term] = definition
            
        return definitions
    
    def _clean_text(self, text: str) -> str:
        """Clean the text by removing unnecessary whitespace and formatting."""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

# Create a singleton instance
enhanced_legal_processor = EnhancedLegalProcessor() 