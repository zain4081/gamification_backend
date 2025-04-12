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
    voting_status = serializers.SerializerMethodField()
    marking_status = serializers.SerializerMethodField()
    class Meta:
        model = project_models.Project
        fields = '__all__'
    
    def get_voting_status(self, obj):
        requirments = Requirement.objects.filter(project_id=obj.id)
        if requirments.count() == 0:
            return False
        users = obj.users.all()
        for req in requirments:
            if set(users) <= set(User.objects.filter(given_points__requirement=req)):
                if requirments[len(requirments)-1] == req:
                    return True
                continue
            return False
        
    def get_marking_status(self, obj):
        requirments = Requirement.objects.filter(project_id=obj.id)
        mark_req = requirments.filter(is_marked=True)

        print(f"req count {requirments.count()}, marked count {mark_req.count()}")
        if requirments.count() == mark_req.count():
            return True
        return False

class ProjectAddSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    class Meta:
        model = project_models.Project
        fields = ["name", "description", "client", "manager", "users"]
        widgets = {
            'content': CKEditorWidget(),
        }

class RequirementsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Automatically set the user
    has_voted = serializers.SerializerMethodField()  # Field to check if the user has voted
    min_points = serializers.SerializerMethodField()
    max_points = serializers.SerializerMethodField()

    class Meta:
        model = project_models.Requirement
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}  # Prevent user from manually setting this field
        }

    def get_has_voted(self, obj):
        """
        Checks if the current user has voted for this requirement.
        """
        request = self.context.get('request')
        if request:
            return obj.has_user_voted(request)
        return False

    def get_min_points(self, obj):
        return obj.project.min_points

    def get_max_points(self, obj):
        return obj.project.max_points

class AdminRequirementSerializer(serializers.ModelSerializer):
    is_all_users_voted = serializers.SerializerMethodField()
    users_status = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    class Meta:
        model = Requirement
        fields = ['id', 'name', 'description',
                  'is_all_users_voted', 'users_status', 'score']

    def get_is_all_users_voted(self, obj):
        return obj.is_all_users_voted
    def get_score(self, obj):
        return obj.score
    def get_users_status(self, obj):
        return obj.users_status
    def get_is_reviewed(self,obj):
        return obj.is_reviewed

class PointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = project_models.Points
        fields = '__all__'

class RequimentListSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()

    class Meta:
        model = project_models.Requirement
        fields = '__all__'

    def get_score(self, obj):
        return obj.score


class ClientRequirementsSerializer(serializers.ModelSerializer):
    has_form = serializers.SerializerMethodField()  # Field to check if the user has voted

    class Meta:
        model = project_models.Requirement
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }
    
    def get_has_form(self, obj):
        return True
