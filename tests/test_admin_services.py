import pytest

from unittest.mock import patch, MagicMock

from fastapi import HTTPException

from services.admin_services import (
    getgroupmembers,
    getgroupinfo,
    addmember,
    updaterole,
    deletemember,
    clearchat,
    group_pfp
)


class Admin:
    user_id = 1
    user_name = "furkhan"


class Group:
    group_id = 1
    group_name = "crazydevs"


class Member:
    user_id = 1
    group_id = 1
    role = "admin"


class Data:
    username = "john"
    role = "user"
    new_role = "admin"


# Get Group Members Tests

def test_getgroupmembers_success():

    with patch("services.admin_services.get_group") as mock_group, \
         patch("services.admin_services.get_members") as mock_members, \
         patch("services.admin_services.Session_Local") as mock_session:

        mock_group.return_value = Group()

        member1 = ("john", "admin")
        member2 = ("wick", "user")

        mock_members.return_value = [member1, member2]

        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        result = getgroupmembers("crazydevs", Admin())

        assert result == {
            "message": {
                "members": [
                    ["john", "admin"],
                    ["wick", "user"]
                ]
            }
        }


def test_getgroupmembers_group_not_found():

    with patch("services.admin_services.get_group") as mock_group:

        mock_group.return_value = None

        with pytest.raises(HTTPException) as exc:
            getgroupmembers("crazydevs", Admin())

        assert exc.value.status_code == 404
        assert exc.value.detail == "Group Not Found"


def test_getgroupmembers_no_members():

    with patch("services.admin_services.get_group") as mock_group, \
         patch("services.admin_services.get_members") as mock_members:

        mock_group.return_value = Group()
        mock_members.return_value = None

        result = getgroupmembers("crazydevs", Admin())

        assert result == {"message": "No memebrs"}


# Get Group Info Tests

def test_getgroupinfo_success():

    with patch("services.admin_services.get_group_info") as mock_group_info, \
         patch("services.admin_services.get_member") as mock_member, \
         patch("services.admin_services.Session_Local") as mock_session:
        group = Group()
        mock_group_info.return_value = group
        mock_member.return_value = Member()

        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        result = getgroupinfo("crazydevs", Admin())

        assert result == {"info": group}


def test_getgroupinfo_group_not_found():

    with patch("services.admin_services.get_group_info") as mock_group_info:

        mock_group_info.return_value = None

        with pytest.raises(HTTPException) as exc:
            getgroupinfo("crazydevs", Admin())

        assert exc.value.status_code == 404
        assert exc.value.detail == "Group Not Found"


def test_getgroupinfo_not_admin():

    with patch("services.admin_services.get_group_info") as mock_group_info, \
         patch("services.admin_services.get_member") as mock_member:

        mock_group_info.return_value = Group()

        member = Member()
        member.role = "user"

        mock_member.return_value = member

        with pytest.raises(HTTPException) as exc:
            getgroupinfo("crazydevs", Admin())

        assert exc.value.status_code == 403
        assert exc.value.detail == "Unauthorized Admin Only"


# Add Member Tests

def test_addmember_already_member():

    with patch("services.admin_services.get_group") as mock_group, \
         patch("services.admin_services.get_user") as mock_user, \
         patch("services.admin_services.get_member") as mock_member:

        mock_group.return_value = Group()

        user = MagicMock()
        user.user_id = 2

        mock_user.return_value = user
        mock_member.return_value = Member()

        with pytest.raises(HTTPException) as exc:
            addmember("crazydevs", Data(), Admin())

        assert exc.value.status_code == 409
        assert exc.value.detail == "Already a member"


def test_addmember_success():

    with patch("services.admin_services.get_group") as mock_group, \
         patch("services.admin_services.get_user") as mock_user, \
         patch("services.admin_services.get_member") as mock_member, \
         patch("services.admin_services.add_member") as mock_add_member, \
         patch("services.admin_services.Session_Local") as mock_session:

        mock_group.return_value = Group()

        user = MagicMock()
        user.user_id = 2

        mock_user.return_value = user
        mock_member.return_value = None
        mock_add_member.return_value = True

        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        result = addmember("crazydevs", Data(), Admin())

        assert "john added to crazydevs successfully" in result["message"]

        mock_db.commit.assert_called_once()


def test_addmember_internal_server_error():

    with patch("services.admin_services.get_group") as mock_group, \
         patch("services.admin_services.get_user") as mock_user, \
         patch("services.admin_services.get_member") as mock_member, \
         patch("services.admin_services.add_member") as mock_add_member:

        mock_group.return_value = Group()

        user = MagicMock()
        user.user_id = 2

        mock_user.return_value = user
        mock_member.return_value = None
        mock_add_member.return_value = None

        with pytest.raises(HTTPException) as exc:
            addmember("crazydevs", Data(), Admin())

        assert exc.value.status_code == 500
        assert exc.value.detail == "Internal Server Error"


# Update Role Tests

def test_updaterole_group_not_found():

    with patch("services.admin_services.get_group") as mock_group:

        mock_group.return_value = None

        with pytest.raises(HTTPException) as exc:
            updaterole("crazydevs", Data(), Admin())

        assert exc.value.status_code == 404
        assert exc.value.detail == "Group Not Found"


def test_updaterole_member_not_found():

    with patch("services.admin_services.get_group") as mock_group, \
         patch("services.admin_services.get_user") as mock_user, \
         patch("services.admin_services.get_member") as mock_member:

        mock_group.return_value = Group()

        user = MagicMock()
        user.user_id = 2

        mock_user.return_value = user
        mock_member.return_value = None

        with pytest.raises(HTTPException) as exc:
            updaterole("crazydevs", Data(), Admin())

        assert exc.value.status_code == 404
        assert exc.value.detail == "Not group member"


def test_updaterole_success():

    with patch("services.admin_services.get_group") as mock_group, \
         patch("services.admin_services.get_user") as mock_user, \
         patch("services.admin_services.get_member") as mock_member, \
         patch("services.admin_services.update_user_role") as mock_update, \
         patch("services.admin_services.Session_Local") as mock_session:

        mock_group.return_value = Group()

        user = MagicMock()
        user.user_id = 2

        mock_user.return_value = user
        mock_member.return_value = Member()
        mock_update.return_value = True

        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        result = updaterole("crazydevs", Data(), Admin())

        assert result == {
            "messsage": "john udpated to admin"
        }

        mock_db.commit.assert_called_once()


# Delete Member Tests

def test_deletemember_group_not_found():

    with patch("services.admin_services.get_group") as mock_group:

        mock_group.return_value = None

        with pytest.raises(HTTPException) as exc:
            deletemember("crazydevs", "john", Admin())

        assert exc.value.status_code == 404
        assert exc.value.detail == "Group Not Found"


def test_deletemember_not_member():

    with patch("services.admin_services.get_group") as mock_group, \
         patch("services.admin_services.get_user") as mock_user, \
         patch("services.admin_services.get_member") as mock_member:

        mock_group.return_value = Group()

        user = MagicMock()
        user.user_id = 2

        mock_user.return_value = user
        mock_member.return_value = None

        with pytest.raises(HTTPException) as exc:
            deletemember("crazydevs", "john", Admin())

        assert exc.value.status_code == 404
        assert exc.value.detail == "Not group member"


def test_deletemember_success():

    with patch("services.admin_services.get_group") as mock_group, \
         patch("services.admin_services.get_user") as mock_user, \
         patch("services.admin_services.get_member") as mock_member, \
         patch("services.admin_services.remove_group_member") as mock_remove, \
         patch("services.admin_services.Session_Local") as mock_session:

        mock_group.return_value = Group()

        user = MagicMock()
        user.user_id = 2

        mock_user.return_value = user
        mock_member.return_value = Member()
        mock_remove.return_value = True

        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        result = deletemember("crazydevs", "john", Admin())

        assert result == {
            "message": "john deleted successfully"
        }


# Clear Chat Tests

def test_clearchat_success():

    with patch("services.admin_services.get_group") as mock_group, \
         patch("services.admin_services.delete_group_msgs") as mock_delete, \
         patch("services.admin_services.Session_Local") as mock_session:

        mock_group.return_value = Group()
        mock_delete.return_value = True

        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        result = clearchat("crazydevs", Admin())

        assert result == {"message": "Chat Cleared"}

        mock_db.commit.assert_called_once()


def test_clearchat_group_not_found():

    with patch("services.admin_services.get_group") as mock_group:

        mock_group.return_value = None

        with pytest.raises(HTTPException) as exc:
            clearchat("crazydevs", Admin())

        assert exc.value.status_code == 404
        assert exc.value.detail == "Group Not Found"


def test_clearchat_internal_server_error():

    with patch("services.admin_services.get_group") as mock_group, \
         patch("services.admin_services.delete_group_msgs") as mock_delete:

        mock_group.return_value = Group()
        mock_delete.return_value = None

        with pytest.raises(HTTPException) as exc:
            clearchat("crazydevs", Admin())

        assert exc.value.status_code == 500
        assert exc.value.detail == "Internal Server Error"