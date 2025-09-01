from huggingface_hub import InferenceClient
from news.models import Category
from decouple import config

client = InferenceClient(
    model="facebook/bart-large-mnli",
    api_key=config("HUGGINGFACE_TOKEN")
)


def nlp_categorize(text: str, threshold: float = 0.7, single: bool = False):
    """
    Categorize text dynamically using DB categories via the Hugging Face Inference API.
    """
    if not text:
        return None if single else []

    candidate_categories = list(
        Category.objects.values_list("name", flat=True))
    if not candidate_categories:
        return None if single else []

    # Use the client's zero-shot classification method
    try:
        result = client.zero_shot_classification(
            sequence=text,
            candidate_labels=candidate_categories,
            multi_label=not single
        )
    except Exception as e:
        print(f"Error during API call: {e}")
        return None if single else []

    if single:
        return result["labels"][0] if result["labels"] else None

    labels = []
    for label, score in zip(result["labels"], result["scores"]):
        if score >= threshold:
            labels.append(label)

    return labels
