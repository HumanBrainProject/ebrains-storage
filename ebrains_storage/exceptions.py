class ClientHttpError(Exception):
    """This exception is raised if the returned http response is not as
    expected"""

    def __init__(self, code, message):
        super(ClientHttpError, self).__init__()
        self.code = code
        self.message = message

    def __str__(self):
        return "ClientHttpError[%s: %s]" % (self.code, self.message)


class OperationError(Exception):
    """Expcetion to raise when an opeartion is failed"""

    pass


class DoesNotExist(Exception):
    """Raised when not matching resource can be found."""

    def __init__(self, msg):
        super(DoesNotExist, self).__init__()
        self.msg = msg

    def __str__(self):
        return "DoesNotExist: %s" % self.msg


class Unauthorized(Exception):

    def __init__(self, msg):
        super().__init__()
        self.msg = msg

    def __str__(self):
        return "Unauthorized. This could be a result of either incorrect path or insufficient privilege. %s" % self.msg


class InvalidParameter(Exception):
    pass


class TokenExpired(Exception):
    pass


class UpstreamAPIException(Exception):
    """This exception is raised if the upstream API returns something unexpected"""
