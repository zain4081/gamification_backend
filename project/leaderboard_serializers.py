from rest_framework import serializers
from collections import defaultdict

class DashboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    new_users_last_month = serializers.IntegerField()
    
    total_projects = serializers.IntegerField()
    total_requirements = serializers.IntegerField()
    
    completed_requirements = serializers.IntegerField()
    voting_complete_projects = serializers.IntegerField()
    prioritized_projects = serializers.IntegerField()
    in_progress_projects = serializers.IntegerField()
    
    monthly_projects = serializers.DictField(child=serializers.IntegerField())

class LeaderboardStatsSerializer(serializers.Serializer):
    top_users = serializers.ListField()
    leaderboard = serializers.DictField()
    points_this_month = serializers.IntegerField()
    top_contributors = serializers.ListField()
    points_trend = serializers.DictField(child=serializers.IntegerField())
