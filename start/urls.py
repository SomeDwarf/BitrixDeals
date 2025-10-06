from django.urls import path

from start.views.start import start, reload_start

urlpatterns = [
    path('', start),
    path('reload_start/', reload_start, name='reload_start'),
]