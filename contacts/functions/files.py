import csv
import os
from io import TextIOWrapper, BytesIO

from openpyxl import load_workbook

CRM_MULTIFIELD = {'PHONE', 'EMAIL', 'WEB', 'IM', 'LINK'}


def iter_contacts(file):
    """
    Универсальный итератор контактов из файла.
    К файлу выдвигаются следующие требования:
    - указаны заголовки полей
    - наличие заголовка NAME
    - записи без значения в поле NAME игнорируются
    - значения для полей с множеством значений разделены запятой
    """
    ext = os.path.splitext(file.name.lower())[-1]
    # Допустимые расширения файла и их парсеры
    parsers = {
        ".csv": _parse_csv,
        ".xlsx": _parse_xlsx,
    }

    parser = parsers.get(ext)
    if not parser:
        raise ValueError(f"Неподдерживаемый формат файла: {ext}")

    for row in parser(file):
        # Пропуск строк без значения в NAME
        if not row.get("NAME"):
            continue
        # Преобразование multifield полей
        _parse_multifield(row)
        yield row


def _parse_multifield(row):
    """
    Преобразует поля контакта с множеством значений из строки в список словарей.
    Предпологается, что значения в строке разделены запятой.
    Также возможно, что строка содержит тип и значение, разделённые символом ':'.
    Например, "<значение 1>,<значение 2>,<тип значения 3>:<значение 3>".
    """
    for field in CRM_MULTIFIELD:
        if field in row:
            parsed_multifield = []
            if str(row[field]):
                for field_values in str(row[field]).split(','):
                    split_values = field_values.split(':', maxsplit=1)
                    if len(split_values) == 2:
                        value_type, value = split_values
                        parsed_multifield.append({'VALUE_TYPE': value_type, 'VALUE': value})
                    elif len(split_values) == 1:
                        value = split_values[0]
                        parsed_multifield.append({'VALUE': value})
            row[field] = parsed_multifield


def _parse_csv(file, delimiter=";"):
    file.seek(0)
    wrapper = TextIOWrapper(file.file, encoding="utf-8")
    reader = csv.reader(wrapper, delimiter=delimiter)

    try:
        headers = next(reader)
    except StopIteration:
        return  # Пустой файл

    headers = [h.strip() for h in headers if h is not None]
    if "NAME" not in headers:
        return  # Если нет столбца NAME - не парсим

    for row in reader:
        row_data = {}
        for i, header in enumerate(headers):
            value = str(row[i]).strip() if i < len(row) else ""
            row_data[header] = value or ""
        yield row_data


def _parse_xlsx(file):
    file.seek(0)
    data = BytesIO(file.read())
    wb = load_workbook(data, read_only=True, data_only=True)
    sheet = wb.active

    rows = sheet.iter_rows(values_only=True)
    try:
        headers = [str(h).strip() if h else "" for h in next(rows)]
    except StopIteration:
        return  # Пустой файл

    if "NAME" not in headers:
        return  # Если нет столбца NAME - не парсим

    for values in rows:
        row_data = {}
        for i, header in enumerate(headers):
            value = values[i] if i < len(values) else ""
            if isinstance(value, str):
                value = value.strip()
            row_data[header] = value or ""
        yield row_data
