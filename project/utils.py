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
        return RequimentListSerializer(reqs, many=True).data, True

    except Exception as e:
        return str(e), False  # Handle unexpected errors properly
       
        
    except Exception as e:
        print("ddd", str(e))
        return str(e), False
    
def assign_indices(project_id):

    """
    Assigns a ranking index to each request in the list based on its points.
    The request with the highest points gets index 1, the next highest gets index 2, etc.
    
    Args:
        reqs (list of dict): A list where each dict contains a 'points' key.
    
    Returns:
        list of dict: The list with each request updated to include an 'index' key.
    """
    # Sort the list of requests by points in descending order
    sorted_reqs = sorted(reqs, key=lambda req: req.points, reverse=True)
    
    # Assign an index to each request based on its order in the sorted list
    for rank, req in enumerate(sorted_reqs, start=1):
        req["index"] = rank
    
    return sorted_reqs

