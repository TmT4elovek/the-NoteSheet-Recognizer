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
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.status == 409) {
            alert('User already exists');
            return;
        } else {
        // console.log('Good req', data);
        // window.location.href = 'http://127.0.0.1:8000/login';
        return;
        }
    })
    .catch(error => console.error(error))
    
} 