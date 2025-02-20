from profile.custom_permissions import IsPmOrAdmin, IsUser
from profile.token_auth import CustomTokenAuthentication
from project.models import Project
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from profile.serializers import (
    RegisterSerializer,
    UserSerializer, UpdateUserSerializer,
    AddRoleSerializer, AddUserSerializer
)
from django.contrib.auth import get_user_model
from profile.utils import (
    custom_error_message,
    send_mail_forgot_password,
    generate_token,
)
from profile.CustomPagination import CustomPagination
from django.utils import timezone
from profile.models import Roles

User = get_user_model()

class AdminAddRole(APIView):
    authentication_classes = [CustomTokenAuthentication,]
    permission_classes = [IsPmOrAdmin]

    def post(self, request):
        try:
            name = request.data.get("name")
            if not name:
                return Response({"error": "Please Provide Role Name Field"}, status=status.HTTP_400_BAD_REQUEST)
            data = {
                "name": name,
            }
            serializer = AddRoleSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"success": "Role Added Successfully"}, status=status.HTTP_201_CREATED)
            return Response(custom_error_message(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AdminPmAddUser(APIView):
    authentication_classes = [CustomTokenAuthentication,]
    permission_classes = [IsPmOrAdmin,]
    def post(self, request):
        try:
            serializer = AddUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"success": "User Added Successfully"}, status=status.HTTP_201_CREATED)
            return Response(custom_error_message(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AdminPmUserList(APIView):
    authentication_classes = [CustomTokenAuthentication,]
    permission_class = (IsPmOrAdmin, IsUser)

    def get(self, request):
        try:
            users_list = User.objects.filter(is_admin=False)
            if request.user.is_user:
                projects = Project.objects.filter(users=request.user)
                mutual_users = set()
                for project in projects:
                    mutual_users.update(project.users.all())
                mutual_users.discard(request.user)
                users_list = mutual_users
            serializer = UserSerializer(users_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AdminPmUserListPaginated(APIView):
    authentication_classes = [CustomTokenAuthentication,]
    permission_class = (IsPmOrAdmin, IsUser)
    pagination_class = CustomPagination
 
    def get(self, request):
        try:
            users_list = User.objects.filter(is_pm=False, is_admin=False)
            role = request.query_params.get('role', None)
            q = request.query_params.get('q', None)
            if role:
                users_list = users_list.filter(roles_id=role)
            if q:
                users_list = users_list.filter(
                    Q(username__icontains=q) | Q(roles__name__icontains=q) | Q(email__icontains=q)
                )
            if request.user.is_user:
                projects = Project.objects.filter(users=request.user)
                mutual_users = set()
                for project in projects:
                    mutual_users.update(project.users.all())
                mutual_users.discard(request.user)
                users_list = mutual_users
            serializer = UserSerializer(users_list, many=True)
            paginator = self.pagination_class()
            paginated_users = paginator.paginate_queryset(users_list, request)
            
            serializer = UserSerializer(paginated_users, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DeleteUser(APIView):
    authentication_classes = [CustomTokenAuthentication,]
    permission_classes = [IsPmOrAdmin, ]

    def delete(self, request, user_id):
        try:
            if not user_id:
                return Response({"error":"Please Provide User Valid Identifier"}, status=status.HTTP_400_BAD_REQUEST)
            user_obj = User.objects.get(pk=user_id)
            del_count, _ =user_obj.delete()
            if del_count > 0:
                return Response({"success":"User Deleted Successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error":"User doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)