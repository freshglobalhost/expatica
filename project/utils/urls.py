from django.urls import URLPattern, URLResolver


def list_urls(lis, acc=None):
    """gets all urls so it can be printed from the command line"""
    if acc is None:
        acc = []

    if not lis:
        return

    l = lis[0]

    if isinstance(l, URLPattern):
        yield acc + [str(l.pattern)]

    elif isinstance(l, URLResolver):
        yield from list_urls(l.url_patterns, acc + [str(l.pattern)])

    yield from list_urls(lis[1:], acc)


