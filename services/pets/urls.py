from django.urls import path
from .views import ModelFieldsView


urlpatterns = [
    path('modules/fields_list/', ModelFieldsView.as_view(),
         name='models_list'),

]
