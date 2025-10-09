import pprint

from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.exceptions import BitrixApiError
from staff.functions.employee_hierarchy import collect_employees_by_department


@main_auth(on_cookies=True)
def table(request):
    but = request.bitrix_user_token
    context = {}
    response_users = None
    response_departments = None
    try:
        # Получение всех активных сотрудников
        response_users = but.call_list_method('user.get', {
            'FILTER': { 'USER_TYPE': 'employee', 'ACTIVE': 'true' }
        })
        # Получение всех отделов
        response_departments = but.call_list_method('department.get')
        # Получение звонков всех активных сотрудников
        users_id = [user.get('ID') for user in response_users]
        response_calls = but.call_list_method('voximplant.statistic.get', {
            'FILTER': {
                'CALL_TYPE': 1,
                '@PORTAL_USER_ID': users_id,
                '>CALL_DURATION': 60,
            }
        })
        pprint.pprint(response_calls)
    except BitrixApiError as e:
        print(e)

    if response_users and response_departments:
        employees_data = collect_employees_by_department(response_users, response_departments)
        context['employees'] = employees_data

    return render(request, 'staff_table.html', context)