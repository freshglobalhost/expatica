from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import EmailTokenObtainPairView
from apps.core.views import health_check

urlpatterns = [
    path("health/", health_check, name="health"),
    path("auth/token/", EmailTokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("accounts/", include("apps.accounts.urls")),
    path("wallets/", include("apps.wallets.urls")),
    path("transactions/", include("apps.transactions.urls")),
    path("banking/", include("apps.banking.urls")),
    path("loans/", include("apps.loans.urls")),
    path("cards/", include("apps.cards.urls")),
    path("investments/", include("apps.investments.urls")),
    path("savings/", include("apps.savings.urls")),
    path("support/", include("apps.support.urls")),
]
