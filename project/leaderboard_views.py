from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Sum, Q
from django.core.cache import cache
from collections import defaultdict
from datetime import timedelta

from profile.custom_permissions import IsSelf, IsPmOrAdmin, IsAdmin, IsUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Requirement, Points
from .leaderboard_serializers import DashboardStatsSerializer, LeaderboardStatsSerializer
from profile.token_auth import CustomTokenAuthentication
from .utils import *
from profile.models import CustomUser

User = get_user_model()

class DashboardView(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = [IsPmOrAdmin]

    def get(self, request):
        try:

            today = timezone.now()
            last_month = today - timedelta(days=30)

            total_users = User.objects.count()
            active_users = User.objects.filter(last_login__gte=last_month).count()
            new_users = User.objects.filter(date_joined__gte=last_month).count()

            total_projects = Project.objects.count()
            total_requirements = Requirement.objects.count()
            completed_requirements = Requirement.objects.filter(is_confirmed=True).count()

            # **Project Categorization**
            voting_complete_projects = 0
            prioritized_projects = 0
            in_progress_projects = 0

            project_user_stats = {}
            for project in Project.objects.all():
                requirements = project.requirement_set.all()
                total_project_users = project.users.count()
                users_voted = User.objects.filter(given_points__requirement__project=project).distinct().count()

                project_user_stats[project.id] = {
                    "total_users": total_project_users,
                    "users_voted": users_voted,
                }

                if not requirements.exists():
                    continue

                total_voted = all(req.is_all_users_voted for req in requirements)
                all_confirmed = all(req.is_confirmed for req in requirements)
                all_marked = all(req.is_marked for req in requirements)
                some_unconfirmed = any(not req.is_confirmed for req in requirements)

                if total_voted:
                    voting_complete_projects += 1
                if all_confirmed:
                    prioritized_projects += 1
                if all_marked and some_unconfirmed:
                    in_progress_projects += 1

            # Monthly projects count
            monthly_projects = defaultdict(int)
            for proj in Project.objects.filter(created_at__year=today.year):
                month_name = proj.created_at.strftime('%B')
                monthly_projects[month_name] += 1

            data = {
                "total_users": total_users,
                "active_users": active_users,
                "new_users_last_month": new_users,
                "total_projects": total_projects,
                "total_requirements": total_requirements,
                "completed_requirements": completed_requirements,
                "voting_complete_projects": voting_complete_projects,
                "prioritized_projects": prioritized_projects,
                "in_progress_projects": in_progress_projects,
                "monthly_projects": dict(monthly_projects),
                "project_user_stats": project_user_stats,
            }

            serializer = DashboardStatsSerializer(data)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)})


class LeaderboardView(APIView):
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = [IsPmOrAdmin]

    def get(self, request):
        try:
            today = timezone.now()
            first_day_of_month = today.replace(day=1)

            # Leaderboard Data
            users = User.objects.filter(is_pm=False, is_admin=False)
            top_users = (
                users.annotate(total_points=Sum("given_points__points"))
                .order_by("-total_points")
                .values("id", "username", "total_points")[:10]
            )
            
            # Top contributors (users with the most votes this month)
            top_contributors = (
                users.filter(given_points__created_at__gte=first_day_of_month)
                .annotate(votes=Count("given_points"))
                .order_by("-votes")
                .values("id", "username", "votes")[:10]
            )
            
            # Monthly points trend
            points_trend = defaultdict(int)
            for points in Points.objects.filter(created_at__gte=first_day_of_month):
                month_name = points.created_at.strftime('%B')
                points_trend[month_name] += points.points
            
            data = {
                "top_users": list(top_users),
                "leaderboard": {user["username"]: user["total_points"] for user in top_users},
                "points_this_month": sum(user["total_points"] or 0 for user in top_users),
                "top_contributors": list(top_contributors),
                "points_trend": dict(points_trend),
            }
            
            serializer = LeaderboardStatsSerializer(data)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)})

class UserStates(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = (IsPmOrAdmin,)

    def get(self, request):
        try:
            # Filter users only once
            users = User.objects.select_related('roles').filter(is_pm=False, is_admin=False)

            # Prepare the data for each role and client count
            data = [
                {
                    "title": users.filter(roles__name='Developer').count(),
                    "subtitle": "Developer",
                    "color": "light-info",
                    "icon": "Code"
                },
                {
                    "title": users.filter(roles__name='StakeHolder').count(),
                    "subtitle": "StakeHolder",
                    "color": "light-primary",
                    "icon": "Award"
                },
                {
                    "title": users.filter(roles__name='Analyst').count(),
                    "subtitle": "Analyst",
                    "color": "light-danger",
                    "icon": "BarChart"
                },
                {
                    "title": users.filter(is_client=True).count(),
                    "subtitle": "Client",
                    "color": "light-success",
                    "icon": "UserCheck"
                },
            ]
            

            return Response(data)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class UserDashboard(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = (IsUser,)

    def get(self, request):
        try:
            assigned_projects =  Project.objects.filter(users=request.user)

            total_assigned_projects = assigned_projects.count()

            # Get the projects where the user has assigned points to all its requirements
            projects_with_all_requirements_voted = 0
            inprogress = 0

            for project in assigned_projects:
                # Check if user has assigned points to all requirements of the project
                for requirement in project.requirement_set.all():
                    if not requirement.has_user_voted(request.user):
                        inprogress += 1
                        break
                else:
                    # If the loop doesn't break, meaning user has voted for all requirements
                    projects_with_all_requirements_voted += 1
            data = {
                "assigned": total_assigned_projects,
                "remaining": inprogress,
                "completed": projects_with_all_requirements_voted
            }
            return Response({"projects": data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MyPoints(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = (IsAuthenticated)


class AdminPMDashboardAPIView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = (IsPmOrAdmin,)

    def get(self, request):
        user = request.user
        if not (user.is_admin or user.is_pm):
            return Response({"error": "Not authorized"}, status=403)

        projects = Project.objects.all()
        total_projects = projects.count()

        is_voting = finish_voting = is_marking = finish_marking = re_voting = re_marking = 0
        voted_projects = marked_projects = prioritized_projects = 0
        voted_requirements = marked_requirements = prioritized_requirements = 0

        for project in projects:
            if is_in_voting(project): is_voting += 1
            if is_finish_voting(project): finish_voting += 1
            if is_in_marking(project): is_marking += 1
            if is_finish_marking(project): finish_marking += 1
            if is_re_voting(project): re_voting += 1
            if is_re_marking(project): re_marking += 1
            if is_prioritized(project): prioritized_projects += 1

            if is_finish_voting(project):
                voted_projects += 1

            if Requirement.objects.filter(project=project, is_marked=True).exists():
                marked_projects += 1

            voted_requirements += Points.objects.filter(requirement__project=project).count()
            marked_requirements += Requirement.objects.filter(project=project, is_marked=True).count()
            prioritized_requirements += Requirement.objects.filter(project=project, is_confirmed=True).count()

        total_clients = CustomUser.objects.filter(is_client=True).count()
        total_users = CustomUser.objects.filter(is_user=True).count()

        top_users = CustomUser.objects.filter(is_user=True).order_by('-points')[:3]
        top_clients = CustomUser.objects.filter(is_client=True).order_by('-points')[:3]

        # User-wise project progress
        user_project_data = []
        users = CustomUser.objects.filter(is_user=True)
        for u in users:
            user_projects = Project.objects.filter(users=u)
            in_progress_count = 0
            finished_count = 0

            for p in user_projects:
                if is_user_finished(p, u):
                    finished_count += 1
                elif is_user_in_progress(p, u):
                    in_progress_count += 1

            user_project_data.append({
                "username": u.username,
                "points": u.points,
                "total_projects": user_projects.count(),
                "in_progress": in_progress_count,
                "finished": finished_count
            })

        return Response({
            "total_projects": total_projects,
            "is_voting": is_voting,
            "finish_voting": finish_voting,
            "is_marking": is_marking,
            "finish_marking": finish_marking,
            "re_voting": re_voting,
            "re_marking": re_marking,
            "total_voted_projects": voted_projects,
            "total_marked_projects": marked_projects,
            "total_prioritized_projects": prioritized_projects,
            "total_voted_requirements": voted_requirements,
            "total_marked_requirements": marked_requirements,
            "total_prioritized_requirements": prioritized_requirements,
            "total_clients": total_clients,
            "total_users": total_users,
            "top_users": [{"username": u.username, "points": u.points} for u in top_users],
            "top_clients": [{"username": c.username, "points": c.points} for c in top_clients],
            "user_project_status": user_project_data
        })
