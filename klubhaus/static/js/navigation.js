document.addEventListener('DOMContentLoaded', () => {

    const navbar_burgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

    navbar_burgers.forEach(element => {
        element.addEventListener('click', () => {

            const target = document.getElementById(element.dataset.target);

            element.classList.toggle('is-active');
            target.classList.toggle('is-active');

        });
    });

});
