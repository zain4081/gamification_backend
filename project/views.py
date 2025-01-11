from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from profile.token_auth import CustomTokenAuthentication
from profile.custom_permissions import IsSelf, IsPmOrAdmin, IsAdmin
from project import models as project_models
from project.models import Project
from project.serializers import ProjectSerializer, ProjectAddSerializer
from profile.CustomPagination import CustomPagination
# Create your views here.

User = get_user_model()
class GetProjectList(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    pagination_class = CustomPagination

    def get(self, request, format=None):
        try:
            # Filter projects based on user role
            projects = project_models.Project.objects.all()
            if request.user.is_admin:
                projects = projects
            elif request.user.is_pm:
                projects = projects.filter(is_pm=True)
            else:
                projects = projects.filter(users__in=[request.user.id])

            # Pagination handling
            paginator = CustomPagination()
            paginated_projects = paginator.paginate_queryset(projects, request)
            serializer = ProjectSerializer(paginated_projects, many=True)

            # Return paginated response
            paginated_response = paginator.get_paginated_response(serializer.data)
            print(paginated_response)
            return paginated_response

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST)

class AddProject(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsPmOrAdmin,)
    def post(self, request, format=None):
        try:
            print()
            serializer = ProjectAddSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GetProjectDetail(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsPmOrAdmin, IsSelf)
    def get(self, request, pk):
        try:
            if not pk:
                return Response({'error': 'Please Provide Project Identifier'}, status=status.HTTP_400_BAD_REQUEST)
            project = project_models.Project.objects.get(pk=pk)
            serializer = ProjectSerializer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DeleteProject(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAdmin,)
    def delete(self, request, pk):
        try:
            if not pk:
                return Response({'error': 'Please Provide Project Identifier'}, status=status.HTTP_400_BAD_REQUEST)
            project = project_models.Project.objects.get(pk=pk)
            count, deleteion = project.delete()
            print(deleteion)
            print(count)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UpdateProject(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsPmOrAdmin,)
    def patch(self, request, pk):
        try:
            if not pk:
                return Response({'error': 'Please Provide Project Identifier'}, status=status.HTTP_400_BAD_REQUEST)
            project = project_models.Project.objects.get(pk=pk)
            serializer = ProjectAddSerializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
