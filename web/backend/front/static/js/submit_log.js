function getCookie(name) {
    let cookieArr = document.cookie.split("; ");
    for(let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");
        if (name == cookiePair[0]) {
            return cookiePair[1];
        }
    }
    return null;
}


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
            return;
        } if (response.status == 422) {
            alert('Invalid body')
            return;
        }else{
            window.location.href = 'http://127.0.0.1:8000/';
            console.log('Good log', data);
        }
    })
    .catch(error => console.error(error));
}