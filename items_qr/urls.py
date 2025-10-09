from django.urls import path

from items_qr.views.items_qr import search, find_item, autocomplete
from items_qr.views.items_qr import search, find_item
from items_qr.api.autocomplete import autocomplete

urlpatterns = [
    path('', search, name='items_qr'),
    path('search', find_item, name='find_item'),
    path('autocomplete', autocomplete, name='autocomplete_item'),
]