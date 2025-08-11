import pytest
import asyncio
from app.auth import redis as redis_mod

class DummyRedis:
    def __init__(self):
        self.set_called = False
        self.exists_called = False
        self.last_args = None
    async def set(self, key, value, ex=None):
        self.set_called = True
        self.last_args = (key, value, ex)
        return True
    async def exists(self, key):
        self.exists_called = True
        self.last_args = (key,)
        return key == "blacklist:revokedjti"

@pytest.mark.asyncio
async def test_get_redis_returns_client(monkeypatch):
    async def fake_from_url(url):
        return DummyRedis()
    monkeypatch.setattr("redis.asyncio.from_url", fake_from_url)
    # Remove cached redis if present
    if hasattr(redis_mod.get_redis, "redis"):
        delattr(redis_mod.get_redis, "redis")
    client = await redis_mod.get_redis()
    assert isinstance(client, DummyRedis)

@pytest.mark.asyncio
async def test_add_to_blacklist(monkeypatch):
    dummy = DummyRedis()
    async def fake_get_redis():
        return dummy
    monkeypatch.setattr(redis_mod, "get_redis", fake_get_redis)
    await redis_mod.add_to_blacklist("jti123", 123)
    assert dummy.set_called
    assert dummy.last_args == ("blacklist:jti123", "1", 123)

@pytest.mark.asyncio
async def test_is_blacklisted(monkeypatch):
    dummy = DummyRedis()
    async def fake_get_redis():
        return dummy
    monkeypatch.setattr(redis_mod, "get_redis", fake_get_redis)
    result = await redis_mod.is_blacklisted("revokedjti")
    assert dummy.exists_called
    assert result is True
    result2 = await redis_mod.is_blacklisted("notrevoked")
    assert result2 is False
