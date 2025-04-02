from project.models import *
from project.serializers import *
from django.db.models import Sum


def assign_index(project_id):
    try:
        reqs = Requirement.objects.filter(project_id=project_id)
        used_indexes = set(reqs.filter(is_confirmed=True).values_list('p_index', flat=True)) 
        
        requirements = reqs.filter(is_confirmed=False).annotate(
            total_score=Sum('received_points__points')
        ).order_by('-total_score')

        if not reqs.exists():
            return "There are no requirements in the project", False

        for req in requirements:
            for i in range(1, len(reqs) + 1):
                if i not in used_indexes:
                    req.p_index = i
                    used_indexes.add(i)
                    break 

        Requirement.objects.bulk_update(requirements, ['p_index'])
        reqs = Requirement.objects.filter(project_id=project_id).order_by('p_index')
        return "ok", True

    except Exception as e:
        return str(e), False  # Handle unexpected errors properly
       
    
from django.db.models import Q

def is_in_voting(project):
    return not project.can_review and Points.objects.filter(requirement__project=project).exists() and Requirement.objects.filter(project=project).exists()

def is_finish_voting(project):
    if project.can_review:
        return False
    for req in project.requirement_set.all():
        if not req.is_all_users_voted:
            return False
    return True

def is_in_marking(project):
    return project.can_review and Requirement.objects.filter(project=project, is_marked=True).exists()

def is_finish_marking(project):
    if not project.can_review:
        return False
    return not Requirement.objects.filter(project=project, is_marked=False).exists()

def is_re_voting(project):
    return (
        not project.can_review and
        Requirement.objects.filter(project=project, is_marked=True).exists() and
        Requirement.objects.filter(project=project, is_confirmed=False).exists()
    )

def is_re_marking(project):
    return (
        project.can_review and
        Requirement.objects.filter(project=project, is_marked=True).exists() and
        Requirement.objects.filter(project=project, is_confirmed=False).exists()
    )

def is_prioritized(project):
    return not Requirement.objects.filter(project=project, is_confirmed=False).exists() and Requirement.objects.filter(project=project).exists()

def is_user_in_progress(project, user):
    return Points.objects.filter(requirement__project=project, user=user).exists()

def is_user_finished(project, user):
    reqs = project.requirement_set.all()
    for req in reqs:
        if not req.has_user_voted(user) or not req.is_confirmed:
            return False
    return True

def is_started(project):
    return not project.can_review and not Points.objects.filter(requirement__project=project).exists()



def is_sended_to_client(project):
    if not project.can_review:
        return False
    for req in project.requirement_set.all():
        if not req.is_all_users_voted:
            return False
    return True


def is_sended_to_developers(project):
    return not project.can_review and not Requirement.objects.filter(project=project, is_marked=False).exists()




def is_client_in_progress(project, user):
    return Requirement.objects.filter(project=project, added_by=user, is_marked=True).exists()

def is_client_finished(project, user):
    reqs = Requirement.objects.filter(project=project, added_by=user)
    return reqs.exists() and not reqs.filter(Q(is_marked=False) | Q(is_confirmed=False)).exists()



