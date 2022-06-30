let streamSocket;
const hostname = JSON.parse(document.getElementById('hostname').textContent);
// console.log(hostname)

let urlCreator = window.URL || window.webkitURL
let videoURL
let video = document.getElementById('video');

function connectSocket() {
    streamSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/'
        + 'video_stream/'
        + hostname
        + '/'
    );

    streamSocket.binaryType = 'arraybuffer';

    streamSocket.onopen = (e) => {
        streamSocket.send(JSON.stringify({
            type: 'receive',
            data: {
                hostname: hostname
            }
        }));
    }

    streamSocket.onclose = (e) => {
        streamSocket.close(1000)
        console.log('close')
        video.src = document.getElementById('cam_off').value;
        console.log('Disconnect from server');
    }

    streamSocket.onmessage = (e) => {
        if (e.data instanceof ArrayBuffer) {
            // console.log(e)
            // console.log(e.data)

            let arrayBufferView = new Uint8Array(e.data);
            // console.log(arrayBufferView)
            let blob = new Blob([arrayBufferView], {type: "image/jpeg"});
            // console.log(blob)
            videoURL = urlCreator.createObjectURL(blob);
            video.src = videoURL;

        } else {

            let response = JSON.parse(e.data);
            // console.log(response)
            let type = response.type;
            // console.log(type)

            if (type === 'connection') {
                console.log(response.data.message)
            }

            if (type === 'video_stream') {
                // console.log(response.data.frame;);
                let arrayBufferView = new Uint8Array(response.data.frame);
                let blob = new Blob([arrayBufferView], {type: "image/jpeg"});
                // console.log(blob);
                videoURL = urlCreator.createObjectURL(blob);
                video.src = videoURL;
            }
        }
    }


    streamSocket.onerror = (e) => {
        console.log(e);
    }
}

