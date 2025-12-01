from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class LoginAPIView(APIView):
    """
    Session-based login (no JWT required)
    """
    permission_classes = []  # Allow unauthenticated access

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'detail': 'Username and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({
                'success': True,
                'username': user.username,
                'full_name': user.get_full_name() or user.username
            })
        else:
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutAPIView(APIView):
    """
    Session-based logout
    """
    def post(self, request):
        logout(request)
        return Response({'success': True})


class CheckAuthAPIView(APIView):
    """
    Check if user is authenticated
    """
    permission_classes = []

    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'authenticated': True,
                'username': request.user.username,
                'full_name': request.user.get_full_name() or request.user.username
            })
        else:
            return Response({
                'authenticated': False
            })
