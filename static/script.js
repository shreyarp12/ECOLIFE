document.addEventListener("DOMContentLoaded", function () {

    // Smooth scrolling
    document.querySelectorAll("a[href^='#']").forEach(function (link) {

        link.addEventListener("click", function (event) {

            const target = document.querySelector(
                this.getAttribute("href")
            );

            if (target) {

                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth"
                });

            }

        });

    });


    // Automatically hide alerts
    setTimeout(function () {

        document.querySelectorAll(".alert").forEach(function (alert) {

            alert.style.transition = "opacity 0.5s";

            alert.style.opacity = "0";

            setTimeout(function () {
                alert.remove();
            }, 500);

        });

    }, 5000);

});
