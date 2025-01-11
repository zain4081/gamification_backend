from rest_framework import serializers
from django.contrib.auth import get_user_model
from project import models as project_models
from ckeditor.widgets import CKEditorWidget
User = get_user_model()

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = project_models.Project
        fields = '__all__'


class ProjectAddSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    class Meta:
        model = project_models.Project
        fields = ["name", "description", "manager", "users"]
        widgets = {
            'content': CKEditorWidget(),
        }