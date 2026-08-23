from fastapi import HTTPException
import pytest
from unittest.mock import patch,AsyncMock
from services.user_services import new_user,user_login,user_info,sendmsg,refresh,logout,is_expired

class User():
     email = "mohdfurkhan7755@gmail.com"
     password = "Mf#@9346954045"

class StoredUser():
      user_name = "fadfafafd"
      password = "fasga"

Payload = {
      "jti" : 121,
      "user_name" : "gfdgsdfgsf" 
}

access_payload = {
      "jti" : 121,
      "exp" : 1787220600 
}

refresh_payload = {
      "jti" : 1,
      "exp" : 1787220600,
      "type" : "refresh",
      "user_name" : "furkhan"
}


class Info():
      user_id = 1
      user_name = "gfdgsdfgsf"
      email = "fadsfbkgbgmk@mgmf.com"
      password = "fasdfkbaksjfb"

info = Info()

class Msg():
      to = "furkhan"
      msg = "fsagfgsd"

class Convo():
      convo_id = 1
      sender = "John"
      reciever = "Wick"

class Connection():
      active_connection = {"furkhan" : "9083qn3f9ngpg3u5piun54pi"}

#User Signup Tests

def test_new_user():
    with patch("services.user_services.random_username") as mock_random_name,\
         patch("services.user_services.bcrypt.hashpw") as mock_hash_pw,\
         patch("services.user_services.add_user") as mock_add_user ,\
         patch("services.user_services.get_user") as mock_get_user :
            mock_random_name.return_value = "889hbibvbib3bbb"
            mock_hash_pw.return_value = b"fasdfqw98bioubgqhtp9hpubu"
            mock_add_user.return_value = True
            mock_get_user.return_value = False
            assert new_user(User()) == { "message" : "signed up successfully",  "user_name": "889hbibvbib3bbb"}

def test_new_user_already_exists():
     with patch("services.user_services.get_user") as mock_get_user:
          mock_get_user.return_value = True
          with pytest.raises(HTTPException) as exc:
               new_user(User())
          assert exc.value.status_code == 409
          assert exc.value.detail == "User Already Exists"

def test_new_user_internal_server_error():
    with patch("services.user_services.random_username") as mock_random_name,\
         patch("services.user_services.bcrypt.hashpw") as mock_hash_pw,\
         patch("services.user_services.add_user") as mock_add_user ,\
         patch("services.user_services.get_user") as mock_get_user :
            mock_random_name.return_value = "889hbibvbib3bbb"
            mock_hash_pw.return_value = b"fasdfqw98bioubgqhtp9hpubu"
            mock_get_user.return_value = False
            mock_add_user.return_value = False
            with pytest.raises(HTTPException) as exc:
                 new_user(User())
            assert exc.value.status_code == 500
            assert exc.value.detail == "Internal Server Error"

#User Login Tests

def test_user_login():
    with patch("services.user_services.get_user") as mock_get_user ,\
         patch("services.user_services.bcrypt.checkpw") as mock_check_pw ,\
         patch("services.user_services.create_access_token") as mock_a_token, \
         patch("services.user_services.create_refresh_token") as mock_r_token :
            mock_get_user.return_value = StoredUser()
            mock_check_pw.return_value = True
            mock_a_token.return_value = "fq3o8gb3ibgvohbpiubkjbqgbv;aebvjhbjbbygfkikj"
            mock_r_token.return_value = "fq3o8gb3ibgvohbpiubkjbqgbv;aebvjhbjbbygfkikgsdfg"
            result = user_login(User())
            assert result == ("fq3o8gb3ibgvohbpiubkjbqgbv;aebvjhbjbbygfkikj", "fq3o8gb3ibgvohbpiubkjbqgbv;aebvjhbjbbygfkikgsdfg"
)


def test_user_login_user_not_found():
      with patch("services.user_services.get_user") as mock_get_user:
            mock_get_user.return_value =  None
            with pytest.raises(HTTPException) as exc:
                  user_login(User())
            assert exc.value.status_code == 404
            assert exc.value.detail == "User Not Found"

def test_user_login_invalid_credentails():
      with patch("services.user_services.get_user") as mock_get_user ,\
           patch("services.user_services.bcrypt.checkpw") as mock_check_pw :
                mock_get_user.return_value = StoredUser()
                mock_check_pw.return_value = False
                with pytest.raises(HTTPException) as exc:
                      user_login(User())
                assert exc.value.status_code == 401
                assert exc.value.detail == "Invalid Credentials"

#User Details Tests

def test_user_info():
    with patch("services.user_services.verify_token") as mock_payload , \
         patch("services.user_services.is_expired") as mock_is_expired, \
         patch("services.user_services.get_user") as mock_get_user :
            mock_payload.return_value = Payload
            mock_is_expired.return_value = None
            mock_get_user.return_value = info
            result = user_info("dfasdfggdsgsdhsdhdhdh")
            assert result == info

def test_user_info_empty_payload():
      with patch("services.user_services.verify_token") as mock_get_payload :
            mock_get_payload.return_value = None
            with pytest.raises(HTTPException) as exc:
                  user_info("dfasdfggdsgsdhsdhdhdh")
            assert exc.value.status_code == 401
            assert exc.value.detail == "Unauthorized"

def test_user_info_revoked_token():
     with patch("services.user_services.verify_token") as mock_payload , \
          patch("services.user_services.is_expired") as mock_is_expired:
               mock_payload.return_value = Payload
               mock_is_expired.side_effect = HTTPException(401,detail="Revoked Token")
               with pytest.raises(HTTPException) as exc:
                  user_info("dfasdfggdsgsdhsdhdhdh")
                     
               assert exc.value.status_code == 401
               assert exc.value.detail == "Revoked Token"

def test_user_info_not_found():
     with patch("services.user_services.verify_token") as mock_payload , \
          patch("services.user_services.is_expired") as mock_is_expired, \
          patch("services.user_services.get_user") as mock_get_user :
               mock_payload.return_value = Payload
               mock_is_expired.return_value = None
               mock_get_user.return_value = None
               with pytest.raises(HTTPException) as exc:
                    user_info("asfasfassaff")
               assert exc.value.status_code == 404
               assert exc.value.detail == "User Not Found"



#Send Msg Tests

@pytest.mark.asyncio
async def test_sendmsg_unauthorized():
     with patch("services.user_services.verify_token") as mock_validation:
          mock_validation.return_value = None
          with pytest.raises(HTTPException) as exc:
               await sendmsg(Msg(),"asfdggbijhbgoljkbkljb")
          assert exc.value.status_code == 401
          assert exc.value.detail == "Unauthorized"

@pytest.mark.asyncio
async def test_sendmsg_revoked_token():
     with patch("services.user_services.verify_token") as mock_validation ,\
          patch("services.user_services.is_expired") as mock_expired :
               mock_validation.return_value = Payload
               mock_expired.side_effect = HTTPException(401,detail="Revoked Token")
               with pytest.raises(HTTPException) as exc:
                    await sendmsg(Msg(),"asfdggbijhbgoljkbkljb")
               assert exc.value.status_code == 401
               assert exc.value.detail == "Revoked Token"

@pytest.mark.asyncio
async def test_sendmsg_convo_notfound():
     with patch("services.user_services.verify_token") as mock_validation , \
          patch("services.user_services.is_expired") as mock_expired ,\
          patch("services.user_services.get_convo") as mock_convo ,\
          patch("services.user_services.add_new_convo") as mock_add_convo ,\
          patch("services.user_services.add_msg") as mock_msg,\
          patch("services.user_services.manager.active_connection") as mock_manager_connections , \
          patch("services.user_services.manager.braodcast_msg") as mock_send_msg:
               mock_validation.return_value = Payload
               mock_expired.return_value = None
               mock_convo.return_value = None
               mock_add_convo.return_value = Convo()
               mock_convo.return_value = Convo()
               mock_msg.return_value = Msg()
               mock_manager_connections.return_value = Connection()
               mock_send_msg.return_value = True
               result = await sendmsg(Msg(),"fasdgaopjnpokjnibnp")
               assert result == {"message" : "sent successfully"}


@pytest.mark.asyncio
async def test_sendmsg_reciever_online():
     with patch("services.user_services.verify_token") as mock_validation , \
          patch("services.user_services.is_expired") as mock_expired ,\
          patch("services.user_services.get_convo") as mock_convo ,\
          patch("services.user_services.add_msg") as mock_msg,\
          patch("services.user_services.manager.active_connection") as mock_manager_connections , \
          patch("services.user_services.manager.braodcast_msg") as mock_send_msg:
               mock_validation.return_value = Payload
               mock_expired.return_value = None
               mock_convo.return_value = Convo()
               mock_msg.return_value = Msg()
               mock_manager_connections.return_value = Connection()
               mock_send_msg.return_value = True
               result = await sendmsg(Msg(),"fasdgaopjnpokjnibnp")
               assert result == {"message" : "sent successfully"}

@pytest.mark.asyncio
async def test_sendmsg_reciever_offline():
     with patch("services.user_services.verify_token") as mock_validation , \
          patch("services.user_services.is_expired") as mock_expired ,\
          patch("services.user_services.get_convo") as mock_convo ,\
          patch("services.user_services.add_msg") as mock_msg,\
          patch("services.user_services.manager.active_connection") as mock_manager_connections :
               mock_validation.return_value = Payload
               mock_expired.return_value = None
               mock_convo.return_value = Convo()
               mock_msg.return_value = Msg()
               mock_manager_connections.get.return_value = None
               result = await sendmsg(Msg(),"fasdgaopjnpokjnibnp")
               assert result == {"message" : "user offline"}

#Refresh Token Tests

def test_refresh():
     with patch("services.user_services.verify_token") as mock_payload, \
          patch("services.user_services.is_revoked") as mock_vaidation, \
          patch("services.user_services.new_token") as mock_token:
               mock_payload.return_value = Payload
               mock_vaidation.return_value = None
               mock_token.return_value =  "asdfadfasdfadfafafaf5367548"
               result = refresh("fadsfasdfgsfdghfdh")
               assert result == "asdfadfasdfadfafafaf5367548"

def test_refresh_empty_payload():
     with patch("services.user_services.verify_token") as mock_payload:
               mock_payload.return_value = None
               with pytest.raises(HTTPException) as exc:
                     refresh("afdasdfa")
               assert exc.value.status_code == 401
               assert exc.value.detail == "Unauthorized"

def test_refresh_revoked_token():
     with patch("services.user_services.verify_token") as mock_payload, \
          patch("services.user_services.is_revoked") as mock_vaidation :
               mock_payload.return_value = Payload
               mock_vaidation.side_effect  = HTTPException(401,detail="Revoked Token")
               with pytest.raises(HTTPException) as exc:
                     refresh("fadsfafafadf")
               assert exc.value.status_code == 401
               assert exc.value.detail == "Revoked Token"

def test_refresh_internal_server_error():
     with patch("services.user_services.verify_token") as mock_payload, \
          patch("services.user_services.is_revoked") as mock_vaidation, \
          patch("services.user_services.new_token") as mock_token:
               mock_payload.return_value = Payload
               mock_vaidation.return_value = None
               mock_token.return_value =  None
               with pytest.raises(HTTPException) as exc:
                    refresh("Fafafagwhgwerhgerth165165m")
               assert exc.value.status_code == 500
               assert exc.value.detail == "Internal Server Error" 

#User Logout Tests

@pytest.mark.asyncio
async def test_logout_payload_missing():
     with patch("services.user_services.verify_token") as mock_payload :
          mock_payload.return_value = None
          with pytest.raises(HTTPException) as exc:
               await logout("fadfadfafafasdf","asdfadsfasfasf")
          assert exc.value.status_code == 401
          assert exc.value.detail == "Unauthorized"

sample_refresh_payload = {
      "jti" : 1,
      "exp" : 1787220600,
      "type" : "access",
      "user_name" : "furkhan"
}

@pytest.mark.asyncio
async def test_logout_wrong_type():
     with patch("services.user_services.verify_token") as mock_payload :
          mock_payload.side_effect = [access_payload,sample_refresh_payload]
          with pytest.raises(HTTPException) as exc:
               await logout("Fdsafadsfasd","fadfasfasdf")
          assert exc.value.status_code == 401
          assert exc.value.detail == "Invalid Token Type"

@pytest.mark.asyncio
async def test_logout_internal_server_error():
     with patch("services.user_services.verify_token") as mock_payload,\
          patch("services.user_services.time.time") as mock_time, \
          patch("services.user_services.r.set") as mock_set, \
          patch("services.user_services.revoketoken") as mock_revoked_token :
               mock_payload.side_effect = [access_payload,refresh_payload]
               mock_time.return_value = "36666666"
               mock_set.return_value = 1
               mock_revoked_token.return_value = None
               with pytest.raises(HTTPException) as exc:
                    await logout("Fadfasdf","adfasdfads")
               assert exc.value.status_code == 500
               assert exc.value.detail == "Internal Server Error"
          

@pytest.mark.asyncio
async def test_logout():
     with patch("services.user_services.verify_token") as mock_payload,\
          patch("services.user_services.time.time") as mock_time, \
          patch("services.user_services.r.set") as mock_set, \
          patch("services.user_services.revoketoken") as mock_revoked_token, \
          patch("services.user_services.manager.active_connection") as mock_active_connections, \
          patch("services.user_services.manager.remove_connection") as mock_remove_connections:
               mock_payload.side_effect = [access_payload,refresh_payload]
               mock_time.return_value = "36666666"
               mock_set.return_value = 1
               mock_revoked_token.return_value = True
               mock_ws = AsyncMock()
               mock_active_connections.get.return_value = mock_ws
               mock_remove_connections.return_value = True
               result = await logout("Fadsfaggsdgsdgf","asdfjvbhvjbnijijabn")
               assert result == {"message" : "logout successfully"}

#Token Checker Tests

def test_is_expired():
    with patch("services.user_services.r.get") as mock_get:
          mock_get.return_value = None
          result = is_expired(1)
          assert result == None

def test_is_expired_true():
    with patch("services.user_services.r.get") as mock_get:
          mock_get.return_value = 1
          with pytest.raises(HTTPException) as exc:
               result = is_expired(1)
          assert exc.value.status_code == 401
          assert exc.value.detail == "Revoked Token"
          