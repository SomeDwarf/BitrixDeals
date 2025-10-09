from django.urls import path

from items_qr.views.items_qr import search, find_item
from items_qr.views.external import external_item
from items_qr.api.autocomplete import autocomplete
from items_qr.api.qr import generate

urlpatterns = [
    path('', search, name='items_qr'),
    path('search', find_item, name='find_item'),
    path('autocomplete', autocomplete, name='autocomplete_item'),
    path('generate_qr', generate, name='generate_qr'),
    path('external/item/', external_item, name='external_item'),
]