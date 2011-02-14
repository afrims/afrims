/* broadcast.js
 * Javascript form functionality for afrims.apps.broadcast RapidSMS app
 */
$(document).ready(function() {
    $('.datetimepicker').datetimepicker();
    $('.multiselect').multiselect({header: false});

    var date_row = $('#id_date').parents('tr').addClass('date-row');
    var frequency_row = $('#id_schedule_frequency').parents('tr').addClass('frequency-row');
    var end_date_row = $('#id_schedule_end_date').parents('tr').addClass('end-date-row');
    var weekdays_row = $('#id_weekdays').parents('tr').addClass('weekdays-row');
    var months_row = $('#id_months').parents('tr').addClass('months-row');
    var body_row = $('#id_body').parents('tr').addClass('body-row');

    function refresh_broadcast_form() {
        var send = $('#id_when').val();
        var frequency = $('#id_schedule_frequency').val();
        if (send == 'now') {
            $(date_row).hide();
            $(frequency_row).hide();
            $(end_date_row).hide();
            $(weekdays_row).hide();
            $(months_row).hide();
        } else {
            $(frequency_row).show();
            if (frequency == 'one-time') {
                $(date_row).show();
                $(end_date_row).hide();
                $(weekdays_row).hide();
                $(months_row).hide();
            } else if (frequency == 'daily') {
                $(end_date_row).show();
                $(weekdays_row).hide();
                $(months_row).hide();
            } else if (frequency == 'weekly') {
                $(weekdays_row).show();
                $(months_row).hide();
            } else if (frequency == 'monthly') {
                $(months_row).show();
                $(weekdays_row).hide();
            } else if (frequency == 'yearly') {
                $(months_row).hide();
                $(weekdays_row).hide();
            }
        }
    }
    refresh_broadcast_form();

    $('#id_when').change(function() {
        refresh_broadcast_form();
    });
    $('#id_schedule_frequency').change(function() {
        refresh_broadcast_form();
    });
});

