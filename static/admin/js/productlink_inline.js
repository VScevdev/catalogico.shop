function lockField(field) {
    field.setAttribute("readonly", "readonly");
    field.value = "";
    field.style.backgroundColor = "var(--darkened-bg)";
    field.style.color = "var(--body-fg)";
}

function unlockField(field) {
    field.removeAttribute("readonly");
    field.style.backgroundColor = "var(--body-bg)";
    field.style.color = "var(--body-fg)";
}

document.addEventListener("DOMContentLoaded", function () {

    function toggleExternal(row) {
        const type = row.querySelector('select[name$="-link_type"]');
        const url = row.querySelector('input[name$="-url"]');
        const text = row.querySelector('input[name$="-button_text"]');

        if (!type || !url || !text) return;

        if (type.value === "external") {
            unlockField(url);
            unlockField(text);
        } else {
            lockField(url);
            lockField(text);
        }
    }

    document.querySelectorAll(".inline-related").forEach(row => {
        toggleExternal(row);
        const select = row.querySelector('select[name$="-link_type"]');
        if (select) {
            select.addEventListener("change", () => toggleExternal(row));
        }
    });

    document.body.addEventListener("formset:added", function (e) {
        toggleExternal(e.target);
    });
});
