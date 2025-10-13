import json

from django.http import HttpResponseServerError
from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.exceptions import BitrixApiError
from local_settings import YANDEX_MAP_KEY
from map.functions.format import full_address
from map.functions.geocoder import get_coordinates


@main_auth(on_cookies=True)
def show_map(request):
    but = request.bitrix_user_token
    try:
        # Получение компаний
        response_companies = but.call_list_method('crm.company.list', {
            'select': ['ID', 'TITLE']
        })
        companies_map = {c['ID']: c['TITLE'] for c in response_companies}
        # Получение адресов всех компаний
        response_addresses = but.call_list_method('crm.address.list', {
            'select': ['ENTITY_ID', 'COUNTRY', 'PROVINCE', 'CITY', 'ADDRESS_1'],
            'filter': {'@ENTITY_ID': list(companies_map.keys())}
        })
    except BitrixApiError as e:
        return HttpResponseServerError(f"Ошибка BitrixApi: {e}")

    # Составление списка точек для YMap
    points = []
    for addr in response_addresses:
        full_addr = full_address(addr)
        coords = get_coordinates(full_addr)
        points.append({
            'title': companies_map[addr['ENTITY_ID']],
            'coords': coords,
        })

    context = {
        'api_key': YANDEX_MAP_KEY,
        'points': json.dumps(points),
    }
    return render(request, 'map_page.html', context)
