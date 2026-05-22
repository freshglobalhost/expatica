from apps.core.routers import APIRouter

from .views import (
    AutoSaveRuleViewSet,
    LockedSavingsAccountViewSet,
    SavingsGoalViewSet,
    SavingsTransactionViewSet,
)

app_name = "savings"

router = APIRouter()
router.register("goals", SavingsGoalViewSet, basename="savings-goal")
router.register("locked", LockedSavingsAccountViewSet, basename="locked-savings")
router.register("auto-save", AutoSaveRuleViewSet, basename="auto-save-rule")
router.register("transactions", SavingsTransactionViewSet, basename="savings-transaction")

urlpatterns = router.urls
