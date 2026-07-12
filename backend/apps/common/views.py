from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from config.celery import app as celery_app


class HealthView(APIView):
    """Liveness/readiness check: verifies DB and broker connectivity.

    Uses the plain JSON renderer (not the app envelope) so orchestrators and the
    frontend probe get a stable, unwrapped payload.
    """

    permission_classes = [AllowAny]
    authentication_classes: list = []
    renderer_classes = [JSONRenderer]

    @extend_schema(responses={200: None, 503: None})
    def get(self, request: Request) -> Response:
        checks = {"db": self._check_db(), "broker": self._check_broker()}
        ok = all(checks.values())
        return Response(
            {"status": "ok" if ok else "degraded", "checks": checks},
            status=status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    @staticmethod
    def _check_db() -> bool:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception:
            return False

    @staticmethod
    def _check_broker() -> bool:
        try:
            conn = celery_app.connection()
            conn.ensure_connection(max_retries=1, timeout=2)
            conn.release()
            return True
        except Exception:
            return False
