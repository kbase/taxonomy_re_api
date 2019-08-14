"""Exception classes."""


class InvalidParams(Exception):
    pass


class REError(Exception):
    """Error from the RE API."""

    def __init__(self, resp):
        """Takes a requests response object."""
        self.resp_json = None
        try:
            body = resp.json()
            self.resp_json = body
        except ValueError:
            pass
        self.resp_text = resp.text
