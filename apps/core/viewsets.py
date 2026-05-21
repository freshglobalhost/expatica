from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class UserScopedViewSet(viewsets.ModelViewSet):
    """Filter queryset to the authenticated user; set user on create."""

    permission_classes = [IsAuthenticated]
    user_field = "user"

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        return queryset.filter(**{self.user_field: self.request.user})

    def perform_create(self, serializer):
        serializer.save(**{self.user_field: self.request.user})
