from apps.core.routers import APIRouter

from .views import TransactionViewSet

app_name = "transactions"

router = APIRouter()
router.register("", TransactionViewSet, basename="transaction")

urlpatterns = router.urls
