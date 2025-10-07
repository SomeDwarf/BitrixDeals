from django.urls import path

from deals.views.deals import deals, generate_deals, create_deal

urlpatterns = [
    path('', deals, name='deals'),
    path('generate', generate_deals, name='generate_deals'),
    path('create', create_deal, name='create_deal'),
]