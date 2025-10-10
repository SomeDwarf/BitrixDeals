import random
from datetime import datetime, timedelta, timezone


def random_calls(employees, n=10, false_n=5, phone_number=None):
    """
    Генерирует n записей исходящих звонков в виде списка словарей для запросов register и finish.
    Из них false_n записей либо имеют длительность меньше 60 секунд, либо старше 24 часов.
    """
    if len(employees) == 0:
        return []

    if phone_number is None:
        phone_number = "+7 123 456 78 90"

    results = []

    for i in range(n):
        emp_id = random.choice(employees)

        duration = timedelta(seconds=random.randint(61, 120))
        now = datetime.now(timezone.utc)
        # Для первых false_n подставляем данные, не проходящие фильтры
        if i < false_n:
            falsehood = random.choice(["start_date", "duration"])
            if falsehood == "start_date": now = now - timedelta(days=7)
            elif falsehood == "duration": duration = timedelta(seconds=random.randint(1, 60))
        start_utc = now - duration

        record = {
            # Поля для telephony.externalcall.register
            "register": {
                "USER_ID": emp_id,
                "PHONE_NUMBER": phone_number,
                "CALL_START_DATE": start_utc.isoformat(),
                "CRM_CREATE": 0,
                "SHOW": 0,
                "TYPE": 1,
            },
            # Поля для telephony.externalcall.finish
            "finish": {
                "CALL_ID": None,  # Необходимо добавить из результата запроса register
                "USER_ID": emp_id,
                "DURATION": duration.total_seconds(),
            }
        }

        results.append(record)

    return results