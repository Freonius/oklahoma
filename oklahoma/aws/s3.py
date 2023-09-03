from typing import TYPE_CHECKING
from boto3 import client

if TYPE_CHECKING is True:
    from boto3_type_annotations.s3 import Client


class S3:
    _client: "Client"
    _bucket_name: str
    _auto_create: bool

    def __init__(
        self,
        bucket_name: str,
        endpoint: str | None = None,
        region: str | None = None,
        auto_create: bool = __debug__,
    ) -> None:
        self._auto_create = auto_create
        self._bucket_name = bucket_name
        self._client = client(
            "s3",
            endpoint_url=endpoint,
            region_name=region,
        )
