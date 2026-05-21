from rest_framework import serializers

from .models import Loan, LoanApplication, LoanProduct, LoanRepayment


class LoanProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanProduct
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "minimum_amount",
            "maximum_amount",
            "minimum_interest_rate",
            "available_terms_months",
            "is_active",
        ]


class LoanApplicationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_slug = serializers.CharField(source="product.slug", read_only=True)

    class Meta:
        model = LoanApplication
        fields = [
            "id",
            "product",
            "product_name",
            "product_slug",
            "reference_code",
            "requested_amount",
            "term_months",
            "purpose",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "employer",
            "job_title",
            "annual_income",
            "employment_years",
            "id_document",
            "income_document",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reference_code", "status", "created_at", "updated_at"]

    def validate(self, attrs):
        if self.instance is None:
            required = [
                "product",
                "requested_amount",
                "term_months",
                "purpose",
                "first_name",
                "last_name",
                "email",
                "phone",
                "address",
                "employer",
                "job_title",
                "annual_income",
                "employment_years",
                "id_document",
                "income_document",
            ]
            missing = [f for f in required if not attrs.get(f)]
            if missing:
                raise serializers.ValidationError(
                    {f: "This field is required." for f in missing}
                )
        return attrs


class LoanRepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRepayment
        fields = ["id", "amount", "due_on", "paid_on", "created_at"]
        read_only_fields = ["id", "paid_on", "created_at"]


class LoanSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    repayments = LoanRepaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Loan
        fields = [
            "id",
            "product",
            "product_name",
            "reference_code",
            "principal_amount",
            "interest_rate",
            "term_months",
            "status",
            "applied_on",
            "disbursed_on",
            "outstanding_balance",
            "repayments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
