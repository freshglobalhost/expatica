from rest_framework.routers import DefaultRouter

from .views import WalletViewSet

app_name = "wallets"

router = DefaultRouter()
router.register("", WalletViewSet, basename="wallet")

urlpatterns = router.urls
