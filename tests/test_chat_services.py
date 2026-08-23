import pytest
from unittest.mock import patch, MagicMock

from fastapi import HTTPException

from services.chats_services import getallchats, get_chat, delete_convo


access_payload = {
    "jti": 121,
    "user_name": "gfdgsdfgsf"
}


class Convo:

    convo_id = 1


def test_getallchats_success():

    with patch("services.chats_services.verify_token") as mock_payload, \
         patch("services.chats_services.is_expired") as mock_expired, \
         patch("services.chats_services.get_chats") as mock_chats:

        mock_payload.return_value = access_payload
        mock_expired.return_value = None
        mock_chats.return_value = ["chat1", "chat2"]

        result = getallchats("fasdgaopjnpokjnibnp")

        assert result == {"chats": ["chat1", "chat2"]}


def test_getallchats_token_missing():

    with patch("services.chats_services.verify_token") as mock_payload:

        mock_payload.return_value = None

        with pytest.raises(HTTPException) as exc:

            getallchats("fasdgaopjnpokjnibnp")

        assert exc.value.status_code == 401
        assert exc.value.detail == "Token Missing"


def test_getallchats_no_chats():

    with patch("services.chats_services.verify_token") as mock_payload, \
         patch("services.chats_services.is_expired") as mock_expired, \
         patch("services.chats_services.get_chats") as mock_chats:

        mock_payload.return_value = access_payload
        mock_expired.return_value = None
        mock_chats.return_value = None

        with pytest.raises(HTTPException) as exc:

            getallchats("fasdgaopjnpokjnibnp")

        assert exc.value.status_code == 404
        assert exc.value.detail == "No Chats Found"


def test_get_chat_success():

    with patch("services.chats_services.verify_token") as mock_payload, \
         patch("services.chats_services.is_expired") as mock_expired, \
         patch("services.chats_services.get_convo") as mock_convo, \
         patch("services.chats_services.get_msg") as mock_messages:

        mock_payload.return_value = access_payload
        mock_expired.return_value = None
        mock_convo.return_value = Convo()
        mock_messages.return_value = ["message1", "message2"]

        result = get_chat(
            "fasdgaopjnpokjnibnp",
            "receiver"
        )

        assert result == ["message1", "message2"]


def test_get_chat_no_chat():

    with patch("services.chats_services.verify_token") as mock_payload, \
         patch("services.chats_services.is_expired") as mock_expired, \
         patch("services.chats_services.get_convo") as mock_convo, \
         patch("services.chats_services.get_msg") as mock_messages:

        mock_payload.return_value = access_payload
        mock_expired.return_value = None
        mock_convo.return_value = Convo()
        mock_messages.return_value = None

        result = get_chat(
            "fasdgaopjnpokjnibnp",
            "receiver"
        )

        assert result == {"message": "no chat found"}


def test_get_chat_contact_not_found():

    with patch("services.chats_services.verify_token") as mock_payload, \
         patch("services.chats_services.is_expired") as mock_expired, \
         patch("services.chats_services.get_convo") as mock_convo:

        mock_payload.return_value = access_payload
        mock_expired.return_value = None
        mock_convo.return_value = None

        result = get_chat(
            "fasdgaopjnpokjnibnp",
            "receiver"
        )

        assert result == {"message": "no contact named receiver"}


def test_get_chat_token_missing():

    with patch("services.chats_services.verify_token") as mock_payload:

        mock_payload.return_value = None

        with pytest.raises(HTTPException) as exc:

            get_chat(
                "fasdgaopjnpokjnibnp",
                "receiver"
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Token Missing"


def test_delete_convo_success():

    with patch("services.chats_services.verify_token") as mock_payload, \
         patch("services.chats_services.is_expired") as mock_expired, \
         patch("services.chats_services.get_convo") as mock_convo, \
         patch("services.chats_services.clear_convo") as mock_clear_convo, \
         patch("services.chats_services.Session_Local") as mock_session:

        mock_payload.return_value = access_payload
        mock_expired.return_value = None
        mock_convo.return_value = Convo()

        mock_db = MagicMock()

        mock_session.return_value.__enter__.return_value = mock_db

        result = delete_convo(
            "fasdgaopjnpokjnibnp",
            "receiver"
        )

        assert result == {"message": "chat cleared successfully"}

        mock_clear_convo.assert_called_once_with(
            1,
            mock_db
        )

        mock_db.commit.assert_called_once()


def test_delete_convo_token_missing():

    with patch("services.chats_services.verify_token") as mock_payload:

        mock_payload.return_value = None

        with pytest.raises(HTTPException) as exc:

            delete_convo(
                "fasdgaopjnpokjnibnp",
                "receiver"
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Token Missing"


def test_delete_convo_contact_not_found():

    with patch("services.chats_services.verify_token") as mock_payload, \
         patch("services.chats_services.is_expired") as mock_expired, \
         patch("services.chats_services.get_convo") as mock_convo:

        mock_payload.return_value = access_payload
        mock_expired.return_value = None
        mock_convo.return_value = None

        with pytest.raises(HTTPException) as exc:

            delete_convo(
                "fasdgaopjnpokjnibnp",
                "receiver"
            )

        assert exc.value.status_code == 404
        assert exc.value.detail == "Contact not found"


def test_delete_convo_database_error():

    with patch("services.chats_services.verify_token") as mock_payload, \
         patch("services.chats_services.is_expired") as mock_expired, \
         patch("services.chats_services.get_convo") as mock_convo, \
         patch("services.chats_services.clear_convo") as mock_clear_convo, \
         patch("services.chats_services.Session_Local") as mock_session:

        mock_payload.return_value = access_payload
        mock_expired.return_value = None
        mock_convo.return_value = Convo()

        mock_db = MagicMock()

        mock_session.return_value.__enter__.return_value = mock_db

        mock_clear_convo.side_effect = Exception("Database error")

        result = delete_convo(
            "fasdgaopjnpokjnibnp",
            "receiver"
        )

        assert result == {
            "message": "an error occured as Database error"
        }

        mock_db.rollback.assert_called_once()