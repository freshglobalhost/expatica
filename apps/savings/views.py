from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.utils import generate_reference_code
from apps.core.viewsets import UserScopedViewSet

from .defaults import (
    ensure_default_auto_save_rules,
    ensure_default_locked_savings,
    ensure_default_savings_for_user,
)
from .models import AutoSaveRule, LockedSavingsAccount, SavingsGoal, SavingsTransaction
from .serializers import (
    AutoSaveRuleSerializer,
    LockedSavingsAccountSerializer,
    SavingsGoalSerializer,
    SavingsTransactionSerializer,
)


class SavingsGoalViewSet(UserScopedViewSet):
    serializer_class = SavingsGoalSerializer
    queryset = SavingsGoal.objects.all()


class LockedSavingsAccountViewSet(UserScopedViewSet):
    serializer_class = LockedSavingsAccountSerializer
    queryset = LockedSavingsAccount.objects.all()
    http_method_names = ["get", "head", "options", "post"]

    def list(self, request, *args, **kwargs):
        ensure_default_locked_savings(request.user)
        return super().list(request, *args, **kwargs)


class AutoSaveRuleViewSet(UserScopedViewSet):
    serializer_class = AutoSaveRuleSerializer
    queryset = AutoSaveRule.objects.all()
    http_method_names = ["get", "head", "options", "patch", "post"]

    def list(self, request, *args, **kwargs):
        ensure_default_auto_save_rules(request.user)
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["post"], url_path="bootstrap")
    def bootstrap(self, request):
        """Create default auto-save rules for the current user if none exist."""
        ensure_default_savings_for_user(request.user)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "count": len(serializer.data),
                "next": None,
                "previous": None,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class SavingsTransactionViewSet(UserScopedViewSet):
    serializer_class = SavingsTransactionSerializer
    queryset = SavingsTransaction.objects.select_related("goal")
    http_method_names = ["get", "head", "options", "post"]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            reference_code=generate_reference_code("SAV"),
        )
