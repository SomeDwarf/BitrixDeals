document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("searchInput");
    const list = document.getElementById("autocompleteList");

    let timeout = null;

    input.addEventListener("input", function () {
        const query = this.value.trim();
        clearTimeout(timeout);
        list.innerHTML = "";

        if (query.length < 1) return;

        timeout = setTimeout(() => {
            fetch(`${autocompleteUrl}?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    list.innerHTML = "";

                    if (data.results && data.results.length > 0) {
                        data.results.forEach(item => {
                            const li = document.createElement("li");
                            li.classList.add("autocomplete-item");

                            li.innerHTML = `
                                <span class="item-name">${item.name}</span>
                                <span class="item-id">#${item.id}</span>
                            `;

                            li.addEventListener("click", () => {
                                findItem(item.id)
                            });

                            list.appendChild(li);
                        });
                    } else {
                        const li = document.createElement("li");
                        li.textContent = "Ничего не найдено";
                        li.classList.add("no-results");
                        list.appendChild(li);
                    }
                })
                .catch(err => {
                    console.error("Ошибка автокомплита:", err);
                });
        }, 300);
    });

    function findItem(id = null, query = null) {
        let url = findItemUrl;
        if (id !== null) {
            url += `?id=${encodeURIComponent(id)}`;
        } else if (query !== null) {
            url += `?q=${encodeURIComponent(query)}`;
        }
        window.location.href = url;
    }

    document.getElementById('searchForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Отключаем стандартную отправку
        let query = document.getElementById('searchInput').value.trim();
        if (query) {
            findItem(null, query);
        }
    });
});