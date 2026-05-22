from apps.core.routers import APIRouter

from .views import (
    LoanApplicationViewSet,
    LoanProductViewSet,
    LoanRepaymentViewSet,
    LoanViewSet,
)

app_name = "loans"

router = APIRouter()
router.register("products", LoanProductViewSet, basename="loan-product")
router.register("applications", LoanApplicationViewSet, basename="loan-application")
router.register("repayments", LoanRepaymentViewSet, basename="loan-repayment")
router.register("", LoanViewSet, basename="loan")

urlpatterns = router.urls
