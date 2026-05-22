from rest_framework.routers import DefaultRouter


class APIRouter(DefaultRouter):
    """JSON API router; disables format suffixes to avoid duplicate URL converter registration."""

    include_format_suffixes = False
