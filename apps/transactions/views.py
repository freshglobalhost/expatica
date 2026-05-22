from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.core.utils import generate_reference_code
from apps.core.viewsets import UserScopedViewSet
from apps.transactions.crypto_assets import CRYPTO_ASSETS

from .models import Transaction
from .serializers import (
    CryptoDepositCreateSerializer,
    LocalDepositCreateSerializer,
    TransactionSerializer,
)


class TransactionViewSet(UserScopedViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    http_method_names = ["get", "head", "options", "post"]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == "crypto_deposit":
            return CryptoDepositCreateSerializer
        if self.action == "local_deposit":
            return LocalDepositCreateSerializer
        return TransactionSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            reference_code=generate_reference_code("TX"),
            status=Transaction.Status.PENDING,
        )

    @action(detail=False, methods=["get"], url_path="crypto-assets")
    def crypto_assets(self, request):
        return Response(CRYPTO_ASSETS)

    @action(detail=False, methods=["post"], url_path="crypto-deposit")
    def crypto_deposit(self, request):
        serializer = CryptoDepositCreateSerializer(
            data=request.data,
            context={"request": request, "reference_code": generate_reference_code("CD")},
        )
        serializer.is_valid(raise_exception=True)
        deposit = serializer.save()
        return Response(
            TransactionSerializer(deposit, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="local-deposit")
    def local_deposit(self, request):
        serializer = LocalDepositCreateSerializer(
            data=request.data,
            context={"request": request, "reference_code": generate_reference_code("LD")},
        )
        serializer.is_valid(raise_exception=True)
        deposit = serializer.save()
        return Response(
            TransactionSerializer(deposit, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
