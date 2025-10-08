from django.shortcuts import render, redirect
from django.http import JsonResponse

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.exceptions import BitrixApiError
from items_qr.dicts import CUSTOM_FIELDS
from items_qr.functions.autocomplete import search_in_catalog, load_autocomplete_catalog


@main_auth(on_cookies=True)
def search(request):
    but = request.bitrix_user_token

    return render(request, 'qr_search_page.html')

@main_auth(on_cookies=True)
def find_item(request):
    but = request.bitrix_user_token
    item_id = request.GET.get("id")
    query = request.GET.get("q")
    context = {}
    try:
        if item_id:
            # Поиск по ID
            item = but.call_api_method('catalog.product.get', {'id': item_id})['result']['product']
        elif query:
            if query.isdigit():
                # Принимаем query как ID
                item = but.call_api_method('catalog.product.get', {'id': int(query)})['result']['product']
            else:
                # Поиск по имени
                iblockId = 15
                products = but.call_list_method('catalog.product.list', {
                    'filter': {"iblockId": iblockId, "name": query},
                    'select': ["id", "iblockId", "name"],
                    'order': {"id": "asc"}
                })['products']
                if products:
                    item = products[0]
        if item:
            context['item'] = item
    except BitrixApiError as e:
        print(e)
        context['error'] = e.json_response['error_description']
    print(context)
    return render(request, 'qr_search_page.html', context)

@main_auth(on_cookies=True)
def autocomplete(request):
    but = request.bitrix_user_token
    query = request.GET.get('q', '')

    catalog = load_autocomplete_catalog(but)
    results = search_in_catalog(query, catalog)

    return JsonResponse({"results": results})