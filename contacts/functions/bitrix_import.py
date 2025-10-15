from contacts.functions.files import iter_contacts


def make_key(obj_fields, key_fields):
    values = []
    for field in key_fields:
        values.append((obj_fields.get(field) or '').strip().lower())
    key = '_'.join(values)
    return key


class FileImporter:
    def __init__(self, bitrix_token, batch_size=50):
        self.bitrix = bitrix_token
        self.batch_size = batch_size

        self.methods = list()  # Список методов для batch_api_call
        self.contact_fields = set(self.bitrix.call_api_method('crm.contact.fields')['result'].keys())  # Поля контактов

        # Поля для добавления компаний
        self.company_title_to_id = dict()  # Связывает название и ID компании
        self.company_title_to_add_result = dict()  # Связывает название компании и результат crm.company.add запроса
        self.request_to_company_title = dict()  # Сязывает имя crm.company.add запроса и название компании

        # Поля для работы с дубликатами
        self.key_fields = ['NAME', 'LAST_NAME', 'COMPANY_ID']  # Перечень полей, по которым определяются дубликаты
        self.key_to_contact = dict()  # Связывает ключ для поиска дубликата и данные существующих контактов
        self.contacts_for_update = dict()  # Связывает ID контакта и поля, которые в нём нужно обновить
        self.request_to_key = dict()  # связывает имя crm.contact.add запроса с ключом контакта

        self.statistics = {
            'contact': {
                'added': 0,
                'updated': 0,
            },
            'company': {
                'added': 0,
            }
        }

    def get_key_to_contacts(self, select=None):
        """
        Получает все контакты из CRM и возвращает словарь по ключу из полей key_fields.
        Ключ используется для последующего поиска дубликатов.
        """
        if select is None:
            select = ['*', 'UF_*', 'PHONE', 'EMAIL']

        contacts = self.bitrix.call_list_method('crm.contact.list', {
            'select': select
        })

        key_to_contact = {}
        for c in contacts:
            key = make_key(c, self.key_fields)
            key_to_contact[key] = c
        return key_to_contact

    def check_duplicate(self, row):
        """
        Проверяет, есть ли дубликат по ключу из полей key_fields.
        Если найден - сравнивает поля и добавляет в contacts_for_update при отличиях.
        Возвращает contact_id, если найден дубликат, иначе None
        """
        key = make_key(row, self.key_fields)
        existing = self.key_to_contact.get(key)
        if not existing:
            return None

        def compare_fields(old, new):
            """Сравнивает поля контакта, возвращает dict с отличиями."""
            new_fields = {}
            for field, new_value in new.items():
                if field not in self.contact_fields:
                    continue
                old_value = old.get(field)
                # Поля multifield
                if isinstance(new_value, list) and isinstance(old_value, list):
                    old_vals = {str(v.get('VALUE')).strip() for v in old_value if v.get('VALUE')}
                    new_vals = {str(v.get('VALUE')).strip() for v in new_value if v.get('VALUE')}
                    diff = new_vals - old_vals
                    if diff:
                        new_fields[field] = [v for v in new_value if str(v.get('VALUE')).strip() in diff]
                    continue
                # Обычные поля
                if new_value and new_value != old_value:
                    new_fields[field] = new_value
            return new_fields

        contact_id = existing['ID']
        new_fields = compare_fields(existing, row)
        if not new_fields:
            return contact_id

        # Объединяем с уже накопленными обновлениями
        update_entry = self.contacts_for_update.setdefault(contact_id, {'id': contact_id, 'fields': {}})
        for field, value in new_fields.items():
            if isinstance(value, list):
                existing_list = update_entry['fields'].setdefault(field, [])
                existing_vals = {v.get('VALUE') for v in existing_list if v.get('VALUE')}

                for v in value:
                    val = v.get('VALUE')
                    if val and val not in existing_vals:
                        existing_list.append(v)
                        existing_vals.add(val)
            else:
                update_entry['fields'][field] = value

        return contact_id

    def update_by_response(self, response):
        """Функция для замены ссылок на значения по результатам batch запроса"""

        # Обход результатов crm.company.add
        for request, title in self.request_to_company_title.items():
            company_id = response[request].get('result')
            if not company_id:
                continue
            # Если компания была успешно добавлена
            self.company_title_to_id[title] = company_id

        # Обход результатов crm.contact.add
        for request, key in self.request_to_key.items():
            contact_id = response[request].get('result')
            if not contact_id:
                continue
            # Формируем временный ID
            temp_id = f"$result[{request}]"
            # Обновляем запись в key_to_contact
            if key in self.key_to_contact and self.key_to_contact[key]['ID'] == temp_id:
                self.key_to_contact[key]['ID'] = contact_id
                # Обновляем ссылки на temp_id в contacts_for_update
                if temp_id in self.contacts_for_update:
                    self.contacts_for_update[contact_id] = self.contacts_for_update.pop(temp_id)
                    self.contacts_for_update[contact_id]['id'] = contact_id

        # Сброс связей с запросами
        self.company_title_to_add_result = dict()
        self.request_to_company_title = dict()
        self.request_to_key = dict()

    def batch_api_call(self):
        """Вызывает batch_api_call из BitrixToken и обрабатывает ответ"""
        response = self.bitrix.batch_api_call(self.methods)
        self.update_by_response(response)
        self.methods = list()

    def add_method(self, method, expected=0):
        """
        Добавляет метод в список, при достижении размера батча вызывает batch_api_call
        Параметр expected обозначает количество методов после этого, которые должны попасть в один и тот же батч,
        в связи с чем batch_api_call может быть вызван раньше достижения batch_size.
        """
        if len(self.methods) >= self.batch_size - expected:
            self.batch_api_call()
        self.methods.append(method)

    def prepare_company(self, index, row):
        """Готовит COMPANY_ID для контакта (создание новой компании при необходимости)."""
        if row.get('COMPANY_ID'):
            # Если уже указан COMPANY_ID - возвращаем его
            return row['COMPANY_ID']

        title = row.get('COMPANY_TITLE')
        if not title:
            # Если нет названия компании - возвращаем 0 (Битрикс ставит COMPANY_ID 0 по умолчанию)
            return '0'

        if title in self.company_title_to_id:
            # Если указано название компании из CRM - возвращаем её ID
            return self.company_title_to_id[title]

        if title in self.company_title_to_add_result:
            # Если указано название компании, которая будет добавлена в этом батче, - ссылка на результат запроса
            return self.company_title_to_add_result[title]

        # Добавляем новую компанию
        req_name = f'cmp_add_{index}'
        self.add_method((req_name, 'crm.company.add', {'fields': {'TITLE': title}}), expected=1)
        company_temp_id = f"$result[{req_name}]"
        self.company_title_to_add_result[title] = company_temp_id
        self.request_to_company_title[req_name] = title
        self.statistics['company']['added'] += 1
        return company_temp_id

    def import_file(self, file):
        # Получение компаний
        response_companies = self.bitrix.call_list_method('crm.company.list', {
            'select': ['ID', 'TITLE']
        })
        self.company_title_to_id = {c['TITLE']: c['ID'] for c in response_companies}

        self.key_to_contact = self.get_key_to_contacts()
        self.contacts_for_update = dict()

        # Обход контактов из файла
        for i, row in enumerate(iter_contacts(file)):
            row['COMPANY_ID'] = self.prepare_company(i, row)
            duplicate_id = self.check_duplicate(row)
            if duplicate_id:
                # Если дубликат найден - обработаем позже
                continue

            # Добавление нового контакта
            request_name = f'cnt_add_{i}'
            method_name = 'crm.contact.add'
            fields = {'fields': row}
            self.add_method((request_name, method_name, fields))
            self.statistics['contact']['added'] += 1

            # Сохраняем временный ID и ключ
            temp_id = f"$result[{request_name}]"
            key = make_key(row, self.key_fields)
            # Сохраняем в key_to_contact с временным ID
            self.key_to_contact[key] = {'ID': temp_id, **row}
            # Запоминаем связь запроса и ключа
            self.request_to_key[request_name] = key

        # Обновление дубликатов
        for contact_id, update_fields in self.contacts_for_update.items():
            request_name = f"cnt_update_{contact_id}"
            self.add_method((request_name, 'crm.contact.update', update_fields))
            self.statistics['contact']['updated'] += 1

        self.batch_api_call()
        return self.statistics