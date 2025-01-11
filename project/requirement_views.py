from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from profile.token_auth import CustomTokenAuthentication
from profile.custom_permissions import IsSelf, IsPmOrAdmin, IsAdmin
from project import models as project_models
from project.models import Project
from project.serializers import ProjectSerializer, ProjectAddSerializer, RequirementsSerializer
from profile.CustomPagination import CustomPagination

class AddRequirementView(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    def post(self, request, project_id):
        try:
            if not project_id:
                return Response(
                    {"error": "Please Provide Project Identifier"},
                    status=status.HTTP_400_BAD_REQUEST)
            if not request.data['name']:
                return Response({"error": "Please Provide Requirement Name"},
                                status=status.HTTP_400_BAD_REQUEST)
            project = project_models.Project.objects.get(pk=project_id)
            requirement_instance = project_models.Requirement.objects.create(
                project_id=project.id,
                added_by=request.user,
            )
            serializer = RequirementsSerializer(requirement_instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response(
                {"error": "Project Does Not Exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class GetProjectRequirementList(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    def get(self, request, project_id):
        try:
            if not project_id:
                return Response({"error": "Please Provide Project Identifier"},
                                status=status.HTTP_400_BAD_REQUEST)
            project = project_models.Project.objects.get(pk=project_id)
            requirements = project.requirements.filter(project_id=project.id)
            serializer = RequirementsSerializer(requirements, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response(
                {"error": "Project Does Not Exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

