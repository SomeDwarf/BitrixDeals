from django.urls import path

from map.views.map import show_map

urlpatterns = [
    path('', show_map, name='map'),
]