from django.urls import path

from contacts.views.contacts import contacts

urlpatterns = [
    path('', contacts, name='contacts'),
]