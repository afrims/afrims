$(document).ready(function() {
    $('input[name$="time_of_day"]').timepicker({});
    $('input.datepicker').datepicker();
    $('.form-action input[type=submit]').button();
    $('#tabs li.app-appointmentreminders').addClass('active');
});
