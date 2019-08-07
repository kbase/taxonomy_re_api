"""Exception classes."""


class InvalidParams(Exception):
    pass


class REError(Exception):
    """Error from the RE API."""

    def __init__(self, resp):
        """Takes a requests response object."""
        try:
            body = resp.json()
            self.resp_json = body
        except ValueError:
            self.resp_json = None
        self.resp_text = resp.text
