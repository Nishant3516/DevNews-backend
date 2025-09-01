from transformers import pipeline
from news.models import Category

# Load Hugging Face pipeline once at import time
classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli")


def nlp_categorize(text: str, threshold: float = 0.7, single: bool = False):
    """
    Categorize text dynamically using DB categories as candidate labels.

    - If single=True → return the best category.
    - If single=False → return all categories with score >= threshold.
    """
    if not text:
        return None if single else []

    candidate_categories = list(
        Category.objects.values_list("name", flat=True))
    if not candidate_categories:
        return None if single else []

    result = classifier(
        text,
        candidate_labels=candidate_categories,
        multi_label=not single  # single=False → pick one, else multi
    )

    if single:
        return result["labels"][0] if result["labels"] else None

    labels = []
    for label, score in zip(result["labels"], result["scores"]):
        if score >= threshold:
            labels.append(label)

    return labels
