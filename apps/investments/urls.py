from rest_framework.routers import DefaultRouter

from .views import InvestmentPlanViewSet, UserInvestmentViewSet

app_name = "investments"

router = DefaultRouter()
router.register("plans", InvestmentPlanViewSet, basename="investment-plan")
router.register("positions", UserInvestmentViewSet, basename="user-investment")

urlpatterns = router.urls
