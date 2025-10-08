from django.core.cache import cache

CACHE_KEY = "bitrix_catalog_cache"
IBLOCK_ID = 15  # ID информационного блока каталога
CACHE_TTL = 60  # 1 минута

def load_autocomplete_catalog(but, iblock_id=IBLOCK_ID):
    """
    Загрузка товаров из Bitrix или кэша для использования в автокомплите.
    """
    catalog = cache.get(CACHE_KEY)
    if catalog is not None:
        return catalog

    products = but.call_list_method('catalog.product.list', {
        'filter': {"iblockId": iblock_id},
        'select': ["id", "iblockId", "name"],
        'order': {"id": "asc"}
    })['products']

    catalog = []
    for item in products:
        catalog.append({
            'id': str(item['id']),
            'search_name': item['name'].strip().lower(), # для поиска
            'display_name': item['name'], # для отображения пользователю
        })

    cache.set(CACHE_KEY, catalog, CACHE_TTL)
    return catalog


def search_in_catalog(query, catalog, limit=5):
    """
    Поиск товаров по подстроке в названии или в ID.
    Ожидается каталог аналогичный load_autocomplete_catalog().
    """
    query = query.strip().lower()
    if not query:
        return []
    id_search = query.isdigit() # Поиск по ID только если запрос является числом

    results = []
    for item in catalog:
        if query in item["search_name"] or (id_search and query in item["id"]):
            results.append({
                "id": item["id"],
                "name": item["display_name"]
            })
            if len(results) >= limit:
                break

    return results