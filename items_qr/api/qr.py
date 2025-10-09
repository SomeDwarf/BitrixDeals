from django.http import HttpResponse
from django.core.signing import TimestampSigner
from django.urls import reverse

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

import qrcode
from io import BytesIO

@main_auth(on_cookies=True)
def generate(request):
    product_id = request.GET.get('id')
    if not product_id:
        return HttpResponse('Не указан ID товара', status=400)

    signer = TimestampSigner()
    signed_value = signer.sign(product_id)
    external_url = request.build_absolute_uri(
        reverse('external_item') + f'?signed={signed_value}'
    )

    qr = qrcode.make(external_url)
    buf = BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)

    return HttpResponse(buf.read(), content_type='image/png')