from rest_framework.routers import DefaultRouter

from .views import FAQViewSet, HelpArticleViewSet, HelpCategoryViewSet, SupportTicketViewSet

app_name = "support"

router = DefaultRouter()
router.register("categories", HelpCategoryViewSet, basename="help-category")
router.register("articles", HelpArticleViewSet, basename="help-article")
router.register("faqs", FAQViewSet, basename="faq")
router.register("tickets", SupportTicketViewSet, basename="support-ticket")

urlpatterns = router.urls
