// Раскрытие биографии художника
function showBio() {
    let bioText = document.querySelector('#bioText');
    let moreBtn = document.querySelector('#bioMoreBtn');

    if (moreBtn.textContent == "Читать дальше") {
        bioText.style = "overflow: visible; -webkit-line-clamp: none;";
        moreBtn.textContent = "Скрыть"
    }
    else {
        bioText.style = "overflow: hidden; -webkit-line-clamp: 3;";
        moreBtn.textContent = "Читать дальше"
    }
}