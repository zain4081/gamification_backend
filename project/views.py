from rest_framework.permissions import AllowAny
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
from profile.utils import custom_error_message
# Create your views here.

User = get_user_model()
class GetProjectList(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    pagination_class = CustomPagination

    def get(self, request, format=None):
        try:
            # Filter projects based on user role
            projects = project_models.Project.objects.all()

            if request.user.is_client:
                projects = projects.filter(client_id=request.user.id)
            elif request.user.is_user:
                projects = projects.filter(users__in=[request.user.id])
            else:
                projects = projects.filter(manager_id=request.user.id)
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
            data = request.data
            data["manager"] = request.user.id
            serializer = ProjectAddSerializer(data=data)
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
    permission_classes = (AllowAny,)
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
    permission_classes = (IsPmOrAdmin,)
    def delete(self, request, pk):
        try:
            if not pk:
                return Response({'error': 'Please Provide Project Identifier'}, status=status.HTTP_400_BAD_REQUEST)
            project = project_models.Project.objects.get(pk=pk)
            if project.manager_id != request.user.id:
                return Response({'error': "You Aren't Authorized to Perform this Action"}, status=status.HTTP_403_FORBIDDEN)
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
            if project.manager_id != request.user.id:
                return Response({'error': "You Aren't Authorized to Perform this Action"}, status=status.HTTP_403_FORBIDDEN)
            serializer = ProjectAddSerializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({'error': 'Project does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AssignMinMax(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsPmOrAdmin, )
    def patch(self, request, project_id):
        try:
            project_instance = project_models.Project.objects.get(pk=project_id)
            if project_instance.manager.id != request.user.id:
                return Response({'error': ' You are Not Authorize to Access this Project'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = ProjectSerializer(project_instance, data=request.data, partial=True)
            if serializer.is_valid():
                instance = serializer.save()
                instance.is_start_voting = True
                instance.save()
                return Response({'data': 'Assigned Successfully'}, status=status.HTTP_200_OK)
            return Response(custom_error_message(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except project_models.Project.DoesNotExist:
            return Response({'error': 'Project Not Exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)