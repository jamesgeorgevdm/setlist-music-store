"""
Django App Configuration for the SetList app.

This class ensures that application signals are loaded at startup.
"""

from django.apps import AppConfig


class SetListConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "set_list"

    def ready(self):
        """
        Import signal handlers to enable model-based triggers (e.g. post-save logic).
        """
        import set_list.signals  
