from django.template.defaultfilters import lower
from rest_framework import serializers
from django.contrib.auth import get_user_model

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
            is_pm=validated_data.get('is_pm', False),
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
        else:
            return "user"

    def get_desg(self, obj):
        if obj.roles:
            return obj.roles.name
        return ""


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]

