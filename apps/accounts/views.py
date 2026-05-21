import logging
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Sum
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.cards.models import VirtualCard
from apps.cards.serializers import VirtualCardSerializer
from apps.loans.models import Loan
from apps.loans.serializers import LoanSerializer
from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer
from apps.wallets.models import Wallet
from apps.wallets.serializers import WalletSerializer

from .dashboard_utils import build_dashboard_notifications
from .models import PasswordResetCode
from .serializers import (
    ForgotPasswordSerializer,
    PasswordChangeSerializer,
    ResetPasswordSerializer,
    TransactionPinChangeSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    VerifyResetCodeSerializer,
    VerifyTransactionPinSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user, context={"request": request}).data, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserProfileUpdateSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = UserProfileUpdateSerializer(
            instance,
            data=request.data,
            partial=partial,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.refresh_from_db()
        return Response(UserSerializer(user, context={"request": request}).data)


class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        wallets = Wallet.objects.filter(user=user)
        primary = wallets.filter(currency_code="USD").first() or wallets.first()
        total_balance = wallets.aggregate(total=Sum("balance"))["total"] or Decimal("0")

        loan_balance = (
            Loan.objects.filter(user=user, status=Loan.Status.ACTIVE).aggregate(
                total=Sum("outstanding_balance")
            )["total"]
            or Decimal("0")
        )

        deposit_balance = (
            Transaction.objects.filter(
                user=user,
                category=Transaction.Category.DEPOSIT,
                status=Transaction.Status.COMPLETED,
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0")
        )

        recent_qs = Transaction.objects.filter(user=user).order_by("-created_at")[:5]
        active_loans_qs = (
            Loan.objects.filter(
                user=user,
                status__in=[Loan.Status.ACTIVE, Loan.Status.APPROVED],
            )
            .select_related("product")
            .prefetch_related("repayments")
            .order_by("-created_at")[:5]
        )
        cards_qs = VirtualCard.objects.filter(user=user).order_by("-created_at")[:5]
        ctx = {"request": request}

        return Response(
            {
                "user": UserSerializer(user, context=ctx).data,
                "primary_wallet": (
                    WalletSerializer(primary, context=ctx).data if primary else None
                ),
                "primary_wallet_balance": str(primary.balance if primary else 0),
                "total_balance": str(total_balance),
                "deposit_balance": str(deposit_balance),
                "loan_balance": str(loan_balance),
                "currency_code": primary.currency_code if primary else "USD",
                "btc_balance": str(primary.btc_balance if primary else 0),
                "eth_balance": str(primary.eth_balance if primary else 0),
                "usdt_balance": str(primary.usdt_balance if primary else 0),
                "sol_balance": str(primary.sol_balance if primary else 0),
                "recent_transactions": TransactionSerializer(
                    recent_qs, many=True, context=ctx
                ).data,
                "recent_transactions_count": Transaction.objects.filter(user=user).count(),
                "active_loans": LoanSerializer(active_loans_qs, many=True, context=ctx).data,
                "virtual_cards": VirtualCardSerializer(cards_qs, many=True, context=ctx).data,
                "notifications": build_dashboard_notifications(user),
            }
        )


class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password updated successfully."})


class TransactionPinChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TransactionPinChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Transaction PIN updated."})


class VerifyTransactionPinView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VerifyTransactionPinSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response({"valid": True, "detail": "Transaction PIN verified."})


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()

        user_exists = User.objects.filter(email__iexact=email).exists()
        if user_exists:
            reset = PasswordResetCode.create_for_email(email)
            message = (
                f"Your PennyCredit password reset code is {reset.code}. "
                "It expires in 15 minutes."
            )
            send_mail(
                subject="PennyCredit password reset",
                message=message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@pennycredit.com"),
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info("Password reset code for %s: %s", email, reset.code)

        return Response(
            {
                "detail": "If an account exists for this email, a reset code has been sent.",
            }
        )


class VerifyResetCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyResetCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        code = serializer.validated_data["code"]

        reset = (
            PasswordResetCode.objects.filter(
                email__iexact=email,
                code=code,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not reset or not reset.is_valid():
            return Response(
                {"detail": "Invalid or expired verification code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reset.is_verified = True
        reset.save(update_fields=["is_verified"])

        return Response(
            {
                "detail": "Code verified.",
                "reset_token": reset.reset_token,
                "email": reset.email,
            }
        )


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        token = serializer.validated_data["reset_token"]
        new_password = serializer.validated_data["new_password"]

        reset = (
            PasswordResetCode.objects.filter(
                email__iexact=email,
                reset_token=token,
                is_verified=True,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not reset or not reset.is_valid():
            return Response(
                {"detail": "Invalid or expired reset session. Request a new code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"detail": "Account not found."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save(update_fields=["password"])
        reset.is_used = True
        reset.save(update_fields=["is_used"])

        return Response({"detail": "Password reset successfully. You can sign in now."})
