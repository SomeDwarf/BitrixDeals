from django.core.cache import cache

# Время хранения словаря в кэше в секундах
DEFAULT_TIMEOUT = 24 * 3600

# Словарь кастомных полей для удобства использования в коде
CUSTOM_FIELDS = {
    "DANGER_LEVEL": "UF_CRM_1759749123",
    "HIGH_PRIORITY": "UF_CRM_1759745698630",
}

# Функция получения словаря стадий сделки для преобразования ID стадии в её имя
def get_stage_dict(but):
    stage_dict = cache.get('deals_stage_dict')
    if stage_dict:
        return stage_dict

    stage_status_list = but.call_list_method('crm.status.list', {
        'filter': {'ENTITY_ID': 'DEAL_STAGE'}
    })
    stage_dict = {stage['STATUS_ID']: stage['NAME'] for stage in stage_status_list}
    cache.set('deals_stage_dict', stage_dict, DEFAULT_TIMEOUT)
    return stage_dict