from app.utils.enhanced_models import enhanced_model_manager

def generate_summary(text):
    result = enhanced_model_manager.generate_enhanced_summary(text)
    return result['summary']
