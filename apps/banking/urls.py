from rest_framework.routers import DefaultRouter

from .views import TransferMethodViewSet, TransferViewSet

app_name = "banking"

router = DefaultRouter()
router.register("methods", TransferMethodViewSet, basename="transfer-method")
router.register("transfers", TransferViewSet, basename="transfer")

urlpatterns = router.urls
