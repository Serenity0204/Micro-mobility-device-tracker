from django.apps import AppConfig

class MicroMobilityDeviceTrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'micro_mobility_device_tracker'

    def ready(self):
        import micro_mobility_device_tracker.signals
