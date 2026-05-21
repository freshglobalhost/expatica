from decimal import Decimal

from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.viewsets import UserScopedViewSet
from apps.wallets.models import Wallet

from .card_utils import format_pan
from .models import CardRequest, CardTransaction, VirtualCard
from .serializers import (
    CardRequestCreateSerializer,
    CardRequestSerializer,
    CardSensitiveRevealSerializer,
    CardTransactionSerializer,
    VirtualCardSerializer,
)

MIN_CARD_FUND_AMOUNT = Decimal("10")


class VirtualCardViewSet(UserScopedViewSet):
    serializer_class = VirtualCardSerializer
    queryset = VirtualCard.objects.all()
    http_method_names = ["get", "head", "options", "patch", "post"]

    @action(detail=True, methods=["post"], url_path="reveal-sensitive")
    def reveal_sensitive(self, request, pk=None):
        card = self.get_object()
        serializer = CardSensitiveRevealSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "card_number": format_pan(card.card_number),
                "card_number_raw": card.card_number,
                "cvv": card.cvv,
                "cardholder_name": card.cardholder_name,
            }
        )

    @action(detail=True, methods=["post"])
    def freeze(self, request, pk=None):
        card = self.get_object()
        card.is_frozen = True
        card.save(update_fields=["is_frozen", "updated_at"])
        return Response(self.get_serializer(card).data)

    @action(detail=True, methods=["post"])
    def unfreeze(self, request, pk=None):
        card = self.get_object()
        card.is_frozen = False
        card.save(update_fields=["is_frozen", "updated_at"])
        return Response(self.get_serializer(card).data)

    @action(detail=True, methods=["post"])
    def fund(self, request, pk=None):
        card = self.get_object()
        if card.is_frozen:
            raise ValidationError({"amount": "Unfreeze the card before funding."})

        amount = request.data.get("amount")
        transaction_pin = request.data.get("transaction_pin", "")

        if amount is None:
            raise ValidationError({"amount": "This field is required."})
        try:
            amount = Decimal(str(amount))
        except Exception as exc:
            raise ValidationError({"amount": "Invalid amount."}) from exc

        if amount < MIN_CARD_FUND_AMOUNT:
            raise ValidationError({"amount": f"Minimum fund amount is ${MIN_CARD_FUND_AMOUNT}."})

        user = request.user
        if not user.has_transaction_pin:
            raise ValidationError(
                {"transaction_pin": "Set a transaction PIN before funding a card."}
            )
        if not user.check_transaction_pin(transaction_pin):
            raise ValidationError({"transaction_pin": "Incorrect transaction PIN."})

        wallet = (
            Wallet.objects.filter(user=user, currency_code="USD").first()
            or Wallet.objects.filter(user=user).first()
        )
        if not wallet or wallet.balance < amount:
            raise ValidationError({"amount": "Insufficient wallet balance."})

        wallet.balance -= amount
        wallet.save(update_fields=["balance", "updated_at"])
        card.balance += amount
        card.save(update_fields=["balance", "updated_at"])

        return Response(self.get_serializer(card).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        card = self.get_object()
        if card.is_frozen:
            raise ValidationError({"amount": "Unfreeze the card before withdrawing."})

        amount = request.data.get("amount")
        transaction_pin = request.data.get("transaction_pin", "")

        if amount is None:
            raise ValidationError({"amount": "This field is required."})
        try:
            amount = Decimal(str(amount))
        except Exception as exc:
            raise ValidationError({"amount": "Invalid amount."}) from exc

        if amount < MIN_CARD_FUND_AMOUNT:
            raise ValidationError(
                {"amount": f"Minimum withdraw amount is ${MIN_CARD_FUND_AMOUNT}."}
            )

        user = request.user
        if not user.has_transaction_pin:
            raise ValidationError(
                {"transaction_pin": "Set a transaction PIN before withdrawing."}
            )
        if not user.check_transaction_pin(transaction_pin):
            raise ValidationError({"transaction_pin": "Incorrect transaction PIN."})

        if card.balance < amount:
            raise ValidationError({"amount": "Insufficient card balance."})

        wallet = (
            Wallet.objects.filter(user=user, currency_code="USD").first()
            or Wallet.objects.filter(user=user).first()
        )
        if not wallet:
            raise ValidationError({"amount": "No wallet found."})

        card.balance -= amount
        card.save(update_fields=["balance", "updated_at"])
        wallet.balance += amount
        wallet.save(update_fields=["balance", "updated_at"])

        return Response(self.get_serializer(card).data, status=status.HTTP_200_OK)


class CardRequestViewSet(UserScopedViewSet):
    queryset = CardRequest.objects.select_related("issued_card")
    http_method_names = ["get", "head", "options", "post"]

    def get_serializer_class(self):
        if self.action == "create":
            return CardRequestCreateSerializer
        return CardRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        output = CardRequestSerializer(instance, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class CardTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CardTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = CardTransaction.objects.filter(card__user=self.request.user).select_related("card")
        card_id = self.request.query_params.get("card")
        if card_id:
            qs = qs.filter(card_id=card_id)
        return qs
