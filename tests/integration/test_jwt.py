import pytest
import asyncio
from uuid import uuid4
from jose import jwt
from fastapi import HTTPException
from app.auth.jwt import create_token, decode_token, get_current_user
from app.schemas.token import TokenType
from app.core.config import get_settings

settings = get_settings()

def test_create_token_with_uuid():
	# Covers line 53: user_id as UUID
	user_id = uuid4()
	token = create_token(user_id, TokenType.ACCESS)
	decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
	assert decoded["sub"] == str(user_id)

def test_create_token_raises_http_exception(monkeypatch):
	# Covers line 65: Exception in jwt.encode
	def fake_encode(*args, **kwargs):
		raise Exception("encode error")
	monkeypatch.setattr("jose.jwt.encode", fake_encode)
	with pytest.raises(HTTPException) as exc_info:
		create_token(str(uuid4()), TokenType.ACCESS)
	assert exc_info.value.status_code == 500

@pytest.mark.asyncio
async def test_decode_token_invalid_type():
	# Covers lines 83-84: Invalid token type
	payload = {
		"sub": "user",
		"type": "refresh",  # Should be 'access'
		"exp": 9999999999,
		"iat": 9999999999,
		"jti": "fakejti"
	}
	token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
	with pytest.raises(HTTPException) as exc_info:
		await decode_token(token, TokenType.ACCESS)
	assert exc_info.value.status_code == 401
	assert exc_info.value.detail == "Invalid token type"


@pytest.mark.asyncio
async def test_decode_token_expired():
	# Covers lines 97-134: Token expired
	payload = {
		"sub": "user",
		"type": "access",
		"exp": 1,  # Already expired
		"iat": 1,
		"jti": "expiredjti"
	}
	token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
	with pytest.raises(HTTPException) as exc_info:
		await decode_token(token, TokenType.ACCESS)
	assert exc_info.value.status_code == 401
	assert exc_info.value.detail == "Token has expired"

@pytest.mark.asyncio
async def test_decode_token_jwt_error():
	# Covers lines 97-134: JWTError
	with pytest.raises(HTTPException) as exc_info:
		await decode_token("invalid.token.value", TokenType.ACCESS)
	assert exc_info.value.status_code == 401
	assert exc_info.value.detail == "Could not validate credentials"

class DummyUser:
	is_active = True

class DummyInactiveUser:
	is_active = False

class DummyDB:
	def query(self, model):
		class DummyQuery:
			def filter(self, *args, **kwargs):
				return self
			def first(self):
				return DummyUser()
		return DummyQuery()

class DummyDBInactive:
	def query(self, model):
		class DummyQuery:
			def filter(self, *args, **kwargs):
				return self
			def first(self):
				return DummyInactiveUser()
		return DummyQuery()

@pytest.mark.asyncio
async def test_get_current_user_success(monkeypatch):
	# Covers lines 147-167: Success path
	async def fake_decode_token(token, token_type, verify_exp=True):
		return {"sub": "user"}
	monkeypatch.setattr("app.auth.jwt.decode_token", fake_decode_token)
	user = await get_current_user(token="token", db=DummyDB())
	assert user.is_active is True

@pytest.mark.asyncio
async def test_get_current_user_user_not_found(monkeypatch):
	# Covers lines 147-167: User not found
	class DummyDBNotFound:
		def query(self, model):
			class DummyQuery:
				def filter(self, *args, **kwargs):
					return self
				def first(self):
					return None
			return DummyQuery()
	async def fake_decode_token(token, token_type, verify_exp=True):
		return {"sub": "user"}
	monkeypatch.setattr("app.auth.jwt.decode_token", fake_decode_token)
	with pytest.raises(HTTPException) as exc_info:
		await get_current_user(token="token", db=DummyDBNotFound())
	assert exc_info.value.status_code == 401
	assert "User not found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_current_user_inactive_user(monkeypatch):
	# Covers lines 147-167: Inactive user
	async def fake_decode_token(token, token_type, verify_exp=True):
		return {"sub": "user"}
	monkeypatch.setattr("app.auth.jwt.decode_token", fake_decode_token)
	with pytest.raises(HTTPException) as exc_info:
		await get_current_user(token="token", db=DummyDBInactive())
	assert exc_info.value.status_code == 401
	assert "Inactive user" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_current_user_exception(monkeypatch):
	# Covers lines 147-167: Exception path
	async def fake_decode_token(token, token_type, verify_exp=True):
		raise Exception("unexpected error")
	monkeypatch.setattr("app.auth.jwt.decode_token", fake_decode_token)
	with pytest.raises(HTTPException) as exc_info:
		await get_current_user(token="token", db=DummyDB())
	assert exc_info.value.status_code == 401
	assert "unexpected error" in exc_info.value.detail
