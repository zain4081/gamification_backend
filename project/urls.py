from django.urls import path
from project import views as project_views
from project import requirement_views
from project import points_views

urlpatterns = [
    path('list/', project_views.GetProjectList.as_view(), name='project-list'),
    path('add/', project_views.AddProject.as_view(), name='project-add'),
    path('<int:pk>/', project_views.GetProjectDetail.as_view(), name='project-detail'),
    path('delete/<int:pk>/', project_views.DeleteProject.as_view(), name='project-delete'),
    path('update/<int:pk>/', project_views.UpdateProject.as_view(), name='project-update'),
    path('<int:project_id>/AssignMinMax/', project_views.AssignMinMax.as_view(), name='assign_minmax'),
    path('<int:project_id>/review/', project_views.RequestForReview.as_view(), name='assign_minmax'),
#   ------------------------------------Requirements------------------------------------------------------
    path('<int:project_id>/requirement/add/', requirement_views.AddRequirementView.as_view(), name='requirement-add'),
    path('<int:project_id>/requirements/', requirement_views.GetProjectRequirementList.as_view(),
         name='requirement-list'),
    path('requirement/<int:requirment_id>/update/', requirement_views.UpdateProjectRequirement.as_view(),
         name='requirment-update'),
    path('requirement/<int:requirment_id>/delete/', requirement_views.DeleteProjectRequirement.as_view(),
         name="requirement-delete"),
    path('requirement/<int:requirment_id>/mark/<int:confirmed>/', requirement_views.MarkRequirmentStatus.as_view(),
         name='requirement-mark'),
#   ----------------------------------Points-----------------------------------------------------------
    path('giveVote/<int:requirement_id>/', points_views.UserAddPoints.as_view(), name="add-points"),
]

