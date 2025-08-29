from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def summarize_text(text, max_words=70):
    """Generate abstractive summary with ~70 words using BART model."""
    if not text:
        return ""

    result = summarizer(text, max_length=70, min_length=60, do_sample=False)
    return result[0]["summary_text"]
