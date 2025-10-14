from contacts.functions.files import write_contacts


class FileExporter:
    def __init__(self, bitrix_token, batch_size=50):
        self.bitrix = bitrix_token
        self.batch_size = batch_size

    def export_file(self, ext=".csv", select=None, filters=None):
        """
        Экспортирует контакты из Битрикс24 в файл.
        Возвращает объект типа BytesIO.
        """
        if filters is None:
            filters = {}

        # Получение компаний
        company_filter = {}
        if filters.get('%COMPANY_TITLE'):
            # Если используется поиск по компании - добавляется фильтр для компаний
            company_filter['%TITLE'] = filters['%COMPANY_TITLE'] if filters.get('%COMPANY_TITLE') else {}
        companies = self.bitrix.call_list_method('crm.company.list', {
            'select': ['ID', 'TITLE'],
            'filter': company_filter
        })
        company_id_to_title = {c['ID']: c['TITLE'] for c in companies}

        # Получение контактов
        if filters.get('%COMPANY_TITLE'):
            # Если используется поиск по компании - добавляется фильтр по ID найденных компаний
            filters['@COMPANY_ID'] = list(company_id_to_title.keys())
        contacts = self.bitrix.call_list_method('crm.contact.list', {
            'select': select,
            'filter': filters,
        })

        # Получение порядка полей контактов
        fields_info = self.bitrix.call_api_method('crm.contact.fields')['result']
        field_order = list(fields_info.keys())

        # Добавление поля COMPANY_TITLE
        for c in contacts:
            if not select or 'COMPANY_TITLE' in select:
                # Если выбрано поле COMPANY_TITLE - заменяем ID компании на её название
                company_id = c.get('COMPANY_ID')
                c['COMPANY_TITLE'] = company_id_to_title.get(company_id, "")
                del c['COMPANY_ID']
            if not 'ID' in select:
                # Если поле ID не было выбрано в select - удаляем его
                # Битрикс, судя по всему, всегда возращает ID, даже если его не указывать
                del c['ID']

        # Сортировка полей для заголовков по их порядку в crm.contact.fields
        headers = set().union(*(c.keys() for c in contacts))
        ordered_headers = [h for h in field_order if h in headers]
        # Оставшиеся заголовки добавляются в конец списка
        for h in headers:
            if h not in ordered_headers:
                ordered_headers.append(h)

        file_obj = write_contacts(contacts, ordered_headers, ext=ext)
        return file_obj
