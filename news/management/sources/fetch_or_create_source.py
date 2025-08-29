from news.models import Source


def fetch_or_create_source(name, url=None, icon_url=None):
    """Fetch an existing source or create/update it with provided details."""
    source, created = Source.objects.get_or_create(
        name=name.lower(),
        defaults={
            "url": url or "",
            "icon_url": icon_url or "",
        },
    )

    updated = False
    if url and not source.url:
        source.url = url
        updated = True
    if icon_url and not source.icon_url:
        source.icon_url = icon_url
        updated = True

    if updated:
        source.save()

    return source
