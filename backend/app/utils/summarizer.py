from transformers import pipeline
import textwrap

# Load long-input legal summarizer
summarizer_pipeline = pipeline(
    "summarization",
    model="nsi319/legal-led-base-16384",
    tokenizer="nsi319/legal-led-base-16384"
)

def generate_summary(text):
    max_chunk = 3000  # This model supports long input chunks (16K tokens)

    paragraphs = textwrap.wrap(text, max_chunk)
    summaries = []

    for para in paragraphs:
        summary = summarizer_pipeline(
            para,
            max_length=512,  # Increased output size for legal text
            min_length=100,
            do_sample=False
        )
        summaries.append(summary[0]['summary_text'])

    return " ".join(summaries)
