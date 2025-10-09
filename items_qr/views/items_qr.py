from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.exceptions import BitrixApiError

IBLOCK_ID = 15

@main_auth(on_cookies=True)
def search(request):
    return render(request, 'qr_search_page.html')


@main_auth(on_cookies=True)
def find_item(request):
    but = request.bitrix_user_token
    item_id = request.GET.get("id")
    query = request.GET.get("q")
    context = {}
    # Поиск товара
    try:
        item = None
        if item_id:
            # Поиск по ID
            item = but.call_api_method('catalog.product.get', {'id': item_id})['result']['product']
        elif query:
            if query.isdigit():
                # Принимаем query как ID
                item = but.call_api_method('catalog.product.get', {'id': int(query)})['result']['product']
            else:
                # Поиск по имени
                # В случае нескольких товаров с одинаковым именем - будет выбран с наименьшим ID
                products = but.call_list_method('catalog.product.list', {
                    'filter': {"iblockId": IBLOCK_ID, "name": query},
                    'select': ["id", "iblockId", "name"],
                    'order': {"id": "asc"}
                })['products']
                if products and len(products) > 0:
                    item = products[0]
        if item:
            context['item'] = item
    except BitrixApiError as e:
        print(e)
        context['error'] = e.json_response['error_description']

    return render(request, 'qr_search_page.html', context)