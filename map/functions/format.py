def full_address(addr: dict):
    """Собирает полный адрес из словаря полей Bitrix."""
    parts = [addr.get(field)
             for field in ('COUNTRY', 'PROVINCE', 'REGION', 'CITY', 'ADDRESS_1')
             if addr.get(field)]
    return ', '.join(parts)
