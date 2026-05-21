from rest_framework.routers import DefaultRouter

from .views import CardRequestViewSet, CardTransactionViewSet, VirtualCardViewSet

app_name = "cards"

router = DefaultRouter()
router.register("requests", CardRequestViewSet, basename="card-request")
router.register("transactions", CardTransactionViewSet, basename="card-transaction")
router.register("", VirtualCardViewSet, basename="virtual-card")

urlpatterns = router.urls
