let form = document.querySelector('#fillForm');
let btn = document.querySelector('#applyForm');

form.addEventListener('change', changeFormHandler);

function changeFormHandler() {
    console.log(form.checkValidity());
    if (form.checkValidity()) {
        btn.removeAttribute('disabled');
    }
    else {
        btn.setAttribute('disabled', '');
    }
}
