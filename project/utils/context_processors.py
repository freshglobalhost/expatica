from django.core.cache import cache
from django.http import HttpResponse
import time
from django.utils.deprecation import MiddlewareMixin


class SignupRateLimitMiddleware(MiddlewareMixin):
    RATE_LIMIT = 5
    TIME_WINDOW = 3600

    def process_request(self, request):
        if request.path.startswith("/accounts/signup/") and request.method == "POST":
            ip = self.get_client_ip(request)
            key = f"signup-ip:{ip}"
            now = time.time()
            history = cache.get(key, [])
            history = [t for t in history if now - t < self.TIME_WINDOW]
            if len(history) >= self.RATE_LIMIT:
                return HttpResponse("<h1>429 Too Many Requests</h1><p>Please try again later.</p>",status=429)
            history.append(now)
            cache.set(key, history, timeout=self.TIME_WINDOW)

    def get_client_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        return x_forwarded.split(",")[0] if x_forwarded else request.META.get("REMOTE_ADDR")