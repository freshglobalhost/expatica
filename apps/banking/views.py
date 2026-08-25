from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.utils import generate_reference_code
from apps.core.viewsets import UserScopedViewSet

from .models import Transfer, TransferMethod
from .serializers import (
    TransferCreateSerializer,
    TransferMethodSerializer,
    TransferSerializer,
)

WITHDRAWAL_REF_PREFIX = "WD-"


class TransferMethodViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransferMethodSerializer
    permission_classes = [IsAuthenticated]
    queryset = TransferMethod.objects.filter(is_active=True)
    lookup_field = "slug"


class TransferViewSet(UserScopedViewSet):
    queryset = Transfer.objects.select_related("method").exclude(
        reference_code__startswith=WITHDRAWAL_REF_PREFIX
    )

    def get_serializer_class(self):
        if self.action == "create":
            return TransferCreateSerializer
        return TransferSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == "create":
            context["reference_code"] = generate_reference_code("TR")
            context["is_withdrawal"] = False
        return context

    def perform_create(self, serializer):
        serializer.save()


class WithdrawalViewSet(UserScopedViewSet):
    queryset = Transfer.objects.select_related("method").filter(
        reference_code__startswith=WITHDRAWAL_REF_PREFIX
    )

    def get_serializer_class(self):
        if self.action == "create":
            return TransferCreateSerializer
        return TransferSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == "create":
            context["reference_code"] = generate_reference_code("WD")
            context["is_withdrawal"] = True
        return context

    def perform_create(self, serializer):
        serializer.save()
