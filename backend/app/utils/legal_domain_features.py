import re
from typing import Dict, List, Set, Any

class LegalDomainFeatures:
    def __init__(self):
        # Initialize sets for different legal entities
        self.parties = set()
        self.dates = set()
        self.amounts = set()
        self.citations = set()
        self.jurisdictions = set()
        self.courts = set()
        self.statutes = set()
        self.regulations = set()
        self.cases = set()
        
        # Compile regex patterns
        self.patterns = {
            'parties': re.compile(r'\b(?:Party|Parties|Lessor|Lessee|Buyer|Seller|Plaintiff|Defendant)\s+(?:of|to|in|the)\s+(?:the\s+)?(?:first|second|third|fourth|fifth)\s+(?:part|party)\b'),
            'dates': re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}\b'),
            'amounts': re.compile(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'),
            'citations': re.compile(r'\b\d+\s+U\.S\.C\.\s+\d+|\b\d+\s+F\.R\.\s+\d+|\b\d+\s+CFR\s+\d+'),
            'jurisdictions': re.compile(r'\b(?:State|Commonwealth|District|Territory)\s+of\s+[A-Za-z\s]+'),
            'courts': re.compile(r'\b(?:Supreme|Appellate|District|Circuit|County|Municipal)\s+Court\b'),
            'statutes': re.compile(r'\b(?:Act|Statute|Law|Code)\s+of\s+[A-Za-z\s]+\b'),
            'regulations': re.compile(r'\b(?:Regulation|Rule|Order)\s+\d+\b'),
            'cases': re.compile(r'\b[A-Za-z]+\s+v\.\s+[A-Za-z]+\b')
        }
        
    def process_legal_document(self, text: str) -> Dict[str, Any]:
        """Process a legal document and extract domain-specific features."""
        # Clear previous extractions
        self._clear_extractions()
        
        # Extract legal entities
        self._extract_legal_entities(text)
        
        # Extract relationships
        relationships = self._extract_legal_relationships(text)
        
        # Extract legal terms
        terms = self._extract_legal_terms(text)
        
        # Categorize document
        category = self._categorize_document(text)
        
        return {
            "entities": {
                "parties": list(self.parties),
                "dates": list(self.dates),
                "amounts": list(self.amounts),
                "citations": list(self.citations),
                "jurisdictions": list(self.jurisdictions),
                "courts": list(self.courts),
                "statutes": list(self.statutes),
                "regulations": list(self.regulations),
                "cases": list(self.cases)
            },
            "relationships": relationships,
            "terms": terms,
            "category": category
        }
    
    def _clear_extractions(self):
        """Clear all extracted entities."""
        self.parties.clear()
        self.dates.clear()
        self.amounts.clear()
        self.citations.clear()
        self.jurisdictions.clear()
        self.courts.clear()
        self.statutes.clear()
        self.regulations.clear()
        self.cases.clear()
    
    def _extract_legal_entities(self, text: str):
        """Extract legal entities from the text."""
        for entity_type, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                getattr(self, entity_type).add(match.group())
    
    def _extract_legal_relationships(self, text: str) -> List[Dict[str, str]]:
        """Extract legal relationships from the text."""
        relationships = []
        # Pattern for relationships like "X shall Y" or "X must Y"
        relationship_pattern = re.compile(r'([A-Z][A-Za-z\s]+)(?:\s+shall|\s+must|\s+will)\s+([^\.]+)')
        
        for match in relationship_pattern.finditer(text):
            subject = match.group(1).strip()
            obligation = match.group(2).strip()
            relationships.append({
                "subject": subject,
                "obligation": obligation
            })
            
        return relationships
    
    def _extract_legal_terms(self, text: str) -> Dict[str, str]:
        """Extract legal terms and their definitions."""
        terms = {}
        # Pattern for terms like "X means Y" or "X shall mean Y"
        term_pattern = re.compile(r'([A-Z][A-Za-z\s]+)(?:\s+means|\s+shall\s+mean)\s+([^\.]+)')
        
        for match in term_pattern.finditer(text):
            term = match.group(1).strip()
            definition = match.group(2).strip()
            terms[term] = definition
            
        return terms
    
    def _categorize_document(self, text: str) -> str:
        """Categorize the document based on its content."""
        # Simple categorization based on keywords
        if any(word in text.lower() for word in ['contract', 'agreement', 'lease']):
            return "Contract"
        elif any(word in text.lower() for word in ['complaint', 'petition', 'motion']):
            return "Pleading"
        elif any(word in text.lower() for word in ['statute', 'act', 'law']):
            return "Statute"
        elif any(word in text.lower() for word in ['regulation', 'rule', 'order']):
            return "Regulation"
        else:
            return "Other"

# Create a singleton instance
legal_domain_features = LegalDomainFeatures() 