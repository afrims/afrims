from django.utils.functional import curry
from rapidsms.contrib.ajax.utils import call_router


# these helper methods are just proxies to app.py
'''Send a broadcast message, use params, identity, text, recipients (== contacts list)'''
send_broadcast_message = curry(call_router, "broadcast", "send")


get_message_log   = curry(call_router, "broadcast", "log")