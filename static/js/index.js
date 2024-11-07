function toggleRecording() {
    const serverUrl = "http://192.168.1.60:8888/toggle_recording";
    fetch(serverUrl, { method: 'POST' })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const status = data.is_recording ? 'Recording' : 'Stopped';
            document.getElementById('recording-status').innerText = status;
            document.getElementById('recording-status').style.color = data.is_recording ? 'red' : 'gray';
            document.querySelector('.button').innerText = data.is_recording ? 'Stop Recording' : 'Start Recording';
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}
