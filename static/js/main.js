document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("question-form");
    if (!form) return;
    form.addEventListener("submit", function (e) {
        var required = form.getAttribute("data-required") === "true";
        if (!required) return;
        var type = form.getAttribute("data-question-type");
        var valid = true;
        if (type === "single_choice" || type === "multiple_choice") {
            valid = form.querySelectorAll('input[name="answer"]:checked').length > 0;
        } else if (type === "text_input") {
            var ta = form.querySelector('textarea[name="answer"]');
            valid = ta && ta.value.trim().length > 0;
        } else if (type === "number_input") {
            var num = form.querySelector('input[name="answer"]');
            valid = num && num.value.trim().length > 0;
        }
        if (!valid) {
            e.preventDefault();
            var warn = document.getElementById("required-warning");
            if (warn) warn.style.display = "block";
        }
    });
});
