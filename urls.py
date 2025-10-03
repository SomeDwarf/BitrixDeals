from django.urls import path
from start.views.start import start

urlpatterns = [
    path('', start),
]