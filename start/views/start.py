from django.shortcuts import render
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

# Функция рендера стартовой страницы
# Вынес, чтобы не дублировать в View с разными декораторами
def render_start(request):
    # Получение имени пользователя
    user = request.bitrix_user
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
    }

    return render(request, 'start_page.html', context)

# View при запуске приложения
@main_auth(on_start=True, set_cookie=True)
def start(request):
    return render_start(request)

# View для возвращаения на главную
@main_auth(on_cookies=True)
def reload_start(request):
    return render_start(request)