from enum import Enum

# pylint: disable=no-name-in-module
from pydantic import BaseModel, Field

# pylint: enable=no-name-in-module


class EngineEnum(str, Enum):
    postgresql = "postgresql"
    mysql = "mysql"


class SecurityEnum(str, Enum):
    jwt = "jwt"
    cognito = "cognito"
    auth0 = "auth0"
    firebase = "firebase"
    keycloak = "keycloak"
    ldap = "ldap"


class LogLevelEnum(str, Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"


class LogSizeEnum(str, Enum):
    kb = "kb"
    mb = "mb"


class Docker(BaseModel):
    up: bool = False
    down: bool = False
    dash: bool = False
    file: str = "."


class OpenApi(BaseModel):
    include: bool = True
    servers: dict[str, str] = {}


class App(BaseModel):
    port: int = 8000
    name: str = "OklahomaApp"
    version: str = "0.1.0"
    prod: bool = False
    test: bool = False
    docker: Docker = Docker()
    openapi: OpenApi = OpenApi()


class Database(BaseModel):
    upgrade_at_start: bool = Field(True, alias="upgrade-at-start")
    host: str | None = None
    port: int | None = None
    database: str | None = None
    user: str | None = None
    password: str | None = None
    engine: EngineEnum = EngineEnum.postgresql


class Aws(BaseModel):
    secrets: dict[str, str] = {}
    endpoint: str | None = None
    region: str | None = None


class Security(BaseModel):
    provider: SecurityEnum = SecurityEnum.jwt
    cognito_pool_id: str | None = Field(None, alias="cognito-pool-id")
    endpoint: str | None = None


class Rabbit(BaseModel):
    host: str = "localhost"
    port: int = 5672


class LogRotation(BaseModel):
    size: int = 1
    unit: LogSizeEnum = LogSizeEnum.mb
    keep: int = 10


class Cloudwatch(BaseModel):
    stream: str | None = None
    retention: int | None = 7
    use: bool = False


class Log(BaseModel):
    folder: str = "logs"
    file: str | None = None
    level: LogLevelEnum = LogLevelEnum.info
    rotation: LogRotation = LogRotation()
    cloudwatch: Cloudwatch = Cloudwatch()


class Profile(BaseModel):
    app: App = App()
    database: Database = Database()  # type: ignore
    aws: Aws = Aws()
    secrets: dict[str, dict[str, str]] = {}
    security: Security = Security()  # type: ignore
    rabbit: Rabbit = Rabbit()
    log: Log = Log()
