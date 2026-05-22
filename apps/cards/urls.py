from apps.core.routers import APIRouter

from .views import CardRequestViewSet, CardTransactionViewSet, VirtualCardViewSet

app_name = "cards"

router = APIRouter()
router.register("requests", CardRequestViewSet, basename="card-request")
router.register("transactions", CardTransactionViewSet, basename="card-transaction")
router.register("", VirtualCardViewSet, basename="virtual-card")

urlpatterns = router.urls
