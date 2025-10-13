from hashlib import sha256

import requests
from django.core.cache import cache

from local_settings import YANDEX_MAP_KEY, BITRIX_DOMAIN

CACHE_TTL = 24 * 3600

GEOCODER_URL = "https://geocode-maps.yandex.ru/v1/"


def make_cache_key(prefix, text):
    """Возвращает ключ для кэшировния текста с заданным префиксом"""
    hashed = sha256(text.encode('utf-8')).hexdigest()
    return f"{prefix}:{hashed}"


def get_coordinates(address):
    """Возвращает координаты для адреса, используя API Геокодера или кэш."""
    cache_key = make_cache_key("geocode", address)
    coords = cache.get(cache_key)
    if coords:
        return coords

    params = {
        'apikey': YANDEX_MAP_KEY,
        'geocode': address,
        'lang': 'ru_RU',
        'format': 'json',
    }
    headers = {"Referer": BITRIX_DOMAIN}
    try:
        resp = requests.get(GEOCODER_URL, params=params, headers=headers)
        data = resp.json()
        pos = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        lon, lat = pos.split(' ')
        coords = [float(lon), float(lat)]
        cache.set(cache_key, coords, CACHE_TTL)
        return coords
    except Exception as e:
        print(f"Не удалось геокодировать адрес {address}: {e}")
        return None
