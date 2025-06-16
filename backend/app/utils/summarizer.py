from transformers import pipeline
import textwrap

# Load long-input legal summarizer
summarizer_pipeline = pipeline(
    "summarization",
    model="TheGod-2003/legal-summarizer",
    tokenizer="TheGod-2003/legal-summarizer"
)

def generate_summary(text):
    max_chunk = 3000  # This model supports long input chunks (16K tokens)

    paragraphs = textwrap.wrap(text, max_chunk)
    summaries = []

    for para in paragraphs:
        # For very short texts, let the model decide the lengths
        if len(para.split()) < 50:
            summary = summarizer_pipeline(
                para,
                max_length=None,  # Let model decide
                min_length=None,  # Let model decide
                do_sample=False
            )
        else:
            # Calculate dynamic lengths based on input text
            input_length = len(para.split())
            max_length = min(max(int(input_length * 0.3), 64), 512)  # Between 64 and 512
            min_length = min(int(max_length * 0.2), 30)  # 20% of max_length, but not more than 30

            summary = summarizer_pipeline(
                para,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
        summaries.append(summary[0]['summary_text'])

    return " ".join(summaries)
