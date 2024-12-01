document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll(".nav-link"); // Select all navbar links
    const currentPath = window.location.pathname; // Get the current URL path

    links.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active"); // Add 'active' class to the matching link
        }
    });
});
