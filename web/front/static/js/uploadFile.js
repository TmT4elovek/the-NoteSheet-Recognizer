function uploadFile(event) {
    // Prevent form submission
    event.preventDefault()

    let formElem = document.getElementById('upload-form');
    let formData = new FormData(formElem);
    let data = Object.fromEntries(formData.entries());

    alert(data);
}