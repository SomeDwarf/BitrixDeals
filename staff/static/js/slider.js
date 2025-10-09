document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".employee-cell, .head-name").forEach(function (elem) {
        elem.addEventListener("click", function () {
            const userId = elem.dataset.userId;
            BX24.openPath(`/company/personal/user/${userId}/`);
        });
    });
});