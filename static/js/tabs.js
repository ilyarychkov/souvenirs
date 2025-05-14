function openTab(evt, tabName) {
    // Скрыть все содержимое табов
    const tabContents = document.querySelectorAll(".tab-block");
    for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].style.display = "none";
    }

    // Удалить активный класс у всех табов
    const tabs = document.querySelectorAll(".tab-active");
    for (let i = 0; i < tabs.length; i++) {
        tabs[i].className = tabs[i].className.replace("tab-active", "tab-disabled");
    }

    // Показать текущий таб и добавить активный класс
    document.getElementById(tabName).style.display = "flex";
    evt.currentTarget.className = "tab-active";
}
