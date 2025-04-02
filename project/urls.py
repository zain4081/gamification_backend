from django.urls import path
from project import views as project_views
from project import requirement_views
from project import points_views
from project import leaderboard_views

urlpatterns = [
    path('list/', project_views.GetProjectList.as_view(), name='project-list'),
    path('listw/', project_views.GetProjectListW.as_view(), name='project-list-w'),
    path('add/', project_views.AddProject.as_view(), name='project-add'),
    path('<int:pk>/', project_views.GetProjectDetail.as_view(), name='project-detail'),
    path('delete/<int:pk>/', project_views.DeleteProject.as_view(), name='project-delete'),
    path('update/<int:pk>/', project_views.UpdateProject.as_view(), name='project-update'),
    path('<int:project_id>/AssignMinMax/', project_views.AssignMinMax.as_view(), name='assign_minmax'),
    path('<int:project_id>/review/', project_views.RequestForReview.as_view(), name='assign_minmax'),
    path('<int:project_id>/report/', project_views.GenerateProjectReportView.as_view(), name='report'),
#   ------------------------------------------Requirements------------------------------------------------------------
    path('<int:project_id>/requirement/add/', requirement_views.AddRequirementView.as_view(), name='requirement-add'),
    path('<int:project_id>/requirements/', requirement_views.GetProjectRequirementList.as_view(),
         name='requirement-list'),
    path('requirement/<int:requirment_id>/update/', requirement_views.UpdateProjectRequirement.as_view(),
         name='requirment-update'),
    path('requirement/<int:requirment_id>/delete/', requirement_views.DeleteProjectRequirement.as_view(),
         name="requirement-delete"),
    path('requirement/<int:requirment_id>/mark/', requirement_views.MarkRequirmentStatus.as_view(),
         name='requirement-mark'),
#   ---------------------------------------------Points---------------------------------------------------------------
    path('giveVote/<int:requirement_id>/', points_views.UserAddPoints.as_view(), name="add-points"),


#   -------------------------------------leaderboard & Dashboard------------------------------------------------------
     path('mainleaderboard/', leaderboard_views.LeaderboardView.as_view(), name='main-leaderbarod'),
     path('maindashboard/', leaderboard_views.DashboardView.as_view(), name='main-dashboard'),
     path('userdashboard/', leaderboard_views.UserDashboard.as_view(), name='userDashbard'),
     path('userstates/', leaderboard_views.UserStates.as_view(), name='users-states'),
     path('adminDashboard/', leaderboard_views.AdminPMDashboardAPIView.as_view(), name='admin-dash')
     # path('leaderboard/<int:user_id>', leaderboard_views.LeaderboardView.as_view(), name='user-leaderbarod'),
     # path('dashboard/<int:user_id>/', leaderboard_views.DashboardView.as_view(), name='user-dashboard'),

]

