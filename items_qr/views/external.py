from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

from integration_utils.bitrix24.bitrix_token import BitrixToken
from integration_utils.bitrix24.exceptions import BitrixApiError

from items_qr.dicts import CUSTOM_FIELDS
from local_settings import BITRIX_DOMAIN, BITRIX_WEBHOOK


def external_item(request):
    signed_data = request.GET.get('signed')
    if not signed_data:
        return HttpResponseForbidden("Отсутствует подпись")

    signer = TimestampSigner()
    try:
        product_id = int(signer.unsign(signed_data))
    except SignatureExpired:
        return HttpResponseForbidden("Время действия подписи истекло")
    except BadSignature:
        return HttpResponseForbidden("Неверная подпись ссылки")

    # Получение данных о товаре через вебхук
    bt = BitrixToken(domain=BITRIX_DOMAIN, web_hook_auth=BITRIX_WEBHOOK)
    methods = [
        ('catalog.product.get', {'id': product_id}),
        ('catalog.productImage.list', {
            'select': ['detailUrl'],
            'productId': product_id
        }),
        ('catalog.price.list', {
            'select': ['currency', 'price'],
            'filter': {'productId': product_id}
        })
    ]
    try:
        response = bt.batch_api_call(methods)
    except BitrixApiError as e:
        return HttpResponseForbidden(e)
    product_response = response.get('data_0')
    image_response = response.get('data_1')
    price_response = response.get('data_2')

    product = product_response.get("result").get("product")
    if product:
        # Обработка кастомного поля
        if product.get(CUSTOM_FIELDS["family"]):
            product["family"] = product.get(CUSTOM_FIELDS["family"]).get('value')
            del product[CUSTOM_FIELDS["family"]]
        # Получение ссылки на изображение
        product_images = image_response.get("result").get("productImages")
        if product_images and len(product_images) > 0:
            product["imageUrl"] = product_images[0].get("detailUrl")
        # Получение цены товара
        prices = price_response.get("result").get("prices")
        if prices and len(prices) > 0:
            product["price"] = prices[0].get("price")
            product["currency"] = prices[0].get("currency")

    context = {
        "product": product
    }

    return render(request, "external_item.html", context)
