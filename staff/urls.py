from django.urls import path

from staff.views.staff import table

urlpatterns = [
    path('', table, name='staff'),
]