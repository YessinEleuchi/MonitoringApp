from enum import Enum

class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

class ResponseFormat(str, Enum):
    JSON = "JSON"
    XML = "XML"
    TEXT = "TEXT"
