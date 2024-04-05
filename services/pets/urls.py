from django.urls import path
from .views import ModelFieldsView, PetsModelNamesView


urlpatterns = [
    path('modules/fields_list/', ModelFieldsView.as_view(),
         name='models_fields_list'),
    path('modules/list/', PetsModelNamesView.as_view(), name='models_list')
]
