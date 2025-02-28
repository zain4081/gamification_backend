from django.db import models
from django.contrib.auth import get_user_model
from profile.models import TimeStampedModel
from ckeditor.fields import RichTextField
User = get_user_model()

class Project(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = RichTextField()
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_manager')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_client')
    users = models.ManyToManyField(User, related_name='project_users')
    is_start_voting = models.BooleanField(default=True)
    is_finish_voting = models.BooleanField(default=True)
    min_points = models.PositiveIntegerField(default=0)
    max_points = models.PositiveIntegerField(default=10)
    can_review = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Requirement(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_confirmed = models.BooleanField(default=False)
    is_marked = models.BooleanField(default=False)
    p_index = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return self.name
    @property
    def is_all_users_voted(self):
        """
        Checks if all users of the project have given points for this requirement.
        """
        project_users = self.project.users.all()
        voters = User.objects.filter(given_points__requirement=self)
        return set(project_users) <= set(voters)

    @property
    def users_status(self):
        project_users = self.project.users.all()
        voters = User.objects.filter(given_points__requirement=self)
        return {
            'all': project_users.count(),
            'voted': voters.count(),
        }
    @property
    def score(self):
        return self.received_points.aggregate(total=models.Sum('points'))['total'] or 0

    def has_user_voted(self, user):
        """
        Checks if a specific user has voted for this requirement.
        """
        return self.received_points.filter(user_id=user).exists()

class Points(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_points")
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, related_name="received_points")
    points = models.PositiveIntegerField()
    class Meta:
        unique_together = ('user', 'requirement')  # Prevents duplicate points from the same user for the same requirement

    def __str__(self):
        return f"{self.points} points by {self.user} for {self.requirement}"
