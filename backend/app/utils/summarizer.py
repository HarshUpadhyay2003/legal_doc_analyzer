from app.utils.enhanced_models import enhanced_model_manager

def generate_summary(text, max_length=4096, min_length=200):
    """
    Generate summary with improved parameters for legal documents
    
    Args:
        text (str): The text to summarize
        max_length (int): Maximum length of the summary (default: 4096)
        min_length (int): Minimum length of the summary (default: 200)
    
    Returns:
        str: The generated summary
    """
    try:
        result = enhanced_model_manager.generate_enhanced_summary(
            text=text,
            max_length=max_length,
            min_length=min_length
        )
        return result['summary']
    except Exception as e:
        # Fallback to basic text truncation if summarization fails
        print(f"Summary generation failed: {e}")
        words = text.split()
        if len(words) > 200:
            return " ".join(words[:200]) + "..."
        return text
