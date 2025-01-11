from django.urls import path
from project import views as project_views

urlpatterns = [
    path('list/', project_views.GetProjectList.as_view(), name='project-list'),
    path('add/', project_views.AddProject.as_view(), name='project-add'),
    path('<int:pk>/', project_views.GetProjectDetail.as_view(), name='project-detail'),
    path('delete/<int:pk>/', project_views.DeleteProject.as_view(), name='project-delete'),
    path('update/<int:pk>/', project_views.UpdateProject.as_view(), name='project-update'),
]
