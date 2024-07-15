from django.apps import AppConfig


class PetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pets'

    def ready(self) -> None:
        from pets.serializers.serializer_registry import register_serializers
        register_serializers()
        return super().ready()
