document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("emailForm");

    if (form) {

        form.addEventListener("submit", function () {

            const button = document.getElementById("checkButton");

            if (button) {

                button.disabled = true;

                button.innerHTML = "⏳ Checking Emails...";

            }

        });

    }


    // Show / Hide App Password

    const passwordInput =
        document.getElementById("app_password");

    const togglePassword =
        document.getElementById("togglePassword");

    if (passwordInput && togglePassword) {

        togglePassword.addEventListener(
            "click",
            function () {

                if (passwordInput.type === "password") {

                    passwordInput.type = "text";

                    togglePassword.innerHTML = "🙈";

                } else {

                    passwordInput.type = "password";

                    togglePassword.innerHTML = "👁️";

                }

            }
        );

    }

});