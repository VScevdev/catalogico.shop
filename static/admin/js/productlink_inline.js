document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ ProductLink inline JS cargado");

    function applyRule(row) {
        const linkType = row.querySelector('select[name$="-link_type"]');
        const buttonInput = row.querySelector('input[name$="-button_text"]');

        if (!linkType || !buttonInput) return;

        if (linkType.value === "external") {
            buttonInput.disabled = false;
            buttonInput.placeholder = "Texto del botón";
        } else {
            buttonInput.disabled = true;
            buttonInput.value = ""; // se fuerza desde backend
            buttonInput.placeholder = "Automático";
        }
    }

    function initRow(row) {
        applyRule(row);

        const linkType = row.querySelector('select[name$="-link_type"]');
        if (linkType) {
            linkType.addEventListener("change", function () {
                applyRule(row);
            });
        }
    }

    document.querySelectorAll(".inline-related").forEach(initRow);

    document.body.addEventListener("formset:added", function (event) {
        initRow(event.target);
    });
});
