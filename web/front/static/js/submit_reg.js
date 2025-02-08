function submitReg() {
    let formElem = document.getElementById('reg_form')
    let data = new FormData(formElem)

    fetch('/api/add-user', {
        method: 'POST',
        body: data
    })
    .catch(error => console.error(error))
}