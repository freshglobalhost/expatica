from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.viewsets import UserScopedViewSet

from .models import InvestmentPlan, UserInvestment
from .serializers import (
    InvestmentPlanSerializer,
    UserInvestmentCreateSerializer,
    UserInvestmentSerializer,
)


class InvestmentPlanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvestmentPlanSerializer
    permission_classes = [IsAuthenticated]
    queryset = InvestmentPlan.objects.filter(is_active=True)
    lookup_field = "slug"


class UserInvestmentViewSet(UserScopedViewSet):
    queryset = UserInvestment.objects.select_related("plan")
    http_method_names = ["get", "head", "options", "post"]

    def get_serializer_class(self):
        if self.action == "create":
            return UserInvestmentCreateSerializer
        return UserInvestmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        investment = serializer.save()
        output = UserInvestmentSerializer(investment, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)
