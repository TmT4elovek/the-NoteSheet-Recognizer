function submitLog(event) {
    // Prevent form submission
    event.preventDefault()

    let formElem = document.getElementById('log_form')
    let formData = new FormData(formElem)
    console.log(formData)
    let data = Object.fromEntries(formData.entries());
    console.log(data)
    fetch('api/check-user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if(response.status == 404) {
            alert('User not found');
        } if (response.status == 422) {
            alert('Invalid body')
        }else{
            window.location.href = 'http://127.0.0.1:8000/';
            console.log('Good log', data);
        }
    })
    .catch(error => console.error(error));
    
} 