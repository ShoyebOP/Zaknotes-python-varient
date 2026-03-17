import pytest
import asyncio
import time
from src.gemini_api_wrapper import BackoffManager

@pytest.mark.anyio
async def test_backoff_async_increment():
    manager = BackoffManager(initial_delay=0.1, max_delay=1.0)
    
    # First attempt
    assert manager.get_delay(0) == 0.1
    # Second attempt
    assert manager.get_delay(1) == 0.2
    # Third attempt
    assert manager.get_delay(2) == 0.4
    # Max delay
    assert manager.get_delay(10) == 1.0

@pytest.mark.anyio
async def test_backoff_async_sleep(monkeypatch):
    manager = BackoffManager(initial_delay=0.1, max_delay=1.0)
    
    sleep_calls = []
    async def mock_sleep(seconds):
        sleep_calls.append(seconds)
    
    monkeypatch.setattr(asyncio, "sleep", mock_sleep)
    
    await manager.async_sleep(0)
    assert sleep_calls == [0.1]
    
    await manager.async_sleep(1)
    assert sleep_calls == [0.1, 0.2]

def test_backoff_sync_sleep(monkeypatch):
    manager = BackoffManager(initial_delay=0.1, max_delay=1.0)
    
    sleep_calls = []
    def mock_sleep(seconds):
        sleep_calls.append(seconds)
    
    monkeypatch.setattr(time, "sleep", mock_sleep)
    
    manager.sync_sleep(0)
    assert sleep_calls == [0.1]
    
    manager.sync_sleep(1)
    assert sleep_calls == [0.1, 0.2]
