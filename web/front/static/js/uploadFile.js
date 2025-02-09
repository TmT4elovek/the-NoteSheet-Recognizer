function uploadFile(event) {
    // Prevent form submission
    event.preventDefault()

    var file = document.getElementById('actual-btn');

    if(file.files.length)
    {
        var reader = new FileReader();

        reader.onload = function(e)
        {
            document.getElementById('outputDiv').innerHTML = e.target.result;
        };

        reader.readAsBinaryString(file.files[0]);
        
        fetch('/upload', {
            method: 'POST',
            body: reader.result
        })
    }
}