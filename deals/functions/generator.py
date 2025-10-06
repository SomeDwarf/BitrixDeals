import random
from deals.functions.dicts import CUSTOM_FIELDS

PROPERTY = ["Красный", "Смешной", "Уставший", "Добрый", "Сердитый", "Огромный", "Нехороший", "Пронырливый"]
ANIMALS = ["Кот", "Пёс", "Волк", "Лис", "Медведь", "Слон", "Пингвин", "Медоед", "Орёл", "Воробей"]

STAGES = ['NEW', 'PREPARATION', 'PREPAYMENT_INVOICE', 'EXECUTING', 'FINAL_INVOICE']
CURRENCIES = ['RUB', 'USD', 'EUR']
DANGER_LEVELS = ["Очень высокая", "Не очень высокая", "Непонятно"]


def random_deals(samples = 5):
    result = []
    for _ in range(samples):
        title = f"{random.choice(PROPERTY)} {random.choice(ANIMALS)}"
        fields = {
            "TITLE": title,
            "STAGE_ID": random.choice(STAGES),
            "CURRENCY_ID": random.choice(CURRENCIES),
            "OPPORTUNITY": round(random.uniform(1, 1000), 2),
            CUSTOM_FIELDS["HIGH_PRIORITY"]: random.choice(['Y', 'N']),
            CUSTOM_FIELDS["DANGER_LEVEL"]: random.choice(DANGER_LEVELS),
        }

        result.append(fields)
    return result