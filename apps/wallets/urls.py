from apps.core.routers import APIRouter

from .views import WalletViewSet

app_name = "wallets"

router = APIRouter()
router.register("", WalletViewSet, basename="wallet")

urlpatterns = router.urls
