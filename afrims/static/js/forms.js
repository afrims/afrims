/* forms.js
 * General, shared javascript form functionality
 */
$(document).ready(function() {
    $("form.buttons input[name=submit], form.buttons button[name=cancel]").button();
    $("form.buttons button[name=cancel]").click(function(e) {
        history.go(-1);
    });
});

