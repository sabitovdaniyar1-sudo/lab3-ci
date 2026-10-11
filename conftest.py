import os
import time
import uuid
import sqlite3

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from logger import get_logger

# ИСПРАВЛЕНО: conftest.py лежит в корне проекта (иначе не находится модуль logger);
# адреса и путь к БД берутся из переменных окружения docker-compose
BASE_URL = os.environ.get("BASE_URL", "http://web:5000")
HUB_URL = os.environ.get("HUB_URL", "http://selenium-hub:4444/wd/hub")
DB_PATH = os.environ.get("USERS_DB", "users.db")


@pytest.fixture(scope="session")
def logger():
    return get_logger("lab3")


@pytest.fixture
def driver():
    # ИСПРАВЛЕНО: драйвер создаётся на каждый тест (а не на сессию), чтобы при
    # параллельном запуске не занимать сессии Grid до конца прогона;
    # повторные попытки - пока Grid и браузерный узел не запустились
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    last_error = None
    for _ in range(30):
        try:
            driver = webdriver.Remote(command_executor=HUB_URL, options=options)
            break
        except Exception as e:
            last_error = e
            time.sleep(2)
    else:
        raise last_error
    yield driver
    driver.quit()


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def api_url():
    return BASE_URL + "/api/users"


@pytest.fixture
def db_path():
    return DB_PATH


@pytest.fixture
def uid():
    # ИСПРАВЛЕНО: уникальный суффикс для email. Тесты выполняются параллельно
    # с одной БД, а email UNIQUE - одинаковые адреса давали бы ошибки.
    return uuid.uuid4().hex[:8]


@pytest.fixture
def clear_db(db_path):
    # Не используется при параллельном запуске (удалила бы данные соседних тестов)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")
    conn.commit()
    conn.close()
