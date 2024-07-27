"""
Template for testing asynchronous operations in PyQt applications using pytest and qasync.
Key feature: sequential execution of async tasks.
"""

import pytest
import sys
import asyncio
from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop
from takeb1 import RemovablesView


# Global semaphore with an initial value of 1
semaphore = asyncio.Semaphore(1)


@pytest.fixture(scope="session")
def app():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    yield app
    app.exit()

async def solely_execute(coro):
    async with semaphore:
        await coro


@pytest.mark.asyncio
async def test_singleton_instance(app):
    await solely_execute(async_test_singleton_instance())

async def async_test_singleton_instance():
    window = RemovablesView.singleton_instance()
    assert window is not None
    assert isinstance(window, RemovablesView)


@pytest.mark.asyncio
async def test_update_content_empty(app):
    await solely_execute(async_test_update_content_empty())

async def async_test_update_content_empty():
    window = RemovablesView.singleton_instance()
    await window.update_content([])
    assert not window.isVisible()


@pytest.mark.asyncio
async def test_update_content_with_device(app):
    await solely_execute(async_test_update_content_with_device())

async def async_test_update_content_with_device():
    window = RemovablesView.singleton_instance()
    devices = [{'drive': 'E:'}]
    await window.update_content(devices)
    assert window.isVisible()
    assert len(window.device_qlabels) == len(devices)
    assert window.device_qlabels[0].text() == "SD card inserted: E:"


@pytest.mark.asyncio
async def test_close_button(app):
    await solely_execute(async_test_close_button())

async def async_test_close_button():
    window = RemovablesView.singleton_instance()
    window.show()
    assert window.isVisible()
    window.button_close.click()
    assert not window.isVisible()
