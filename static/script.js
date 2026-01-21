flatpickr("#datePicker", {
    minDate: "today",
    dateFormat: "Y-m-d"
});

function submitDate() {
    const date = document.getElementById("datePicker").value;
    if (!date) {
        alert("Please select a date");
        return;
    }
    window.location.href = "/?date=" + date;
}
