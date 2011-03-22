/* forms.js
 * General, shared javascript functionality
 */
$(document).ready(function() {
    $('a.button').button({text: false});
    $('a.button.add').button("option", "icons", {primary: 'ui-icon-circle-plus'});
    $('a.button.add').button("option", "text", true);
});
