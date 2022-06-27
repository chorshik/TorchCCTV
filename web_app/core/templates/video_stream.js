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

  streamSocket.onopen = event => {
    streamSocket.send(JSON.stringify({
        type: 'receive',
        data: {
            hostname: hostname
        }
    }));

  streamSocket.onmessage = (e) => {
      let resp
      if(e.data instanceof ArrayBuffer) {
        // console.log(e)
        resp = e.data

        let arrayBufferView = new Uint8Array(resp);
        let blob = new Blob([arrayBufferView], {type: "image/jpeg"});
        // console.log(blob)
        videoURL = urlCreator.createObjectURL(blob);
        video.src = videoURL;

      } else {

          let response = JSON.parse(e.data);
          // console.log(response)
          let type = response.type;
          // console.log(type)

          if (type == 'connection') {
              console.log(response.data.message)
          }
      }
  }
}
}