from profile.custom_permissions import IsPmOrAdmin, IsUser
from profile.token_auth import CustomTokenAuthentication
from project.models import Project
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from profile.serializers import (
    RegisterSerializer,
    UserSerializer, UpdateUserSerializer,
    AddRoleSerializer, AddUserSerializer,
    RoleSerializer,
)
from django.contrib.auth import get_user_model
from profile.utils import (
    custom_error_message,
    send_mail_forgot_password,
    generate_token,
)
from django.utils import timezone
from profile.models import Roles

User = get_user_model()
class SignUpView(APIView):
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                token, _ = Token.objects.get_or_create(user=instance)
                if _:
                    return Response({"success": "User Registered Successfully"}, status=status.HTTP_201_CREATED)
                print("error:", custom_error_message(serializer.errors))
            return Response(custom_error_message(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class SignInView(APIView):
    permission_classes = [AllowAny, ]
    def post(self, request):
        try:
            email = request.data['email']
            password = request.data['password']
            if not email or not password:
                return Response({"error": "All Fields are required"}, status=status.HTTP_400_BAD_REQUEST)
            user_instance = User.objects.get(email=email)
            if user_instance.check_password(password):
                user_instance.last_login = timezone.now()
                user_instance.save()
                token, _ = Token.objects.get_or_create(user=user_instance)
                return Response({"success": "User Successfully Loggined", "token": str(token)}, status=status.HTTP_200_OK)
            return Response({"error": "Email or password is invalid"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Email or password is invalid"}, status=status.HTTP_400_BAD_REQUEST)
        except Token.DoesNotExist:
            return Response({"error": "Token is invalid"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class GetProfile(APIView):
    authentication_classes = [CustomTokenAuthentication]
    def get(self, request):
        try:
            user = User.objects.get(pk=request.user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class GeneratePasswordResetLink(APIView):
    permission_classes = [AllowAny, ]
    def post(self, request):
        try:
            email = request.data.get('email')
            if not email:
                return Response({"error": "All Fields are required"}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=email)
            token = generate_token()
            user.reset_password_token = token
            user.is_reset_attempt = True
            user.save()
            if(send_mail_forgot_password(user.email, user.reset_password_token, user.username)):
                return Response({"success": "Email has been sent successfully", "token": user.reset_password_token}, status=status.HTTP_200_OK)
            return Response({"error": "Email Sending Error"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Email does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ResetPasswordByLink(APIView):
    permission_classes = [AllowAny, ]
    def post(self, request):
        try:
            token = request.data.get('token')
            password = request.data.get('password')
            confirm_password = request.data.get('confirm_password')
            if not token or not password or not confirm_password:
                return Response({"error": "All Fields are required"}, status=status.HTTP_400_BAD_REQUEST)
            if password != confirm_password:
                return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
            user  = User.objects.get(reset_password_token=token)
            if user.is_reset_attempt:
                user.set_password(password)
                user.reset_password_token = ''
                user.is_reset_attempt = False
                user.save()
                return Response({"success": "Password has been reset successfully"}, status=status.HTTP_200_OK)
            return Response({"error": "Token is invalid or Expired"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Token is invalid or Expired"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UpdateUserProfile(APIView):
    authentication_classes = [CustomTokenAuthentication,]
    permission_classes = [IsAuthenticated, ]
    def patch(self, request):
        try:
            user = User.objects.get(pk=request.user.id)
            serializer = UpdateUserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"success": "Data Updated Successfully"}, status=status.HTTP_200_OK)
            return Response(custom_error_message(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)})

class GetUserList(APIView):
    authentication_classes = [CustomTokenAuthentication,]
    permission_classes = [IsPmOrAdmin, ]
    def get(self, request, role=None):
        try:
            user = None
            if role=='pm':
                user = User.objects.filter(is_pm=True)
            elif role=='user':
                user = User.objects.filter(is_pm=False, is_admin=False)
            else:
                user = User.objects.filter(is_admin=False)
            serializer = UserSerializer(user, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetRoleList(APIView):
    authentication_classes = [CustomTokenAuthentication,]
    permission_classes = [IsPmOrAdmin]
    def get(self, request):
        try:
            roles = Roles.objects.all()
            serializer = RoleSerializer(roles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
