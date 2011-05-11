/* test_messager.js
 *
 * jQuery UI widget for test_messager RapidSMS app that allows sending
 * test messages to a backend/identity pair via an AJAX jQuery dialog.
 *
 * By default, widget will install to .test-messager-field elements:
 * <textarea class="test-messager-field" name="body"></textarea>
 * ...
 * $('.test-messager-field').messager();
 */

$.widget("ui.messager", {
    options: {
        'url': '/test-messager/form/'
    },
    _create: function() {
        var self = this;
        var dialog = $('<div>').dialog({
            autoOpen: false,
            title: 'Send Test Message',
            modal: true,
            resizable: false,
            open: function (e, ui) {
                $.getJSON(self.options.url, {'message': self.element.val()}, function(data) {
                    self._handle_response(data);
                });
            }
        });
        self.element.data('dialog', dialog.data('dialog'));
        // create button next to field
        var button = $('<a>').attr('href', '#').text('Send Test Message');
        button.click(function (e) {
            var enabled = !$(this).button("option", "disabled");
            if (enabled) {
                dialog.dialog('open');
            }
        });
        button.button();
        button.button('disable');
        self.element.after($('<div>').append(button));
        // only enable button if there is text to send
        self.element.keyup(function(e) {
            var size = $(this).val().length;
            if (size == 0) {
                button.button('disable');
            } else {
                button.button('enable');
            }
        });
        self.element.keyup();
    },
    _handle_response: function (data) {
        if (data.success === true) {
            console.log(this.element.data('dialog'));
            this.element.data('dialog').close();
        } else {
            this._draw_form(data);
        }
    },
    _draw_form: function(data) {
        var self = this;
        var dialog = self.element.data('dialog');
        var $element = dialog.element;
        $element.empty();
        if (data.success === false) {
            $element.append($('<h2>').text('Message Failure'));
            $element.append($('<p>').text(data.status));
        }
        $element.append(data.form);
        var submit = $element.find('input:submit');
        submit.button();
        submit.click(function (e) {
            var form = $(this.form);
            var query = form.serialize();
            $.post(self.options.url, query, function (data) {
                self._handle_response(data);
            });
        });
        $element.find('form').submit(function(e) {
            e.preventDefault();
        });
    }
});

// By default, install on all .test-messager-field elements
$(document).ready(function() {
    $('.test-messager-field').messager();
});

