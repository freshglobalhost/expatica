from apps.core.routers import APIRouter

from .views import InvestmentPlanViewSet, UserInvestmentViewSet

app_name = "investments"

router = APIRouter()
router.register("plans", InvestmentPlanViewSet, basename="investment-plan")
router.register("positions", UserInvestmentViewSet, basename="user-investment")

urlpatterns = router.urls
