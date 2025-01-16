from rest_framework import serializers
from django.contrib.auth import get_user_model
from project import models as project_models
from ckeditor.widgets import CKEditorWidget
from datetime import datetime, timedelta
import random
from faker import Faker

from project.models import Requirement

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
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Automatically set the user
    has_voted = serializers.SerializerMethodField()  # Field to check if the user has voted
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
        extra_kwargs = {
            'user': {'read_only': True}  # Prevent user from manually setting this field
        }

    def get_assignee(self, obj):
        assignee = obj.added_by
        return {
            'fullName': assignee.username if assignee else 'Unknown',
            'avatar': '',
            'id': assignee.id if assignee else None
        }

    def get_has_voted(self, obj):
        """
        Checks if the current user has voted for this requirement.
        """
        request = self.context.get('request')
        if request:
            return obj.requirement.has_user_voted(request.user)
        return False

class AdminRequirementSerializer(serializers.ModelSerializer):
    isCompleted = serializers.BooleanField(default=lambda: random.choice([True, False]))
    dueDate = serializers.DateField(default=lambda: fake.date_between(
        start_date=datetime.today() - timedelta(days=30),
        end_date=datetime.today() + timedelta(days=30)
    ))
    tags = serializers.ListField(child=serializers.CharField(),
                                 default=lambda: [random.choice(['high', 'medium', 'low']),
                                                  random.choice(['update', 'team'])])
    assignee = serializers.SerializerMethodField()
    is_all_users_voted = serializers.SerializerMethodField
    users_status = serializers.SerializerMethodField
    score = serializers.SerializerMethodField
    class Meta:
        model = Requirement
        fields = ['id', 'name', 'description', 'dueDate', 'tags', 'assignee',
                  'is_all_users_voted', 'users_status', 'score', 'isCompleted']

    def get_is_all_users_voted(self, obj):
        return obj.is_all_users_voted
    def get_score(self, obj):
        return obj.score
    def get_users_status(self, obj):
        return obj.users_status
    def get_assignee(self, obj):
        assignee = obj.added_by
        return {
            'fullName': assignee.username if assignee else 'Unknown',
            'avatar': '',
            'id': assignee.id if assignee else None
        }

class PointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = project_models.Points
        fields = '__all__'