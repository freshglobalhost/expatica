from django.urls import path

from .views import (
    DashboardSummaryView,
    ForgotPasswordView,
    PasswordChangeView,
    ProfileView,
    RegisterView,
    ResetPasswordView,
    TransactionPinChangeView,
    VerifyResetCodeView,
    VerifyTransactionPinView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", ProfileView.as_view(), name="profile"),
    path("me/dashboard/", DashboardSummaryView.as_view(), name="dashboard"),
    path("me/password/", PasswordChangeView.as_view(), name="password-change"),
    path("me/transaction-pin/", TransactionPinChangeView.as_view(), name="transaction-pin-change"),
    path("verify-transaction-pin/", VerifyTransactionPinView.as_view(), name="verify-transaction-pin"),
    path("password/forgot/", ForgotPasswordView.as_view(), name="password-forgot"),
    path("password/verify-code/", VerifyResetCodeView.as_view(), name="password-verify-code"),
    path("password/reset/", ResetPasswordView.as_view(), name="password-reset"),
]
