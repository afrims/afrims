/* test_messager.js
 */

$.widget("ui.messager", {
    options: {
        'url': '/test-messager/form/',
    },
    _create: function() {
        var self = this;
        var dialog = $('<div>').dialog({
            autoOpen: false,
            title: 'Send Test Message',
            modal: true,
            resizable: false,
            width: 400,
            open: function (e, ui) {
                $.getJSON(self.options.url, {'message': self.element.val()}, function(data) {
                    self._handle_response(data);
                });
            },
        });
        self.element.data('dialog', dialog.data('dialog'));
        // create button next to field
        var button = $('<a>').attr('href', '#').text('Send Test Message');
        button.click(function (e) {
            dialog.dialog('open');
        });
        button.button();
        this.element.after($('<div>').append(button));
    },
    _handle_response: function (data) {
        this._draw_form(data);
    },
    _draw_form: function(data) {
        var self = this;
        var dialog = self.element.data('dialog');
        var $element = dialog.element;
        $element.html(data.form);
        var submit = $element.find('input:submit');
        submit.button();
        submit.click(function (e) {
            var form = $(this.form);
            var query = form.serialize();
            $.post(self.options.url, query, function (data) {
                self._handle_response(data);
            });
        });
        console.log($element.find('form'));
        $element.find('form').submit(function(e) {
            e.preventDefault();
            
            
        });
            
        
    }
});

$(document).ready(function() {
    $('.test-messager-field').messager();
});

