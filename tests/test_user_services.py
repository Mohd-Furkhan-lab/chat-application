import pytest

from unittest.mock import patch, AsyncMock

from fastapi import HTTPException

from services.user_services import (
    new_user,
    user_login,
    user_info,
    refresh,
    logout,
    is_expired,
    upload_file
)


# Test Data

class User:
    email = "test@gmail.com"
    password = "password"


class StoredUser:
    user_id = 1
    user_name = "furkhan"
    password = "hashed_password"


class Info:
    user_id = 1
    user_name = "furkhan"
    email = "test@gmail.com"
    password = "hashed_password"


# get_current_user() returns the payload from verify_token()
# so payload must be a dictionary.
Payload = {
    "user_id": 1,
    "user_name": "furkhan",
    "jti": 121
}


access_payload = {
    "user_id": 1,
    "user_name": "furkhan",
    "jti": 121,
    "exp": 1787220600,
    "type": "access"
}


refresh_payload = {
    "user_id": 1,
    "user_name": "furkhan",
    "jti": 1,
    "exp": 1787220600,
    "type": "refresh"
}


# SIGNUP

def test_new_user_success():

    with patch("services.user_services.get_user") as mock_get_user, \
         patch("services.user_services.random_username") as mock_random_username, \
         patch("services.user_services.bcrypt.hashpw") as mock_hashpw, \
         patch("services.user_services.add_user") as mock_add_user:

        mock_get_user.return_value = None
        mock_random_username.return_value = "random_user"
        mock_hashpw.return_value = b"hashed_password"
        mock_add_user.return_value = True

        result = new_user(User())

        assert result == {
            "message": "signed up successfully",
            "user_name": "random_user"
        }

        mock_get_user.assert_called_once_with(User.email)
        mock_random_username.assert_called_once()
        mock_add_user.assert_called_once()


def test_new_user_already_exists():

    with patch("services.user_services.get_user") as mock_get_user:

        mock_get_user.return_value = StoredUser()

        with pytest.raises(HTTPException) as exc:

            new_user(User())

        assert exc.value.status_code == 409
        assert exc.value.detail == "User Already Exists"


def test_new_user_internal_server_error():

    with patch("services.user_services.get_user") as mock_get_user, \
         patch("services.user_services.random_username") as mock_random_username, \
         patch("services.user_services.bcrypt.hashpw") as mock_hashpw, \
         patch("services.user_services.add_user") as mock_add_user:

        mock_get_user.return_value = None
        mock_random_username.return_value = "random_user"
        mock_hashpw.return_value = b"hashed_password"
        mock_add_user.return_value = False

        with pytest.raises(HTTPException) as exc:

            new_user(User())

        assert exc.value.status_code == 500
        assert exc.value.detail == "Internal Server Error"


# LOGIN

def test_user_login_success():

    with patch("services.user_services.get_user") as mock_get_user, \
         patch("services.user_services.bcrypt.checkpw") as mock_checkpw, \
         patch("services.user_services.create_access_token") as mock_access, \
         patch("services.user_services.create_refresh_token") as mock_refresh:

        mock_get_user.return_value = StoredUser()
        mock_checkpw.return_value = True

        mock_access.return_value = "access_token"
        mock_refresh.return_value = "refresh_token"

        result = user_login(User())

        assert result == (
            "access_token",
            "refresh_token"
        )

        mock_get_user.assert_called_once_with(User.email)
        mock_checkpw.assert_called_once()


def test_user_login_user_not_found():

    with patch("services.user_services.get_user") as mock_get_user:

        mock_get_user.return_value = None

        with pytest.raises(HTTPException) as exc:

            user_login(User())

        assert exc.value.status_code == 404
        assert exc.value.detail == "User Not Found"


def test_user_login_invalid_credentials():

    with patch("services.user_services.get_user") as mock_get_user, \
         patch("services.user_services.bcrypt.checkpw") as mock_checkpw:

        mock_get_user.return_value = StoredUser()
        mock_checkpw.return_value = False

        with pytest.raises(HTTPException) as exc:

            user_login(User())

        assert exc.value.status_code == 401
        assert exc.value.detail == "Invalid Credentials"


# USER INFO

def test_user_info_success():

    with patch("services.user_services.verify_token") as mock_verify, \
         patch("services.user_services.is_expired") as mock_expired, \
         patch("services.user_services.get_user") as mock_get_user:

        mock_verify.return_value = Payload
        mock_expired.return_value = None
        mock_get_user.return_value = Info()

        result = user_info("access_token")

        assert result.user_id == 1
        assert result.user_name == "furkhan"
        assert result.email == "test@gmail.com"

        mock_verify.assert_called_once_with("access_token")
        mock_expired.assert_called_once_with(121)
        mock_get_user.assert_called_once_with(
            username="furkhan"
        )


def test_user_info_unauthorized():

    with patch("services.user_services.verify_token") as mock_verify:

        mock_verify.return_value = None

        with pytest.raises(HTTPException) as exc:

            user_info("invalid_token")

        assert exc.value.status_code == 401
        assert exc.value.detail == "Unauthorized"


def test_user_info_revoked_token():

    with patch("services.user_services.verify_token") as mock_verify, \
         patch("services.user_services.is_expired") as mock_expired:

        mock_verify.return_value = Payload

        mock_expired.side_effect = HTTPException(
            401,
            detail="Revoked Token"
        )

        with pytest.raises(HTTPException) as exc:

            user_info("revoked_token")

        assert exc.value.status_code == 401
        assert exc.value.detail == "Revoked Token"


def test_user_info_user_not_found():

    with patch("services.user_services.verify_token") as mock_verify, \
         patch("services.user_services.is_expired") as mock_expired, \
         patch("services.user_services.get_user") as mock_get_user:

        mock_verify.return_value = Payload
        mock_expired.return_value = None
        mock_get_user.return_value = None

        with pytest.raises(HTTPException) as exc:

            user_info("access_token")

        assert exc.value.status_code == 404
        assert exc.value.detail == "User Not Found"


# REFRESH TOKEN

def test_refresh_success():

    with patch("services.user_services.verify_token") as mock_verify, \
         patch("services.user_services.is_revoked") as mock_revoked, \
         patch("services.user_services.new_token") as mock_new_token:

        mock_verify.return_value = refresh_payload
        mock_revoked.return_value = False
        mock_new_token.return_value = "new_access_token"

        result = refresh("refresh_token")

        assert result == "new_access_token"

        mock_verify.assert_called_once_with("refresh_token")
        mock_revoked.assert_called_once_with(1)
        mock_new_token.assert_called_once_with("refresh_token")


def test_refresh_unauthorized():

    with patch("services.user_services.verify_token") as mock_verify:

        mock_verify.return_value = None

        with pytest.raises(HTTPException) as exc:

            refresh("invalid_token")

        assert exc.value.status_code == 401
        assert exc.value.detail == "Unauthorized"


def test_refresh_revoked_token():

    with patch("services.user_services.verify_token") as mock_verify, \
         patch("services.user_services.is_revoked") as mock_revoked:

        mock_verify.return_value = refresh_payload

        mock_revoked.side_effect = HTTPException(
            401,
            detail="Token Revoked"
        )

        with pytest.raises(HTTPException) as exc:

            refresh("revoked_token")

        assert exc.value.status_code == 401
        assert exc.value.detail == "Token Revoked"


def test_refresh_internal_server_error():

    with patch("services.user_services.verify_token") as mock_verify, \
         patch("services.user_services.is_revoked") as mock_revoked, \
         patch("services.user_services.new_token") as mock_new_token:

        mock_verify.return_value = refresh_payload
        mock_revoked.return_value = False
        mock_new_token.return_value = None

        with pytest.raises(HTTPException) as exc:

            refresh("refresh_token")

        assert exc.value.status_code == 500
        assert exc.value.detail == "Internal Server Error"


# LOGOUT

@pytest.mark.asyncio
async def test_logout_unauthorized():

    with patch("services.user_services.verify_token") as mock_verify:

        mock_verify.return_value = None

        with pytest.raises(HTTPException) as exc:

            await logout(
                "access_token",
                "refresh_token"
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Unauthorized"


@pytest.mark.asyncio
async def test_logout_refresh_token_unauthorized():

    with patch("services.user_services.verify_token") as mock_verify:

        mock_verify.side_effect = [
            access_payload,
            None
        ]

        with pytest.raises(HTTPException) as exc:

            await logout(
                "access_token",
                "refresh_token"
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Unauthorized"


@pytest.mark.asyncio
async def test_logout_invalid_token_type():

    invalid_refresh_payload = {
        "user_id": 1,
        "user_name": "furkhan",
        "jti": 1,
        "exp": 1787220600,
        "type": "access"
    }

    with patch("services.user_services.verify_token") as mock_verify:

        mock_verify.side_effect = [
            access_payload,
            invalid_refresh_payload
        ]

        with pytest.raises(HTTPException) as exc:

            await logout(
                "access_token",
                "refresh_token"
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Invalid Token Type"


@pytest.mark.asyncio
async def test_logout_internal_server_error():

    with patch("services.user_services.verify_token") as mock_verify, \
         patch("services.user_services.time.time") as mock_time, \
         patch("services.user_services.r.set") as mock_set, \
         patch("services.user_services.revoketoken") as mock_revoke:

        mock_verify.side_effect = [
            access_payload,
            refresh_payload
        ]

        mock_time.return_value = 36666666
        mock_set.return_value = True
        mock_revoke.return_value = None

        with pytest.raises(HTTPException) as exc:

            await logout(
                "access_token",
                "refresh_token"
            )

        assert exc.value.status_code == 500
        assert exc.value.detail == "Internal Server Error"

        mock_set.assert_called_once()

        mock_revoke.assert_called_once_with(
            1,
            1787220600,
            True
        )


@pytest.mark.asyncio
async def test_logout_success():

    with patch("services.user_services.verify_token") as mock_verify, \
         patch("services.user_services.time.time") as mock_time, \
         patch("services.user_services.r.set") as mock_set, \
         patch("services.user_services.revoketoken") as mock_revoke, \
         patch("services.user_services.manager.active_connection") as mock_connections, \
         patch("services.user_services.manager.remove_connection") as mock_remove:

        mock_verify.side_effect = [
            access_payload,
            refresh_payload
        ]

        mock_time.return_value = 36666666
        mock_set.return_value = True
        mock_revoke.return_value = True

        mock_ws = AsyncMock()

        mock_connections.get.return_value = mock_ws

        result = await logout(
            "access_token",
            "refresh_token"
        )

        assert result == {
            "message": "logout successfully"
        }

        mock_set.assert_called_once()

        mock_revoke.assert_called_once_with(
            1,
            1787220600,
            True
        )

        mock_connections.get.assert_called_once_with(
            "furkhan"
        )

        mock_ws.close.assert_awaited_once()

        mock_remove.assert_called_once_with(
            "furkhan"
        )


@pytest.mark.asyncio
async def test_logout_success_user_offline():

    with patch("services.user_services.verify_token") as mock_verify, \
         patch("services.user_services.time.time") as mock_time, \
         patch("services.user_services.r.set") as mock_set, \
         patch("services.user_services.revoketoken") as mock_revoke, \
         patch("services.user_services.manager.active_connection") as mock_connections, \
         patch("services.user_services.manager.remove_connection") as mock_remove:

        mock_verify.side_effect = [
            access_payload,
            refresh_payload
        ]

        mock_time.return_value = 36666666
        mock_set.return_value = True
        mock_revoke.return_value = True

        mock_connections.get.return_value = None

        result = await logout(
            "access_token",
            "refresh_token"
        )

        assert result == {
            "message": "logout successfully"
        }

        mock_remove.assert_not_called()


# IS EXPIRED

def test_is_expired_token_not_revoked():

    with patch("services.user_services.r.get") as mock_get:

        mock_get.return_value = None

        result = is_expired(121)

        assert result is None

        mock_get.assert_called_once_with(
            "blacklist:121"
        )


def test_is_expired_token_revoked():

    with patch("services.user_services.r.get") as mock_get:

        mock_get.return_value = True

        with pytest.raises(HTTPException) as exc:

            is_expired(121)

        assert exc.value.status_code == 401
        assert exc.value.detail == "Revoked Token"


# UPLOAD FILE

def test_upload_file_success():

    with patch("services.user_services.get_user") as mock_get_user, \
         patch("services.user_services.uploader.upload") as mock_upload, \
         patch("services.user_services.add_pic") as mock_add_pic:

        mock_get_user.return_value = Info()

        mock_upload.return_value = {
            "secure_url": "https://cloudinary.com/profile.jpg"
        }

        mock_add_pic.return_value = True

        result = upload_file(
            "profile_image",
            Payload
        )

        assert result == {
            "message": "new profile pic added to furkhan profile"
        }

        mock_get_user.assert_called_once_with(
            username="furkhan"
        )

        mock_upload.assert_called_once_with(
            "profile_image",
            resource_type="auto"
        )

        mock_add_pic.assert_called_once_with(
            1,
            "https://cloudinary.com/profile.jpg"
        )


def test_upload_file_user_not_found():

    with patch("services.user_services.get_user") as mock_get_user:

        mock_get_user.return_value = None

        with pytest.raises(HTTPException) as exc:

            upload_file(
                "profile_image",
                Payload
            )

        assert exc.value.status_code == 404
        assert exc.value.detail == "User Not Found"


def test_upload_file_upload_failed():

    with patch("services.user_services.get_user") as mock_get_user, \
         patch("services.user_services.uploader.upload") as mock_upload:

        mock_get_user.return_value = Info()

        mock_upload.return_value = None

        with pytest.raises(HTTPException) as exc:

            upload_file(
                "profile_image",
                Payload
            )

        assert exc.value.status_code == 500
        assert exc.value.detail == "Failed to upload pfp"


def test_upload_file_database_error():

    with patch("services.user_services.get_user") as mock_get_user, \
         patch("services.user_services.uploader.upload") as mock_upload, \
         patch("services.user_services.add_pic") as mock_add_pic:

        mock_get_user.return_value = Info()

        mock_upload.return_value = {
            "secure_url": "https://cloudinary.com/profile.jpg"
        }

        mock_add_pic.return_value = None

        with pytest.raises(HTTPException) as exc:

            upload_file(
                "profile_image",
                Payload
            )

        assert exc.value.status_code == 500
        assert exc.value.detail == "Internal Server Error"

