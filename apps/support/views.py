from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.core.utils import generate_reference_code
from apps.core.viewsets import UserScopedViewSet

from .models import FAQ, HelpArticle, HelpCategory, SupportTicket, TicketMessage
from .serializers import (
    FAQSerializer,
    HelpArticleSerializer,
    HelpCategorySerializer,
    SupportTicketCreateSerializer,
    SupportTicketSerializer,
    TicketMessageCreateSerializer,
    TicketMessageSerializer,
)


class HelpCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HelpCategorySerializer
    permission_classes = [AllowAny]
    queryset = HelpCategory.objects.all()
    lookup_field = "slug"


class HelpArticleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HelpArticleSerializer
    permission_classes = [AllowAny]
    queryset = HelpArticle.objects.filter(is_published=True).select_related("category")
    lookup_field = "slug"


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    queryset = FAQ.objects.filter(is_published=True).select_related("category")


class SupportTicketViewSet(UserScopedViewSet):
    queryset = SupportTicket.objects.prefetch_related("messages")

    def get_serializer_class(self):
        if self.action == "create":
            return SupportTicketCreateSerializer
        return SupportTicketSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message_body = serializer.validated_data.pop("message_body")
        ticket = serializer.save(
            user=request.user,
            reference_code=generate_reference_code("TKT"),
            status=SupportTicket.Status.OPEN,
        )
        TicketMessage.objects.create(
            ticket=ticket,
            author=request.user,
            message_body=message_body,
        )
        output = SupportTicketSerializer(ticket, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], serializer_class=TicketMessageCreateSerializer)
    def reply(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = TicketMessage.objects.create(
            ticket=ticket,
            author=request.user,
            message_body=serializer.validated_data["message_body"],
            is_staff_reply=False,
        )
        return Response(
            TicketMessageSerializer(message, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
