from huggingface_hub import InferenceClient
from transformers import AutoTokenizer
from decouple import config


def summarize_text(text):
    """Summarize any length text by truncating it based on tokens."""
    model_name = "facebook/bart-large-cnn"

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
    except Exception as e:
        print(f"Failed to load tokenizer for {model_name}. Error: {e}")
        return None

    # This is the fix: explicitly set a reasonable max_length value.
    # The BART model has a max input length of 1024 tokens.
    max_input_length = 1024

    # Tokenize the input text and get the IDs
    encoded_input = tokenizer(
        text,
        truncation=True,
        max_length=max_input_length,
        return_tensors='pt'
    )

    # Decode the truncated text back into a string
    truncated_text = tokenizer.decode(
        encoded_input['input_ids'][0], skip_special_tokens=True)

    client = InferenceClient(
        provider="hf-inference",
        api_key=config("HUGGINGFACE_TOKEN"),
    )

    try:
        result = client.summarization(
            text=truncated_text,
            model=model_name
        )
        return result.summary_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
