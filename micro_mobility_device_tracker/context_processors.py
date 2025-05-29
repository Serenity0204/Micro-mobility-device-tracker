from .views import is_locked

def monitoring_status(request):
    return {
        'monitoring_active': is_locked()
    }
