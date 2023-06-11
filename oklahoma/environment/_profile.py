from enum import Enum

# pylint: disable=no-name-in-module,too-few-public-methods
from pydantic import BaseModel, Field

# pylint: enable=no-name-in-module


# pylint: disable=invalid-name
class EngineEnum(str, Enum):
    """Enum for database engine"""

    postgresql = "postgresql"
    mysql = "mysql"


class SecurityEnum(str, Enum):
    """Enum for security provider"""

    jwt = "jwt"
    cognito = "cognito"
    auth0 = "auth0"
    firebase = "firebase"
    keycloak = "keycloak"
    ldap = "ldap"


class LogLevelEnum(str, Enum):
    """Enum for log level"""

    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"


class LogSizeEnum(str, Enum):
    """Enum for kilobytes or megabytes or \
        trilobites."""

    kb = "kb"
    mb = "mb"


# pylint:enable=invalid-name
class Docker(BaseModel):
    """Section for docker options"""

    up: bool = False
    down: bool = False
    dash: bool = False
    file: str = "."


class OpenApi(BaseModel):
    """Section for OpenAPI options"""

    include: bool = True
    servers: dict[str, str] = {}


class App(BaseModel):
    """Section for app options"""

    port: int = 8000
    name: str = "OklahomaApp"
    version: str = "0.1.0"
    prod: bool = False
    test: bool = False
    docker: Docker = Docker()
    openapi: OpenApi = OpenApi()


class Database(BaseModel):
    """Section for database options"""

    upgrade_at_start: bool = Field(True, alias="upgrade-at-start")
    host: str | None = None
    port: int | None = None
    database: str | None = None
    user: str | None = None
    password: str | None = None
    engine: EngineEnum = EngineEnum.postgresql


class Aws(BaseModel):
    """Section for AWS options"""

    secrets: dict[str, str] = {}
    endpoint: str | None = None
    region: str | None = None


class Security(BaseModel):
    """Section for security options"""

    provider: SecurityEnum = SecurityEnum.jwt
    cognito_pool_id: str | None = Field(None, alias="cognito-pool-id")
    endpoint: str | None = None


class Rabbit(BaseModel):
    """Section for RabbitMQ options"""

    host: str = "localhost"
    port: int = 5672


class LogRotation(BaseModel):
    """Section for log rotation options"""

    size: int = 1
    unit: LogSizeEnum = LogSizeEnum.mb
    keep: int = 10


class Cloudwatch(BaseModel):
    """Section for cloudwatch options"""

    stream: str | None = None
    retention: int | None = 7
    use: bool = False


class Log(BaseModel):
    """Section for log options"""

    folder: str = "logs"
    file: str | None = None
    level: LogLevelEnum = LogLevelEnum.info
    rotation: LogRotation = LogRotation()
    cloudwatch: Cloudwatch = Cloudwatch()


class Profile(BaseModel):
    """The profile model, with all its defaults"""

    app: App = App()
    database: Database = Database()  # type: ignore
    aws: Aws = Aws()
    secrets: dict[str, dict[str, str]] = {}
    security: Security = Security()  # type: ignore
    rabbit: Rabbit = Rabbit()
    log: Log = Log()
