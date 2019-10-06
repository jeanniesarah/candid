document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure button
    socket.on('connect', () => {

        // Notify server user has joined
        socket.emit('joined');

        // Forget user's last channel when clicked on 'New channel'
        document.querySelector('#newChannel').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });

        // When user leaves channel redirect '/'
        document.querySelector('#leave').addEventListener('click', () => {

            // Notify the server user has left
            socket.emit('left');

            localStorage.removeItem('last_channel');
            window.location.replace('/');
        })

        // Forget user's last channel when logged out
        document.querySelector('#logout').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });

        // 'Enter' key on textarea also sends a message
        document.querySelector('#comment').addEventListener("keydown", event => {
            if (event.key == "Enter") {
                document.getElementById("send-button").click();
            }
        });
        
        // Send button emits a "message sent" event
        document.querySelector('#send-button').addEventListener("click", () => {
            
            // Save time in format HH:MM:SS
            let timestamp = new Date;
            timestamp = timestamp.toLocaleTimeString();

            // Save user input
            let msg = document.getElementById("comment").value;

            socket.emit('send message', msg, timestamp);
            
            // Clear input
            document.getElementById("comment").value = '';
        });
    });
    
    // When user joins channel, add message and on users connected
    socket.on('status', data => {

        // Broadcast message new joined user
        let row = '<' + `${data.msg}` + '>'
        document.querySelector('#chat').value += row + '\n';

        // Save user current channel on localStorage
        localStorage.setItem('last_channel', data.channel)
    })

    // When a message is announced, add it to textarea
    socket.on('announce message', data => {

        // Format message
        let row = '<' + `${data.timestamp}` + '> - ' + '[' + `${data.user}` + ']:  ' + `${data.msg}`
        document.querySelector('#chat').value += row + '\n'
    })

    
});