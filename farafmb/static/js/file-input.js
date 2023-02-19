const form = document.querySelector('form.has-file-input');
const fileInputs = form.querySelectorAll('input[type=file]');
fileInputs.forEach((fileInput) => {
    fileInput.onchange = () => {
        if (fileInput.files.length > 0) {
            const fileName = fileInput.parentNode.querySelector('.file-name');
            fileName.textContent = fileInput.files[0].name;
        }
    }
})
