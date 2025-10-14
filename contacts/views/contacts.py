from django.http import FileResponse, HttpResponseServerError
from django.shortcuts import render, redirect

from contacts.functions.bitrix_export import FileExporter
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
    ext = request.GET.get("ext", ".csv")
    select = request.GET.getlist("select")
    if 'COMPANY_TITLE' in select:
        select.append('COMPANY_ID')
    # Получение фильтров
    filters = {}
    for key, value in request.GET.items():
        if key in {"select", "ext"}:
            continue
        if not value:
            continue
        if key == "COMPANY_TITLE":
            filters["%COMPANY_TITLE"] = str(value).strip()
        else:
            filters[key] = value

    try:
        file_obj = FileExporter(but).export_file(ext, select, filters)
    except ValueError as e:
        return HttpResponseServerError(e)

    return FileResponse(
        file_obj,
        as_attachment=True,
        filename=f"bitrix_contacts{ext}"
    )
