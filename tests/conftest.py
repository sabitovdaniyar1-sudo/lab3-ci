import pytest
import sqlite3
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from logger import get_logger

BASE_URL = "http://web:5000"
HUB_URL = "http://selenium-hub:4444/wd/hub"

@pytest.fixture(scope="session")
def logger():
    return get_logger("lab3")

@pytest.fixture(scope="session")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Remote(
        command_executor=HUB_URL,
        options=options
    )
    yield driver
    driver.quit()

@pytest.fixture
def api_url():
    return BASE_URL + "/api/users"

@pytest.fixture
def db_path():
    return "users.db"

@pytest.fixture
def clear_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")
    conn.commit()
    conn.close()

