from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from profile.token_auth import CustomTokenAuthentication
from profile.custom_permissions import IsSelf, IsPmOrAdmin, IsAdmin
from profile.utils import custom_error_message
from project import models as project_models
from project.serializers import ProjectSerializer, ProjectAddSerializer, RequirementsSerializer, PointsSerializer
from profile.CustomPagination import CustomPagination

# try:
# except Exception as e:
#     return Response({"error", str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

User = get_user_model()
class UserAddPoints(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (AllowAny, )

    def post(self, request, requirement_id):
        try:
            points = int(request.data.get('points'))
            if not points:
                return Response({"error": "Please Enter Points"}, status=status.HTTP_400_BAD_REQUEST)
            requirement = project_models.Requirement.objects.get(pk=requirement_id)
            user = User.objects.get(pk=request.user.id)
            if not requirement.project.is_start_voting:
                return Response({"error": "Voting is Not Started yet"}, status=status.HTTP_400_BAD_REQUEST)
            if requirement.project.max_points >= points >= requirement.project.min_points:
                data = {
                    "points": points,
                    "user": user.id,
                    "requirement": requirement.id
                }
                serializer = PointsSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                print(serializer.errors)
                return Response(custom_error_message(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Points can't Exceed Limit"}, status=status.HTTP_400_BAD_REQUEST)

        except project_models.Requirement.DoesNotExist:
            return Response({"error": "Requirement Not Exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
