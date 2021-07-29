from enum import Enum

class TableServiceErrorCode(Enum):
    ALREADY_EXISTS = "already_exists"
    NOT_EXISTS = "not_exists"
    GRAPHQL_ERROR = "graphql_error"
    INVALID = "invalid"
    NOT_FOUND = "not_found"
    REQUIRED = "required"
    UNIQUE = "unique"
