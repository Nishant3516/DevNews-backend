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
        matched_categories = set()

        # 1. Match from TAG_KEYWORDS
        for keyword, mapping in TAG_KEYWORDS.items():
            if keyword in text:
                # Create categories first
                category_objs = []
                for cat_name in mapping["categories"]:
                    cat_obj, _ = Category.objects.get_or_create(name=cat_name)
                    category_objs.append(cat_obj)
                    matched_categories.add(cat_obj)

                # Create tags linked to first category (or default)
                main_category = category_objs[0] if category_objs else None
                for tag_name in mapping["tags"]:
                    tag_obj, _ = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={"category": main_category}
                    )
                    # if tag already exists but category is missing, patch it
                    if not tag_obj.category and main_category:
                        tag_obj.category = main_category
                        tag_obj.save()
                    matched_tags.add(tag_obj)

        # 2. NLP fallback if nothing matched
        if not matched_categories:
            nlp_categories = nlp_categorize(text)
            for cat_name in nlp_categories:
                cat_obj, _ = Category.objects.get_or_create(name=cat_name)
                matched_categories.add(cat_obj)

        # 3. Guarantee at least one category
        if not matched_categories:
            cat_obj, _ = Category.objects.get_or_create(name="Uncategorized")
            matched_categories.add(cat_obj)

        # 4. Save TaggedNews
        with transaction.atomic():
            tagged_news = TaggedNews.objects.create(
                raw_news=raw,
                processed_at=datetime.datetime.now(datetime.timezone.utc),
                summary=summarize_text(
                    getattr(raw, "description", "") or "")
            )

            if matched_categories:
                tagged_news.categories.add(*matched_categories)
            if matched_tags:
                tagged_news.tags.add(*matched_tags)

        raw.status = "processed"
        raw.save()
