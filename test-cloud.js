const cloudName = 'qfpgpfqk';
const uploadPreset = 'LpskCq8FvbDgBwzGjiTTwHzAhCg';
const formData = new FormData();
formData.append('upload_preset', uploadPreset);
const base64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';
formData.append('file', 'data:image/png;base64,' + base64);
fetch(`https://api.cloudinary.com/v1_1/${cloudName}/image/upload`, {
  method: 'POST',
  body: formData
}).then(res => res.json()).then(console.log).catch(console.error);
