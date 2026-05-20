const imageInput = document.getElementById('imageInput');
const originalPreview = document.getElementById('originalPreview');
const sketchPreview = document.getElementById('sketchPreview');
const downloadBtn = document.getElementById('downloadBtn');

const cameraBtn = document.getElementById('cameraBtn');
const captureBtn = document.getElementById('captureBtn');
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');

let stream;


imageInput.addEventListener('change', async () => {

    const file = imageInput.files[0];

    if (!file) return;

    originalPreview.src = URL.createObjectURL(file);

    uploadImage(file);
});


cameraBtn.addEventListener('click', async () => {

    try {

        stream = await navigator.mediaDevices.getUserMedia({
            video: true
        });

        video.srcObject = stream;

        video.classList.remove('hidden');
        captureBtn.classList.remove('hidden');

    } catch (error) {
        alert('Camera access denied');
    }
});


captureBtn.addEventListener('click', async () => {

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');

    ctx.drawImage(video, 0, 0);

    canvas.toBlob(async (blob) => {

        const file = new File([blob], 'camera_capture.png', {
            type: 'image/png'
        });

        originalPreview.src = URL.createObjectURL(file);

        uploadImage(file);

    }, 'image/png');

    stream.getTracks().forEach(track => track.stop());

    video.classList.add('hidden');
    captureBtn.classList.add('hidden');
});


async function uploadImage(file) {

    const formData = new FormData();

    formData.append('image', file);

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    if (data.success) {

        sketchPreview.src = data.sketch + '?t=' + new Date().getTime();

        downloadBtn.href = data.download;

        downloadBtn.classList.remove('hidden');

    } else {
        alert(data.error);
    }
}