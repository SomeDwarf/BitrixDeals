import pprint

from django.shortcuts import render, redirect

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.exceptions import BitrixApiError


@main_auth(on_cookies=True)
def show_map(request):
    but = request.bitrix_user_token
    return render(request, 'map_page.html')