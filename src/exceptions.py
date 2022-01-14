"""Exception classes."""


class ParseError(Exception):
    code = -32700


class InvalidRequest(Exception):
    code = -32600


class MethodNotFound(Exception):
    code = -32601

    def __init__(self, method_name):
        self.method_name = method_name


class InvalidParams(Exception):
    code = -32602


class InternalError(Exception):
    code = -32603


class ServerError(Exception):
    code = -32000


class REError(Exception):
    """Error from the RE API."""

    def __init__(self, resp):
        """Takes a requests response object."""
        self.resp_json = None
        try:
            self.resp_json = resp.json()
        except ValueError:
            pass
        self.resp_text = resp.text

    def __str__(self):
        return self.resp_text
