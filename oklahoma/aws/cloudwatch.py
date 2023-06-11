from typing import TYPE_CHECKING
from boto3 import client
from botocore.exceptions import ClientError

if TYPE_CHECKING is True:
    from boto3_type_annotations.logs import Client


class CloudWatchLogs:
    """Class for CloudWatch logs"""

    _group_name: str
    _client: "Client"

    def __init__(
        self,
        group_name: str,
        endpoint: str | None = None,
        region: str | None = None,
    ) -> None:
        """CloudWatchLogs

        Args:
            group_name (str): Log group name
            endpoint (str | None, optional): If you want to use\
                localstack, add this with localstack's\
                    address. Defaults to None.
            region (str | None, optional): If you want to specify\
                the region. Defaults to None.
        """
        self._group_name = group_name
        self._client = client(
            "logs",
            endpoint_url=endpoint,
            region_name=region,
        )

    @property
    def client(self) -> "Client":
        """boto3 client for cloudwatch logs"""
        return self._client

    def create(
        self,
        *,
        stream_name: str | None = None,
        retention_days: int | None = None,
        tags: dict[str, str] | None = None,
        raise_on_error: bool = False,
    ) -> bool:
        """Create an alarm if it does not exist

        Args:
            stream_name (str | None, optional): Stream name. Defaults to None.
            retention_days (int | None, optional): Retention days. Defaults to None.
            tags (dict[str, str] | None, optional): Tags. Defaults to None.
            raise_on_error (bool, optional): Raise on error or \
                suppress. Defaults to False.

        Raises:
            ClientError: If raise on error is set to true and\
                there are problems with boto3

        Returns:
            bool: The result
        """
        try:
            need_to_create: bool = True
            res = self._client.describe_log_groups()
            for log_group in res["logGroups"]:
                if log_group["logGroupName"] == self._group_name:
                    need_to_create = False
            if need_to_create is True:
                args: dict[str, object] = {"logGroupName": self._group_name}
                if tags is not None:
                    args["tags"] = tags
                self._client.create_log_group(**args)
            if retention_days is not None:
                self._client.put_retention_policy(
                    logGroupName=self._group_name, retentionInDays=retention_days
                )
            if stream_name is not None:
                need_to_create = True
                res_stream = self._client.describe_log_streams(
                    logGroupName=self._group_name
                )
                for log_stream in res_stream["logStreams"]:
                    if log_stream["logStreamName"] == stream_name:
                        need_to_create = False
                if need_to_create is True:
                    self._client.create_log_stream(
                        logGroupName=self._group_name,
                        logStreamName=stream_name,
                    )
            return True
        except ClientError as ex:
            if raise_on_error is True:
                raise ex
            return False
