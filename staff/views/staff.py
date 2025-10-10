import pprint
from datetime import datetime, timedelta, timezone

from django.http import HttpResponseServerError
from django.shortcuts import render, redirect

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from integration_utils.bitrix24.exceptions import BitrixApiError
from staff.functions.employee_hierarchy import collect_employees_by_department
from staff.functions.generator import random_calls


@main_auth(on_cookies=True)
def table(request):
    but = request.bitrix_user_token
    context = {}
    try:
        # Получение всех активных сотрудников
        response_users = but.call_list_method('user.get', {
            'FILTER': {'USER_TYPE': 'employee', 'ACTIVE': 'true'}
        })
        # Получение всех отделов
        response_departments = but.call_list_method('department.get')
        # Получение звонков всех активных сотрудников
        users_id = [user.get('ID') for user in response_users]
        start_date = datetime.now(timezone.utc) - timedelta(hours=24)
        response_calls = but.call_list_method('voximplant.statistic.get', {
            'FILTER': {
                'CALL_TYPE': 1,
                '@PORTAL_USER_ID': users_id,
                '>CALL_DURATION': 60,
                '>CALL_START_DATE': start_date.isoformat(),
            }
        })
        # Подсчёт количества звонков для каждого пользователя
        calls_count = {uid: 0 for uid in users_id}
        for call in response_calls:
            key = call['PORTAL_USER_ID']
            if key in calls_count:
                calls_count[call['PORTAL_USER_ID']] += 1
            else:
                calls_count[call['PORTAL_USER_ID']] = 1
        for user in response_users:
            user["CALLS_COUNT"] = calls_count.get(user.get('ID'))
    except BitrixApiError as e:
        return HttpResponseServerError(f"Ошибка BitrixApi: {e}")

    # Сборка данных для таблицы
    if response_users and response_departments:
        employees_data = collect_employees_by_department(response_users, response_departments)
        context['employees'] = employees_data

    return render(request, 'staff_table.html', context)


@main_auth(on_cookies=True)
def generate_calls(request):
    but = request.bitrix_user_token
    try:
        # Получение всех активных сотрудников
        response_users = but.call_list_method('user.get', {
            'FILTER': {'USER_TYPE': 'employee', 'ACTIVE': 'true'}
        })
        users_id = [user.get('ID') for user in response_users]
    except BitrixApiError as e:
        return HttpResponseServerError(f"Ошибка BitrixApi: {e}")

    calls = random_calls(users_id)
    # Подготовка batch_api_call
    methods = []
    for i, call in enumerate(calls):
        # Регистрация звонка
        register_name = f"register_{i}"
        methods.append((register_name, "telephony.externalcall.register", call["register"]))
        # Завершение звонка
        # Добавляем в список полей CALL_ID из результата запроса register
        call["finish"]["CALL_ID"] = f"$result[{register_name}][CALL_ID]"
        finish_name = f"finish_{i}"
        methods.append((finish_name, "telephony.externalcall.finish", call["finish"]))
    try:
        response = but.batch_api_call(methods, halt=1)
    except BitrixApiError as e:
        return HttpResponseServerError(f"Ошибка BitrixApi: {e}")

    return redirect("staff")
