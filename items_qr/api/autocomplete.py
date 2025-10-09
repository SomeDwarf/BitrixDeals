from django.http import JsonResponse

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

from items_qr.functions.autocomplete import search_in_catalog, load_autocomplete_catalog


@main_auth(on_cookies=True)
def autocomplete(request):
    but = request.bitrix_user_token
    query = request.GET.get('q', '')

    catalog = load_autocomplete_catalog(but)
    results = search_in_catalog(query, catalog)

    return JsonResponse({"results": results})