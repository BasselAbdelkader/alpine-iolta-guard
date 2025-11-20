"""
Health Check Endpoint for IOLTA Guard
Provides system status for monitoring and load balancers
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
import datetime


@api_view(['GET'])
@permission_classes([AllowAny])  # Health check should be publicly accessible
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers

    Returns 200 OK if system is healthy
    Returns 503 Service Unavailable if system has issues

    Usage:
        GET /api/health/

    Response:
        {
            "status": "healthy",
            "timestamp": "2025-10-13T12:00:00Z",
            "checks": {
                "database": "ok",
                "cache": "ok"
            }
        }
    """
    checks = {}
    overall_status = "healthy"
    http_status = status.HTTP_200_OK

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        overall_status = "unhealthy"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    # Check cache
    try:
        cache_key = "health_check_test"
        cache.set(cache_key, "test", 30)
        cache_value = cache.get(cache_key)
        if cache_value == "test":
            checks["cache"] = "ok"
        else:
            checks["cache"] = "error: cache read/write failed"
            overall_status = "degraded"
    except Exception as e:
        checks["cache"] = f"error: {str(e)}"
        overall_status = "degraded"

    return Response({
        "status": overall_status,
        "timestamp": datetime.datetime.now().isoformat(),
        "checks": checks
    }, status=http_status)


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness(request):
    """
    Readiness probe for Kubernetes/Docker deployments

    Returns 200 OK if the service is ready to accept traffic
    Returns 503 if the service is starting up or shutting down
    """
    # Check if database is accessible
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return Response({"status": "ready"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": "not ready",
            "error": str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness(request):
    """
    Liveness probe for Kubernetes/Docker deployments

    Returns 200 OK if the service is alive (even if not ready)
    Only returns error if the process itself is dead/crashed
    """
    return Response({"status": "alive"}, status=status.HTTP_200_OK)
