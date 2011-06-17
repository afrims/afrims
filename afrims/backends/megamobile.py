from rapidsms.backends.http import RapidHttpBackend


class MegaMobileBackend(RapidHttpBackend):
    default_timeout = 8

    def configure(self, host="localhost", port=8080, config=None, **kwargs):
        if "params_incoming" not in kwargs:
            kwargs["params_incoming"] = "cel=%(phone_number)s&msg=%(message)s"
        if "params_outgoing" not in kwargs:
            kwargs["params_outgoing"] = "cel=%(phone_number)s&msg=%(message)s&pid=0"
        if "gateway_url" not in kwargs:
            kwargs["gateway_url"] = "http://api.mymegamobile.com/api.php"
        super(MegaMobileBackend, self).configure(host, port, **kwargs)
        self.config = config
