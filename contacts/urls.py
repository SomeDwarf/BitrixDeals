from django.urls import path

from contacts.views.contacts import contacts, import_contacts, export_contacts

urlpatterns = [
    path('', contacts, name='contacts'),
    path('import', import_contacts, name='import_contacts'),
    path('export', export_contacts, name='export_contacts'),
]