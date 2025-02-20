from django.template.defaultfilters import lower
from rest_framework import serializers
from django.contrib.auth import get_user_model
from profile.models import Roles

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["username", "email", "password", "is_pm"]
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'email': {'required': True},
            'username': {'required': True},
        }
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'].lower(),
            password=validated_data.get('password'),
            is_pm=validated_data.get('is_pm', True),
            roles_id=1,
        )
        return user
class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    desg = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "desg"]

    def get_role(self, obj):
        if obj.is_admin:
            return "admin"
        elif obj.is_pm:
            return "pm"
        elif obj.is_user:
            return "user"
        elif obj.is_client:
            return "client"
        else:
            return ""

    def get_desg(self, obj):
        if obj.roles:
            return obj.roles.name
        return ""


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]

class AddRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = ['name']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = "__all__"

class AddUserSerializer(serializers.ModelSerializer):
    roles_id = serializers.CharField(write_only=True)
    access = serializers.ChoiceField(choices=['is_admin', 'is_client', 'is_pm', 'is_user'], write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'roles_id', 'access']

    def create(self, validated_data):
        roles_id = validated_data.pop('roles_id', None)
        access = validated_data.pop('access', None)

        # Validate Role
        role = Roles.objects.get(id=roles_id)
        if not role:
            raise serializers.ValidationError({"roles_id": "Role does not exist."})

        # Set user permissions dynamically
        user_data = {key: False for key in ['is_admin', 'is_client', 'is_pm', 'is_user']}
        user_data[access] = True

        # Create user
        user = User.objects.create(roles_id=role.id, **validated_data, **user_data)
        user.set_password('123')
        user.save()
        return user

