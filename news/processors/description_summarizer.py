from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def summarize_text(text, target_length=70):
    """Generate abstractive summary with BART model.
       Falls back safely for short/empty text."""
    if not text or not text.strip():
        return ""

    input_len = len(text.split())

    max_len = min(target_length, input_len)
    min_len = max(5, min(max_len - 5, 60))

    try:
        result = summarizer(
            text,
            max_length=max_len,
            min_length=min_len,
            do_sample=False
        )
        return result[0]["summary_text"]
    except Exception as e:
        print(f"[WARN] Summarizer failed: {e}")
        return text
