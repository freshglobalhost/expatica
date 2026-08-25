from apps.core.routers import APIRouter

from .views import TransferMethodViewSet, TransferViewSet, WithdrawalViewSet

app_name = "banking"

router = APIRouter()
router.register("methods", TransferMethodViewSet, basename="transfer-method")
router.register("transfers", TransferViewSet, basename="transfer")
router.register("withdrawals", WithdrawalViewSet, basename="withdrawal")

urlpatterns = router.urls
