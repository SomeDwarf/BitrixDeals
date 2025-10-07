from django.urls import path

from items_qr.views.items_qr import search

urlpatterns = [
    path('', search, name='items_qr'),
]