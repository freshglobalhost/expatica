from apps.core.routers import APIRouter

from .views import FAQViewSet, HelpArticleViewSet, HelpCategoryViewSet, SupportTicketViewSet

app_name = "support"

router = APIRouter()
router.register("categories", HelpCategoryViewSet, basename="help-category")
router.register("articles", HelpArticleViewSet, basename="help-article")
router.register("faqs", FAQViewSet, basename="faq")
router.register("tickets", SupportTicketViewSet, basename="support-ticket")

urlpatterns = router.urls
