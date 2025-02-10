function submitReg(event) {
    // Prevent form submission
    event.preventDefault()

    let formElem = document.getElementById('reg_form')
    let formData = new FormData(formElem)
    let data = Object.fromEntries(formData.entries());

    fetch('api/add-user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: data
    })
    .then(response => {
        console.log('Good req', data);
        window.location.href = 'http://127.0.0.1:8000/login';
    })
    .catch(error => console.error(error))
    
} 