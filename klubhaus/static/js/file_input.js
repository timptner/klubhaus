{
    const file_inputs = document.querySelectorAll('input[type=file]');

    file_inputs.forEach(file_input => {
        file_input.onchange = () => {
            if (file_input.files.length > 0) {
                const file_name = file_input.parentElement.querySelector('.file-name');
                file_name.textContent = file_input.files[0].name;
                file_name.classList.remove('is-italic', 'has-text-grey-light');
            }
        }
    })
}
