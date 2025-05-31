from enum import Enum
import enum


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

# 🔹 Définir un Enum Python pour les statuts
class AppStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"