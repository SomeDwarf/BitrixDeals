from django.urls import path

from staff.views.staff import table, generate_calls

urlpatterns = [
    path('', table, name='staff'),
    path('generate_calls', generate_calls, name='generate_calls'),
]