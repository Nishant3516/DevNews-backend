from django.db import models
from category.models import Category, Tag
from django.utils.text import slugify


class Source(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    icon_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class RawNews(models.Model):
    STATUS_CHOICES = [
        ("raw", "Raw"),
        ("processed", "Processed"),
        ("failed", "Failed"),
    ]

    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name="raw_news")
    source_news_id = models.CharField(
        max_length=255)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    url = models.URLField()
    source_url = models.URLField()
    published_at = models.DateTimeField()
    fetched_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="raw")
    img_url = models.URLField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_app_url(self):
        return f"https://myapp.com/news/{self.slug}/"

    def __str__(self):
        return self.title


class NewsType(models.Model):
    type = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type


class TaggedNews(models.Model):
    raw_news = models.ForeignKey(
        RawNews, on_delete=models.CASCADE, related_name="tagged_versions")
    processed_at = models.DateTimeField(null=True, blank=True)
    news_type = models.ForeignKey(
        NewsType, on_delete=models.SET_NULL, null=True, blank=True, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    summary = models.TextField(blank=True, null=True)
    likes = models.IntegerField(default=0)

    tags = models.ManyToManyField(
        Tag, through="TaggedNewsTags", related_name="tagged_news")
    categories = models.ManyToManyField(
        Category, through="TaggedNewsCategories", related_name="tagged_news")

    def __str__(self):
        return f"Tagged: {self.raw_news.title}"


class TaggedNewsTags(models.Model):
    tagged_news = models.ForeignKey(TaggedNews, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        db_table = "tagged_news_tags"
        unique_together = ("tagged_news", "tag")


class TaggedNewsCategories(models.Model):
    tagged_news = models.ForeignKey(TaggedNews, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = "tagged_news_categories"
        unique_together = ("tagged_news", "category")
