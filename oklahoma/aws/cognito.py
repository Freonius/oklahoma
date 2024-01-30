from typing import TYPE_CHECKING
from boto3 import client
from fastapi import Request
from ..environment import environ

if TYPE_CHECKING is True:
    from boto3_type_annotations.cognito_idp import Client


class CognitoException(Exception):
    pass


class Cognito:
    _client: "Client"
    _is_local: bool = False
    _pool_id: str
    _client_id: str

    def __init__(
        self, pool_name: str | None = None, client_name: str | None = None
    ) -> None:
        self._is_local = environ.profile.aws.cognito_endpoint is not None

        self._client = client(
            "cognito-idp",
            endpoint_url=environ.profile.aws.cognito_endpoint,
            region_name=environ.profile.aws.region,
        )

        if pool_name is None:
            pool_name = environ.profile.security.cognito_pool_id
        if client_name is None:
            client_name = environ.profile.security.cognito_client_id
        if pool_name is None and "COGNITO_POOL_ID" in environ:
            pool_name = environ["COGNITO_POOL_ID"]
        if client_name is None and "COGNITO_CLIENT_ID" in environ:
            client_name = environ["COGNITO_CLIENT_ID"]
        if pool_name is None or client_name is None:
            raise CognitoException("Pool name cannot be None")

        self.create_pool(pool_name, client_name)

    @property
    def client(self) -> "Client":
        return self._client

    def create_pool(
        self,
        pool_name: str,
        client_name: str | None = None,
    ) -> None:
        """
        If the pool/client already exist, it will not recreate it.
        """
        list_of_pools: dict[
            str, list[dict[str, object]]
        ] = self._client.list_user_pools(
            MaxResults=30,
        )
        pool_id: str | None = None
        for x in list_of_pools["UserPools"]:
            if x["Name"] == pool_name:
                if isinstance(x["Id"], str):
                    pool_id = x["Id"]
                    break
        if pool_id is None:
            res: dict[str, dict[str, str]] = self._client.create_user_pool(
                PoolName=pool_name
            )
            pool_id = res["UserPool"]["Id"]
        clients: dict[str, list[dict[str, str]]] = self._client.list_user_pool_clients(
            UserPoolId=pool_id
        )
        client_id: str | None = None
        for y in clients["UserPoolClients"]:
            if client_name is not None:
                if y["ClientName"] == client_name:
                    client_id = y["ClientId"]
                    break
            else:
                # Get the first
                client_id = y["ClientId"]
                break
        if client_id is None and client_name is None:
            client_name = pool_name
        if client_id is None:
            create: dict[str, dict[str, str]] = self._client.create_user_pool_client(
                UserPoolId=pool_id, ClientName=client_name
            )
            client_id = create["UserPoolClient"]["ClientId"]
        if self._is_local:
            environ[
                "AWS_COGNITO_JWKS_PATH"
            ] = f"{environ.profile.aws.cognito_endpoint}/{pool_id}/.well-known/jwks.json"
        self._pool_id = pool_id
        self._client_id = client_id

    def find_users_by_group(self, *groups: str) -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        for group in groups:
            res = self._client.list_users_in_group(
                UserPoolId=self._pool_id, GroupName=group
            )
            for x in res["Users"]:
                usr: dict[str, str] = {}
                for y in x["Attributes"]:
                    usr[y["Name"]] = y["Value"]
                out.append(usr)
        return out

    def list_users(self) -> list[dict[str, str]]:
        res = self._client.list_users(UserPoolId=self._pool_id)
        out: list[dict[str, str]] = []
        for x in res["Users"]:
            usr: dict[str, str] = {}
            for y in x["Attributes"]:
                usr[y["Name"]] = y["Value"]
            out.append(usr)
        return out

    def find_user_by_email(self, email: str) -> dict[str, str] | None:
        res = self._client.list_users(UserPoolId=self._pool_id)
        for x in res["Users"]:
            if x["Username"] == email:
                usr: dict[str, str] = {}
                for y in x["Attributes"]:
                    usr[y["Name"]] = y["Value"]
                return usr
        return None

    def find_by_attribute(self, key: str, value: str) -> dict[str, str] | None:
        res = self._client.list_users(
            UserPoolId=self._pool_id, Filter=f'{key}="{value}"'
        )
        for x in res["Users"]:
            usr: dict[str, str] = {}
            for y in x["Attributes"]:
                usr[y["Name"]] = y["Value"]
            return usr
        return None

    def create_group(self, group_name: str) -> None:
        res: dict[str, list[dict[str, str]]] = self._client.list_groups(
            UserPoolId=self._pool_id
        )
        for x in res["Groups"]:
            if x["GroupName"] == group_name:
                return
        self._client.create_group(UserPoolId=self._pool_id, GroupName=group_name)

    def admin_create_user(
        self,
        email: str,
        temporary_password: str | None,
        attributes: dict[str, str] | None = None,
        *,
        group: list[str] | str | None = None,
        auto_verify: bool = False,
        send_sms: bool = True,
        resend: bool = False,
        send_email: bool = True,
        suppress: bool = False,
    ) -> dict[str, str]:
        """
        Create a user and return its attributes.

        Args:
            email (str): Email address
            temporary_password (str): Temporary password, the user will need to change it.
            attributes (Union[dict[str, str], None], optional): Dictionary of attributes to pass, like first name, last name, et c.. Defaults to None.
            group (Union[list[str], str, None], optional): Add the user to a group or list of groups. Defaults to None.
            auto_verify (bool, optional): If set to true, it will automatically confirm the signup. Defaults to False.

        Returns:
            dict[str, str]: _description_
        """
        notify_methods: list[str] = []
        if send_email is True:
            notify_methods.append("EMAIL")
        if attributes is None:
            attributes = {}
        if send_sms is True and "phone_number" in attributes.keys():
            notify_methods.append("SMS")
        if auto_verify is True:
            attributes["email_verified"] = "true"
        attributes["email"] = email
        _kwargs: dict[str, object] = {
            "UserPoolId": self._pool_id,
            "Username": email,
            "DesiredDeliveryMediums": notify_methods,
            "UserAttributes": [{"Name": k, "Value": v} for k, v in attributes.items()],
        }
        if temporary_password is not None:
            _kwargs["TemporaryPassword"] = temporary_password
        if resend is True:
            _kwargs["MessageAction"] = "RESEND"
        if suppress is True:
            _kwargs["MessageAction"] = "SUPPRESS"
        res = self._client.admin_create_user(**_kwargs)
        if group is not None:
            if isinstance(group, str):
                group = [group]
            for x in group:
                self.create_group(x)
                self._client.admin_add_user_to_group(
                    UserPoolId=self._pool_id, Username=email, GroupName=x
                )
        out: dict[str, str] = {}
        for at in res["User"]["Attributes"]:
            out[at["Name"]] = at["Value"]
        return out

    def sign_up(
        self,
        email: str,
        password: str,
        attributes: dict[str, str] | None = None,
        group: list[str] | str | None = None,
        auto_verify: bool = False,
    ) -> None:
        if attributes is None:
            attributes = {}
        attributes["email"] = email
        self._client.sign_up(
            ClientId=self._client_id,
            Username=email,
            Password=password,
            UserAttributes=[{"Name": k, "Value": v} for k, v in attributes.items()],
        )
        if auto_verify is True:
            self._client.admin_confirm_sign_up(UserPoolId=self._pool_id, Username=email)
        if group is not None:
            if isinstance(group, str):
                group = [group]
            for x in group:
                self.create_group(x)
                self._client.admin_add_user_to_group(
                    UserPoolId=self._pool_id, Username=email, GroupName=x
                )

    def delete_user(self, email: str) -> None:
        self._client.admin_delete_user(UserPoolId=self._pool_id, Username=email)

    def get_access_token(self, username: str, password: str) -> tuple[str, str, str]:
        res: dict[str, dict[str, str]] = self._client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password},
            ClientId=self._client_id,
        )
        if "AuthenticationResult" not in res.keys():
            raise Exception("Could not authenticate")
        for x in ("AccessToken", "RefreshToken", "IdToken"):
            if x not in res["AuthenticationResult"].keys():
                raise Exception("Could not authenticate")
        return (
            res["AuthenticationResult"]["AccessToken"],
            res["AuthenticationResult"]["RefreshToken"],
            res["AuthenticationResult"]["IdToken"],
        )

    def get_username(self, token: str) -> str:
        res: dict[str, str] = self._client.get_user(AccessToken=token)
        return res["Username"]

    def user_in_group(self, username: str, *groups: str, just_one: bool = True) -> bool:
        got_groups: list[str] = []
        res: dict[str, list[dict[str, str]]] = self._client.admin_list_groups_for_user(
            Username=username,
            UserPoolId=self._pool_id,
        )
        for x in res["Groups"]:
            got_groups.append(x["GroupName"])
        if just_one is True:
            return any([x in got_groups for x in groups])
        return all([x in got_groups for x in groups])

    def check(self, request: Request, *groups: str, must_be_in_all: bool) -> str:
        header: str = ""
        if (
            "COGNITO_JWT_HEADER_NAME" in environ
            and len(environ["COGNITO_JWT_HEADER_NAME"].strip()) > 0
        ):
            header = environ["COGNITO_JWT_HEADER_NAME"].strip()
        else:
            header = "Authorization"
        prefix: str = ""
        if (
            "COGNITO_JWT_HEADER_PREFIX" in environ
            and len(environ["COGNITO_JWT_HEADER_PREFIX"].strip()) > 0
        ):
            prefix = environ["COGNITO_JWT_HEADER_PREFIX"].strip()
        else:
            prefix = "Bearer"
        token: str = request.headers.get(header, "")
        if token.strip() == "":
            raise CognitoException()
        if token.startswith(prefix + " "):
            token = token.replace(prefix + " ", "").strip()
        try:
            username = self.get_username(token)
            if self.user_in_group(username, *groups, just_one=not must_be_in_all):
                return username
            raise Exception()
        except:
            raise CognitoException()

    def forgot_password(self, email: str) -> None:
        self._client.forgot_password(
            ClientId=self._client_id,
            Username=email,
        )

    def confirm_forgot_password(
        self, email: str, new_password: str, confirm_code: str
    ) -> None:
        self._client.confirm_forgot_password(
            ClientId=self._client_id,
            Username=email,
            ConfirmationCode=confirm_code,
            Password=new_password,
        )
