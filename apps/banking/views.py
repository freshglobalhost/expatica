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


class TransferMethodViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransferMethodSerializer
    permission_classes = [IsAuthenticated]
    queryset = TransferMethod.objects.filter(is_active=True)
    lookup_field = "slug"


class TransferViewSet(UserScopedViewSet):
    queryset = Transfer.objects.select_related("method")

    def get_serializer_class(self):
        if self.action == "create":
            return TransferCreateSerializer
        return TransferSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == "create":
            context["reference_code"] = generate_reference_code("TR")
        return context

    def perform_create(self, serializer):
        serializer.save()
