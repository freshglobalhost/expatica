from rest_framework import serializers

from .models import FAQ, HelpArticle, HelpCategory, SupportTicket, TicketMessage


class HelpCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpCategory
        fields = ["id", "slug", "name", "display_order"]


class HelpArticleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = HelpArticle
        fields = [
            "id",
            "category",
            "category_name",
            "slug",
            "title",
            "body",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class FAQSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, allow_null=True)

    class Meta:
        model = FAQ
        fields = [
            "id",
            "question",
            "answer",
            "category",
            "category_name",
            "display_order",
            "is_published",
        ]
        read_only_fields = fields


class TicketMessageSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source="author.email", read_only=True)

    class Meta:
        model = TicketMessage
        fields = [
            "id",
            "author",
            "author_email",
            "message_body",
            "is_staff_reply",
            "created_at",
        ]
        read_only_fields = ["id", "author", "author_email", "is_staff_reply", "created_at"]


class SupportTicketCreateSerializer(serializers.ModelSerializer):
    message_body = serializers.CharField(write_only=True)

    class Meta:
        model = SupportTicket
        fields = ["subject", "priority", "message_body"]


class SupportTicketSerializer(serializers.ModelSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta:
        model = SupportTicket
        fields = [
            "id",
            "reference_code",
            "subject",
            "status",
            "priority",
            "messages",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reference_code", "status", "messages", "created_at", "updated_at"]


class TicketMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = ["message_body"]
