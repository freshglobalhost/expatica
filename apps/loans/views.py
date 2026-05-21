from rest_framework import viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from apps.core.utils import generate_reference_code
from apps.core.viewsets import UserScopedViewSet

from .models import Loan, LoanApplication, LoanProduct, LoanRepayment
from .serializers import (
    LoanApplicationSerializer,
    LoanProductSerializer,
    LoanRepaymentSerializer,
    LoanSerializer,
)


class LoanProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoanProductSerializer
    permission_classes = [IsAuthenticated]
    queryset = LoanProduct.objects.filter(is_active=True)
    lookup_field = "slug"


class LoanApplicationViewSet(UserScopedViewSet):
    serializer_class = LoanApplicationSerializer
    queryset = LoanApplication.objects.select_related("product")
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            reference_code=generate_reference_code("LA"),
            status=LoanApplication.Status.PENDING,
        )


class LoanViewSet(UserScopedViewSet):
    serializer_class = LoanSerializer
    queryset = Loan.objects.select_related("product").prefetch_related("repayments")
    http_method_names = ["get", "head", "options"]


class LoanRepaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoanRepaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LoanRepayment.objects.filter(loan__user=self.request.user).select_related("loan")
