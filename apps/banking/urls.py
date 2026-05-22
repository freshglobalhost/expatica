from apps.core.routers import APIRouter

from .views import TransferMethodViewSet, TransferViewSet

app_name = "banking"

router = APIRouter()
router.register("methods", TransferMethodViewSet, basename="transfer-method")
router.register("transfers", TransferViewSet, basename="transfer")

urlpatterns = router.urls
