document.getElementById("menu-toggle").addEventListener("click", function() {
    document.getElementById("wrapper").classList.toggle("toggled");
});

// Scroll Animations
window.addEventListener('scroll', function() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    elements.forEach(element => {
        const position = element.getBoundingClientRect().top;
        if (position < window.innerHeight) {
            element.classList.add('fade-in');
        }
    });
});
