import datetime
from django.db import transaction
from news.models import RawNews, TaggedNews, Tag, Category
from news.tagger.nlp import nlp_categorize
from news.tagger.keywords import TAG_KEYWORDS
from news.processors.description_summarizer import summarize_text


def process_raw_news():
    unprocessed_news = RawNews.objects.filter(status="raw")

    for raw in unprocessed_news:
        text = f"{raw.title} {raw.description or ''}".lower()
        matched_tags = set()
        selected_category = None

        # 1. Match from TAG_KEYWORDS
        for keyword, mapping in TAG_KEYWORDS.items():
            if keyword in text:
                if mapping["categories"]:
                    cat_name = mapping["categories"][0]
                    selected_category, _ = Category.objects.get_or_create(
                        name=cat_name)

                for tag_name in mapping["tags"]:
                    tag_obj, _ = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={"category": selected_category}
                    )
                    # if tag already exists but category is missing, patch it
                    if not tag_obj.category and selected_category:
                        tag_obj.category = selected_category
                        tag_obj.save()
                    matched_tags.add(tag_obj)
                break

        # 2. NLP fallback if nothing matched
        if not selected_category:
            best_cat_name = nlp_categorize(text, single=True)
            if best_cat_name:
                selected_category, _ = Category.objects.get_or_create(
                    name=best_cat_name)

        # 3. Guarantee exactly one category
        if not selected_category:
            selected_category, _ = Category.objects.get_or_create(
                name="Uncategorized")

        # 4. Save TaggedNews
        with transaction.atomic():
            tagged_news = TaggedNews.objects.create(
                raw_news=raw,
                processed_at=datetime.datetime.now(datetime.timezone.utc),
                summary=summarize_text(
                    getattr(raw, "description", "") or "")
            )

            tagged_news.categories.add(selected_category)
            if matched_tags:
                tagged_news.tags.add(*matched_tags)

        raw.status = "processed"
        raw.save()
