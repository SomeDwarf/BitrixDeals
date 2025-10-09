document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('generateQrBtn');

    btn.addEventListener('click', function () {
        const qrBlock = document.getElementById('qrBlock');
        const productId = qrBlock ? qrBlock.dataset.itemId : null;

        btn.disabled = true;
        btn.textContent = 'Генерирую QR...';

        fetch(`${generateQrUrl}?id=${productId}`)
            .then(response => {
                if (!response.ok) throw new Error('Ошибка запроса QR');
                return response.blob();
            })
            .then(blob => {
                const imgUrl = URL.createObjectURL(blob);
                let qrContainer = document.getElementById('qrResult');
                if (!qrContainer) {
                    qrContainer = document.createElement('div');
                    qrContainer.id = 'qrResult';
                    qrBlock.appendChild(qrContainer);
                }

                qrContainer.innerHTML = `
                    <h3>QR-код для товара</h3>
                    <img src="${imgUrl}" class="qr-code">
                `;

                btn.disabled = false;
                btn.textContent = 'Сгенерировать QR-код';
            })
            .catch(err => {
                alert('Ошибка: ' + err.message);
                btn.disabled = false;
                btn.textContent = 'Сгенерировать QR-код';
            });
    });
});
