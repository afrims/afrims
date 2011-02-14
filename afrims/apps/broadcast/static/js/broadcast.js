$(document).ready(function() {
    $('.datetimepicker').datetimepicker();
    $('.multiselect').multiselect({header: false});
    
    $('#id_body').parents('tr').addClass('body');
    
    $('#id_when').change(function() {
        var value = $(this).val();
        var tr = $(this).parents('tr');
        var siblings = tr.nextUntil('tr.body');
        if (value == 'now') {
            $(siblings).hide();
        } else {
            $(siblings).show();
        }
    }).change();
});

