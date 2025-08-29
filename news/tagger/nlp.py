from transformers import pipeline
from news.models import Category

# Load Hugging Face pipeline once at import time
classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli")


def nlp_categorize(text: str, threshold: float = 0.7):
    """
    Categorize text dynamically using DB categories as candidate labels.
    Falls back to empty list if no categories exist.
    """
    if not text:
        return []

    # Pull candidate categories dynamically from DB
    candidate_categories = list(
        Category.objects.values_list("name", flat=True))
    if not candidate_categories:
        return []

    result = classifier(
        text,
        candidate_labels=candidate_categories,
        multi_label=True
    )

    labels = []
    for label, score in zip(result["labels"], result["scores"]):
        if score >= threshold:
            labels.append(label)

    return labels
