from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from profile.token_auth import CustomTokenAuthentication
from profile.custom_permissions import IsSelf, IsPmOrAdmin, IsAdmin
from project import models as project_models
from project.models import Project
from project.serializers import ProjectSerializer, ProjectAddSerializer, RequirementsSerializer, \
    AdminRequirementSerializer
from profile.CustomPagination import CustomPagination

User = get_user_model()
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
                added_by_id=request.user.id,
            )
            serializer = RequirementsSerializer(requirement_instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
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
            requirements = project_models.Requirement.objects.filter(project_id=project.id, )
            serializer = RequirementsSerializer(requirements, context={'request': request.user.id}, many=True)
            if request.user.is_pm or request.user.is_admin:
                serializer = AdminRequirementSerializer(requirements, many=True)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response(
                {"error": "Project Does Not Exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateProjectRequirement(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    def patch(self, request, requirement_id):
        try:
            if not requirement_id:
                return Response({"error": "Please Provide Requirement Identifier"},
                                status=status.HTTP_400_BAD_REQUEST)
            requirement_instance = project_models.Requirement.objects.get(pk=requirement_id)
            serializer = RequirementsSerializer(requirement_instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"data": "Requirement Updated Successfully"},
                                status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except project_models.Project.DoesNotExist:
            return Response({"error": "Requirement Doen't Exist"},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Please Provide Requirement Identifier"},
                            status=status.HTTP_400_BAD_REQUEST)

class DeleteProjectRequirement(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    def delete(self, request, requirement_id):
        try:
            if not requirement_id:
                return Response({"error": "Please Provide Requirement Identifier"},
                                status=status.HTTP_400_BAD_REQUEST)
            requirement = project_models.Requirement.objects.get(pk=requirement_id)
            requirement.delete()
            return Response({"data":"Successfully Deleted"}, status=status.HTTP_204_NO_CONTENT)
        except project_models.Project.DoesNotExist:
            return Response({"error": "Requirement Doen't Exist"},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error", str(e)}, status=status.HTTP_400_BAD_REQUEST)