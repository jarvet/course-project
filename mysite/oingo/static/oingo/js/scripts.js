// Empty JS for your own code to be here
var from_date = document.getElementById('from_date');
var to_date = document.getElementById('to_date');

from_date.addEventListener('change', function() {
    if (from_date.value)
        to_date.min = from_date.value;
}, false);
to_date.addEventListener('change', function() {
    if (to_date.value)
        from_date.max = to_date.value;
}, false);


function verify() {
    var start_time = $("#start_time").val();
    var end_time = $("#end_time").val();
    if (start_time > end_time) {
        alert('start time should before end time');
        return false;
    }
};