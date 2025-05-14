function extraFilters() {
    let block = document.querySelector('.extra-filters');
    let showHideBtn = document.querySelector('.checkbox-block span');

    if (showHideBtn.textContent == 'Ещё') {
        block.style.display = 'flex'; 
        showHideBtn.textContent = 'Скрыть';
    } else {
        block.style.display = 'none';
        showHideBtn.textContent = 'Ещё';
    }
}

let sortForm = document.querySelector('.sort-block');
let resetBtn = document.querySelector('.reset-btn');

resetBtn.addEventListener('click', resetFilters); // Привязка обработчика

// Сброс фильтров
function resetFilters(event) {
    event.preventDefault(); // Предотвратить отправку формы
    const checkboxes = document.querySelectorAll('.checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false; // Сбросить состояние чекбокса
    });
    // После сброса можно отправить форму с пустыми параметрами
    sortForm.submit(); // Изменено на правильное обращение к форме
}

// Сортировка select
function sortCatalog(sortType) {
    window.location.href = `/arts-catalog?sort=${sortType}`;
}

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const artsBlock = document.querySelector('.arts-block'); 
    const artCards = artsBlock.querySelectorAll('.art-card');

    searchInput.addEventListener('input', function() {
        const searchTerm = searchInput.value.toLowerCase();

        artCards.forEach(card => {
            const artTitle = card.querySelector('.art-title').textContent.toLowerCase();
            
            // Проверяем, содержит ли название товара искомый текст
            if (artTitle.includes(searchTerm)) {
                card.style.display = ''; // Показываем карточку
            } else {
                card.style.display = 'none'; // Скрываем карточку
            }
        });
    });
});