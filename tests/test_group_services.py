import pytest

from unittest.mock import patch, MagicMock

from fastapi import HTTPException

from services.group_services import (
    get_groups,
    fetch_group_by_name,
    add_group,
    update_group_type,
    delete_group,
    join_public_group
)


Payload = {
    "user_id" : 1,
    "user_name" : "furkhan"
}


class GroupData:
    gname = "crazydevs"
    type = "public"
    new_type = "private"


class Group:
    group_id = 1
    group_name = "crazydevs"
    type = "public"


class Member:
    user_id = 1
    group_id = 1
    role = "admin"


# Get Groups Tests

def test_get_groups_success():

    with patch("services.group_services.get_joined_groups") as mock_groups:

        mock_groups.return_value = ["group1", "group2"]

        result = get_groups(Payload)

        assert result == ["group1", "group2"]


def test_get_groups_no_groups():

    with patch("services.group_services.get_joined_groups") as mock_groups:

        mock_groups.return_value = None

        with pytest.raises(HTTPException) as exc:
            get_groups(Payload)

        assert exc.value.status_code == 404
        assert exc.value.detail == "No Joined Groups Found"


# Fetch Group Tests

def test_fetch_group_by_name_success():

    with patch("services.group_services.get_group") as mock_get_group, \
         patch("services.group_services.get_member") as mock_get_member:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = Member()

        result = fetch_group_by_name(Payload, "crazydevs")

        assert result == "crazydevs"


def test_fetch_group_by_name_not_found():

    with patch("services.group_services.get_group") as mock_get_group:

        mock_get_group.return_value = None

        with pytest.raises(HTTPException) as exc:
            fetch_group_by_name(Payload, "crazydevs")

        assert exc.value.status_code == 404
        assert exc.value.detail == "Group Doesnt Exists"


def test_fetch_group_by_name_not_member():

    with patch("services.group_services.get_group") as mock_get_group, \
         patch("services.group_services.get_member") as mock_get_member:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = None

        with pytest.raises(HTTPException) as exc:
            fetch_group_by_name(Payload, "crazydevs")

        assert exc.value.status_code == 401
        assert exc.value.detail == "Not a member of crazydevs"


# Add Group Tests

def test_add_group_success():

    with patch("services.group_services.get_user") as mock_get_user, \
         patch("services.group_services.get_group") as mock_get_group, \
         patch("services.group_services.create_group") as mock_create_group, \
         patch("services.group_services.add_member") as mock_add_member, \
         patch("services.group_services.calculate_no_members") as mock_count, \
         patch("services.group_services.update_no_of_members") as mock_update, \
         patch("services.group_services.Session_Local") as mock_session:

        mock_user = MagicMock()
        mock_user.user_id = 1
        mock_user.user_name = "furkhan"

        mock_get_user.return_value = mock_user
        mock_get_group.return_value = None
        mock_create_group.return_value = Group()
        mock_add_member.return_value = True
        mock_count.return_value = 1
        mock_update.return_value = True

        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        result = add_group(GroupData(), Payload)

        assert "created crazydevs" in result["message"]

        mock_db.commit.assert_called_once()


def test_add_group_already_exists():

    with patch("services.group_services.get_user") as mock_get_user, \
         patch("services.group_services.get_group") as mock_get_group:

        mock_get_user.return_value = MagicMock()
        mock_get_group.return_value = Group()

        with pytest.raises(HTTPException) as exc:
            add_group(GroupData(), Payload)

        assert exc.value.status_code == 409
        assert exc.value.detail == "Group Already Exists"


# Update Group Type Tests

def test_update_group_type_success():

    with patch("services.group_services.get_group") as mock_get_group, \
         patch("services.group_services.get_member") as mock_get_member, \
         patch("services.group_services.change_type") as mock_change_type, \
         patch("services.group_services.Session_Local") as mock_session:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = Member()
        mock_change_type.return_value = True

        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        result = update_group_type(GroupData(), Payload)

        assert result == {"message": "Group Type Changed To private"}


def test_update_group_type_group_not_found():

    with patch("services.group_services.get_group") as mock_get_group:

        mock_get_group.return_value = None

        with pytest.raises(HTTPException) as exc:
            update_group_type(GroupData(), Payload)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Group Not Exists"


def test_update_group_type_forbidden():

    with patch("services.group_services.get_group") as mock_get_group, \
         patch("services.group_services.get_member") as mock_get_member:

        mock_get_group.return_value = Group()

        member = Member()
        member.role = "user"

        mock_get_member.return_value = member

        with pytest.raises(HTTPException) as exc:
            update_group_type(GroupData(), Payload)

        assert exc.value.status_code == 403
        assert exc.value.detail == "Forbidden"


def test_update_group_type_invalid_type():

    with patch("services.group_services.get_group") as mock_get_group, \
         patch("services.group_services.get_member") as mock_get_member:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = Member()

        data = GroupData()
        data.new_type = "invalid"

        with pytest.raises(HTTPException) as exc:
            update_group_type(data, Payload)

        assert exc.value.status_code == 400
        assert exc.value.detail == "Invalid Type"


def test_update_group_type_internal_server_error():

    with patch("services.group_services.get_group") as mock_get_group, \
         patch("services.group_services.get_member") as mock_get_member, \
         patch("services.group_services.change_type") as mock_change_type:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = Member()
        mock_change_type.return_value = None

        with pytest.raises(HTTPException) as exc:
            update_group_type(GroupData(), Payload)

        assert exc.value.status_code == 500
        assert exc.value.detail == "Internal Server Error"


# Delete Group Tests

def test_delete_group_success():

    with patch("services.group_services.get_group") as mock_get_group, \
         patch("services.group_services.remove_group") as mock_remove_group, \
         patch("services.group_services.delete_members") as mock_delete_members, \
         patch("services.group_services.Session_Local") as mock_session:

        mock_get_group.return_value = Group()
        mock_remove_group.return_value = Group()
        mock_delete_members.return_value = True

        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        result = delete_group("crazydevs", Payload)

        assert result == {"message": "group deleted successfully"}

        mock_db.commit.assert_called_once()


def test_delete_group_not_found():

    with patch("services.group_services.get_group") as mock_get_group:

        mock_get_group.return_value = None

        with pytest.raises(HTTPException) as exc:
            delete_group("crazydevs", Payload)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Group Not Exists"


# Join Public Group Tests

def test_join_public_group_success():

    with patch("services.group_services.get_group") as mock_get_group, \
         patch("services.group_services.get_member") as mock_get_member, \
         patch("services.group_services.add_member") as mock_add_member, \
         patch("services.group_services.Session_Local") as mock_session:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = None
        mock_add_member.return_value = True

        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        result = join_public_group(Payload, "crazydevs")

        assert "joined" in result["message"]

        mock_db.commit.assert_called_once()


def test_join_public_group_group_not_found():

    with patch("services.group_services.get_group") as mock_get_group:

        mock_get_group.return_value = None

        with pytest.raises(HTTPException) as exc:
            join_public_group(Payload, "crazydevs")

        assert exc.value.status_code == 404
        assert exc.value.detail == "Group Not Found"


def test_join_public_group_private():

    with patch("services.group_services.get_group") as mock_get_group:

        group = Group()
        group.type = "private"

        mock_get_group.return_value = group

        with pytest.raises(HTTPException) as exc:
            join_public_group(Payload, "crazydevs")

        assert exc.value.status_code == 400
        assert exc.value.detail == "Only admin can add members"


def test_join_public_group_already_member():

    with patch("services.group_services.get_group") as mock_get_group, \
         patch("services.group_services.get_member") as mock_get_member:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = Member()

        with pytest.raises(HTTPException) as exc:
            join_public_group(Payload, "crazydevs")

        assert exc.value.status_code == 409
        assert exc.value.detail == "already a member"


def test_join_public_group_internal_server_error():

    with patch("services.group_services.get_group") as mock_get_group, \
         patch("services.group_services.get_member") as mock_get_member, \
         patch("services.group_services.add_member") as mock_add_member:

        mock_get_group.return_value = Group()
        mock_get_member.return_value = None
        mock_add_member.return_value = None

        with pytest.raises(HTTPException) as exc:
            join_public_group(Payload, "crazydevs")

        assert exc.value.status_code == 500
        assert exc.value.detail == "Internal Server Error"