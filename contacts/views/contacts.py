from django.shortcuts import render, redirect

from contacts.functions.bitrix_import import FileImporter
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth


@main_auth(on_cookies=True)
def contacts(request):
    return render(request, 'contacts_page.html')


@main_auth(on_cookies=True)
def import_contacts(request):
    but = request.bitrix_user_token
    if request.method == "POST" and request.FILES.get("import_file"):
        file = request.FILES["import_file"]
        FileImporter(but).import_file(file)
    return redirect("contacts")


@main_auth(on_cookies=True)
def export_contacts(request):
    but = request.bitrix_user_token

    return render(request, 'contacts_page.html')
