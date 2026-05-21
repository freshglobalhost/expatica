from apps.core.viewsets import UserScopedViewSet

from .models import Wallet
from .serializers import WalletSerializer


class WalletViewSet(UserScopedViewSet):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()
    http_method_names = ["get", "head", "options"]
