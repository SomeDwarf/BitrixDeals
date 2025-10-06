from django.shortcuts import render, redirect
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from deals.functions.dicts import get_stage_dict, CUSTOM_FIELDS
from deals.functions.generator import random_deals
from pprint import pprint


@main_auth(on_cookies=True)
def deals(request):
    but = request.bitrix_user_token
    user_id = request.bitrix_user.id
    active_stages = ['NEW', 'PREPARATION', 'PREPAYMENT_INVOICE', 'EXECUTING', 'FINAL_INVOICE']
    deals = but.call_list_method('crm.deal.list', {
        'select': ['ID', 'TITLE', 'CURRENCY_ID',
                   'OPPORTUNITY', 'STAGE_ID', 'DATE_CREATE',
                   CUSTOM_FIELDS['DANGER_LEVEL'], CUSTOM_FIELDS['HIGH_PRIORITY']],
        'filter': {'ASSIGNED_BY_ID': user_id, 'STAGE_ID': active_stages},
        'order': {'DATE_CREATE': 'DESC'},
    })[:10]

    stage_dict = get_stage_dict(but)
    for deal in deals:
        deal['STAGE_NAME'] = stage_dict.get(deal.get('STAGE_ID'))
        deal['DANGER_LEVEL'] = deal.get(CUSTOM_FIELDS['DANGER_LEVEL'])
        deal['HIGH_PRIORITY'] = deal.get(CUSTOM_FIELDS['HIGH_PRIORITY'])

    return render(request, 'deals_page.html', {'deals': deals})

@main_auth(on_cookies=True)
def generate_deals(request):
    but = request.bitrix_user_token

    new_deals = random_deals()
    methods = [('crm.deal.add', {'fields': deal_fields}) for deal_fields in new_deals]
    try:
        but.batch_api_call(methods)
    except Exception as e:
        print(e)

    return redirect("deals")