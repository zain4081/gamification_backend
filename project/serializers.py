from rest_framework import serializers
from django.contrib.auth import get_user_model
from project import models as project_models
from ckeditor.widgets import CKEditorWidget
from datetime import datetime, timedelta
import random
from faker import Faker

User = get_user_model()
fake = Faker()

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

class RequirementsSerializer(serializers.ModelSerializer):
    isCompleted = serializers.BooleanField(default=lambda: random.choice([True, False]))
    dueDate = serializers.DateField(default=lambda: fake.date_between(
        start_date=datetime.today() - timedelta(days=30),
        end_date=datetime.today() + timedelta(days=30)
    ))
    tags = serializers.ListField(child=serializers.CharField(),
                                 default=lambda: [random.choice(['high', 'medium', 'low']),
                                                  random.choice(['update', 'team'])])
    assignee = serializers.SerializerMethodField()
    class Meta:
        model = project_models.Requirement
        fields = '__all__'

    def get_assignee(self, obj):
        assignee = obj.added_by
        return {
            'fullName': assignee.username if assignee else 'Unknown',
            'avatar': '',
            'id': assignee.id if assignee else None
        }