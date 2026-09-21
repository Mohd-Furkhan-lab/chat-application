import pytest

from unittest.mock import patch, MagicMock

from fastapi import HTTPException

from services.group_msg_services import (
    getmsgs,
    clearchat,
    sendmsg,
    sendmedia
)


Payload = {
    "user_id" : 1,
    "user_name" : "furkhan"
}


class Group:
    group_id = 1
    group_name = "crazydevs"
    type = "public"


class Member:
    user_id = 1
    group_id = 1


class Msg:
    msg = "hello"


# Get Messages Tests

def test_getmsgs_success():

    with patch("services.group_msg_services.get_group") as mock_get_group, \
         patch("services.group_msg_services.get_member") as mock_get_member, \
         patch("services.group_msg_services.get_group_msgs") as mock_get_msgs:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = Member()
        mock_get_msgs.return_value = ["msg1", "msg2"]

        mock_db = MagicMock()

        with patch("services.group_msg_services.Session_Local") as mock_session:

            mock_session.return_value.__enter__.return_value = mock_db

            result = getmsgs(Payload, "crazydevs")

            assert result == ["msg1", "msg2"]


def test_getmsgs_group_not_found():

    with patch("services.group_msg_services.get_group") as mock_get_group, \
         patch("services.group_msg_services.Session_Local") as mock_session:

        mock_get_group.return_value = None

        with pytest.raises(HTTPException) as exc:
            getmsgs(Payload, "crazydevs")

        assert exc.value.status_code == 404
        assert exc.value.detail == "Group Not Found"


def test_getmsgs_not_member():

    with patch("services.group_msg_services.get_group") as mock_get_group, \
         patch("services.group_msg_services.get_member") as mock_get_member:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = None

        with pytest.raises(HTTPException) as exc:
            getmsgs(Payload, "crazydevs")

        assert exc.value.status_code == 401
        assert exc.value.detail == "Not crazydevs's member"


# Clear Chat Tests

def test_clearchat_success():

    with patch("services.group_msg_services.get_group") as mock_get_group, \
         patch("services.group_msg_services.get_member") as mock_get_member, \
         patch("services.group_msg_services.delete_group_msgs") as mock_delete, \
         patch("services.group_msg_services.Session_Local") as mock_session:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = Member()
        mock_delete.return_value = True

        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        result = clearchat("crazydevs", Payload)

        assert result == {"message": "Chat Cleared"}

        mock_db.commit.assert_called_once()


def test_clearchat_group_not_found():

    with patch("services.group_msg_services.get_group") as mock_get_group:

        mock_get_group.return_value = None

        with pytest.raises(HTTPException) as exc:
            clearchat("crazydevs", Payload)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Group Not Found"


def test_clearchat_private_group():

    with patch("services.group_msg_services.get_group") as mock_get_group:

        group = Group()
        group.type = "private"

        mock_get_group.return_value = group

        with pytest.raises(HTTPException) as exc:
            clearchat("crazydevs", Payload)

        assert exc.value.status_code == 403
        assert exc.value.detail == "Unauthorized Admin Only"


def test_clearchat_not_member():

    with patch("services.group_msg_services.get_group") as mock_get_group, \
         patch("services.group_msg_services.get_member") as mock_get_member:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = None

        with pytest.raises(HTTPException) as exc:
            clearchat("crazydevs", Payload)

        assert exc.value.status_code == 401
        assert exc.value.detail == "Not crazydevs's member"


def test_clearchat_internal_server_error():

    with patch("services.group_msg_services.get_group") as mock_get_group, \
         patch("services.group_msg_services.get_member") as mock_get_member, \
         patch("services.group_msg_services.delete_group_msgs") as mock_delete:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = Member()
        mock_delete.return_value = None

        with pytest.raises(HTTPException) as exc:
            clearchat("crazydevs", Payload)

        assert exc.value.status_code == 500
        assert exc.value.detail == "Internal Server Error"


# Send Message Tests

@pytest.mark.asyncio
async def test_sendmsg_success():

    with patch("services.group_msg_services.get_group") as mock_get_group, \
         patch("services.group_msg_services.get_member") as mock_get_member, \
         patch("services.group_msg_services.add_group_msg") as mock_add_msg, \
         patch("services.group_msg_services.group_manager.braodcast_msg") as mock_broadcast, \
         patch("services.group_msg_services.Session_Local") as mock_session:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = Member()
        mock_add_msg.return_value = True
        mock_broadcast.return_value = True

        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        result = await sendmsg(
            Payload,
            "crazydevs",
            Msg()
        )

        assert result == {"message": "message sent successfully"}

        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_sendmsg_group_not_found():

    with patch("services.group_msg_services.get_group") as mock_get_group:

        mock_get_group.return_value = None

        with pytest.raises(HTTPException) as exc:
            await sendmsg(Payload, "crazydevs", Msg())

        assert exc.value.status_code == 404
        assert exc.value.detail == "Group Not Found"


@pytest.mark.asyncio
async def test_sendmsg_not_member():

    with patch("services.group_msg_services.get_group") as mock_get_group, \
         patch("services.group_msg_services.get_member") as mock_get_member:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = None

        with pytest.raises(HTTPException) as exc:
            await sendmsg(Payload, "crazydevs", Msg())

        assert exc.value.status_code == 401
        assert exc.value.detail == "Not crazydevs's member"


# Send Media Tests

@pytest.mark.asyncio
async def test_sendmedia_success():

    with patch("services.group_msg_services.get_group") as mock_get_group, \
         patch("services.group_msg_services.get_member") as mock_get_member, \
         patch("services.group_msg_services.uploader.upload") as mock_upload, \
         patch("services.group_msg_services.add_group_media") as mock_add_media, \
         patch("services.group_msg_services.group_manager.braodcast_msg") as mock_broadcast, \
         patch("services.group_msg_services.Session_Local") as mock_session:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = Member()

        mock_file = MagicMock()
        mock_file.content_type = "image/jpeg"
        mock_file.file = "image_file"

        mock_upload.return_value = {
            "secure_url": "https://cloudinary.com/image.jpg"
        }

        mock_add_media.return_value = True
        mock_broadcast.return_value = True

        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        result = await sendmedia(
            "crazydevs",
            mock_file,
            Payload
        )

        assert result == {"message": "message sent successfully"}

        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_sendmedia_group_not_found():

    with patch("services.group_msg_services.get_group") as mock_get_group:

        mock_get_group.return_value = None

        mock_file = MagicMock()
        mock_file.content_type = "image/jpeg"

        with pytest.raises(HTTPException) as exc:
            await sendmedia(
                "crazydevs",
                mock_file,
                Payload
            )

        assert exc.value.status_code == 404
        assert exc.value.detail == "Group Not Found"


@pytest.mark.asyncio
async def test_sendmedia_not_member():

    with patch("services.group_msg_services.get_group") as mock_get_group, \
         patch("services.group_msg_services.get_member") as mock_get_member:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = None

        mock_file = MagicMock()
        mock_file.content_type = "image/jpeg"

        with pytest.raises(HTTPException) as exc:
            await sendmedia(
                "crazydevs",
                mock_file,
                Payload
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Not crazydevs's member"


@pytest.mark.asyncio
async def test_sendmedia_unsupported_media():

    with patch("services.group_msg_services.get_group") as mock_get_group, \
         patch("services.group_msg_services.get_member") as mock_get_member:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = Member()

        mock_file = MagicMock()
        mock_file.content_type = "text/plain"

        with pytest.raises(HTTPException) as exc:
            await sendmedia(
                "crazydevs",
                mock_file,
                Payload
            )

        assert exc.value.status_code == 400
        assert exc.value.detail == "Unsupported media type"


@pytest.mark.asyncio
async def test_sendmedia_upload_failed():

    with patch("services.group_msg_services.get_group") as mock_get_group, \
         patch("services.group_msg_services.get_member") as mock_get_member, \
         patch("services.group_msg_services.uploader.upload") as mock_upload:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = Member()
        mock_upload.return_value = None

        mock_file = MagicMock()
        mock_file.content_type = "image/jpeg"
        mock_file.file = "image_file"

        with pytest.raises(HTTPException) as exc:
            await sendmedia(
                "crazydevs",
                mock_file,
                Payload
            )

        assert exc.value.status_code == 500
        assert exc.value.detail == "Oops cant send the media"