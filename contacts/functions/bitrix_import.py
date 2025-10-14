from contacts.functions.files import iter_contacts


class FileImporter:
    def __init__(self, bitrix_token, batch_size=50):
        self.bitrix = bitrix_token
        self.batch_size = batch_size

        self.methods = list()  # Список методов для batch_api_call
        self.companies_id = set()  # Множество всех ID компаний в CRM
        self.title_to_id = dict()  # Связывает название и ID компании
        self.title_to_add_result = dict()  # Связывает название компании и ссылку на результат crm.company.add запроса
        self.request_to_title = dict()  # Сязывает имя crm.company.add запроса и название компании

    def add_method(self, method, expected=0):
        """
        Добавляет метод в список, при достижении размера батча вызывает batch_api_call
        Параметр expected обозначает количество методов после этого, которые должны попасть в один и тот же батч,
        в связи с чем batch_api_call может быть вызван раньше достижения batch_size.
        """
        if len(self.methods) >= self.batch_size - expected:
            self.batch_api_call()
        self.methods.append(method)

    def batch_api_call(self):
        """Вызывает batch_api_call из BitrixToken и обрабатывает ответ"""
        response = self.bitrix.batch_api_call(self.methods)
        # Обход результатов crm.company.add
        for request, title in self.request_to_title.items():
            company_id = response[request].get('result')
            if company_id:
                # Если компания была успешно добавлена
                self.companies_id.add(company_id)
                self.title_to_id[title] = company_id
        # Сброс методов и данных о запросах батча
        self.methods = list()
        self.title_to_add_result = dict()
        self.request_to_title = dict()

    def import_file(self, file):
        # Получение компаний
        response_companies = self.bitrix.call_list_method('crm.company.list', {
            'select': ['ID', 'TITLE']
        })
        self.title_to_id = {c['TITLE']: c['ID'] for c in response_companies}
        self.companies_id = {c['ID'] for c in response_companies}

        # Обход контактов из файла
        for i, row in enumerate(iter_contacts(file)):
            company_id = row.get('COMPANY_ID')
            if company_id:
                # Если у контакта указан ID его компании
                if not company_id in self.companies_id:
                    # Пропуск контакта, если компании с таким ID нет в CRM
                    continue
            elif row.get('COMPANY_TITLE'):
                # Если у контакта не указан ID, но указано имя компании
                title = row['COMPANY_TITLE']
                if self.title_to_id.get(title):
                    # Если название компании уже есть в CRM
                    # Контакту присваивается COMPANY_ID существующей компании
                    row['COMPANY_ID'] = self.title_to_id[title]
                elif self.title_to_add_result.get(title):
                    # Если компания добавлялась для предыдущего контакта в батче
                    # Контакту вместо COMPANY_ID присваивается ссылка на результат запроса на добавление компании
                    row['COMPANY_ID'] = self.title_to_add_result[title]
                else:
                    # Добавляется новая компания с указанным названием
                    request_name = f'cmp_add_{i}'
                    method_name = 'crm.company.add'
                    fields = {'fields': {'TITLE': row['COMPANY_TITLE']}}
                    self.add_method((request_name, method_name, fields), expected=1)
                    # Контакту присваивается COMPANY_ID созданной компании
                    company_url_id = f'$result[{request_name}]'
                    row['COMPANY_ID'] = company_url_id
                    # Сохранение ссылки на COMPANY_ID для использования следующими контактами в батче
                    self.title_to_add_result[title] = company_url_id
                    self.request_to_title[request_name] = title

            request_name = f'cnt_add_{i}'
            method_name = 'crm.contact.add'
            fields = {'fields': row}
            self.add_method((request_name, method_name, fields))

        self.batch_api_call()