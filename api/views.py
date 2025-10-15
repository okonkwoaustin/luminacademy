from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserSerializer, TokenObtainPairSerializer, RegisterSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer