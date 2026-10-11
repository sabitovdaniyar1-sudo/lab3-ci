import sqlite3
import requests
from selenium.webdriver.common.by import By
import time


def test_integration_api_ui_db(driver, base_url, api_url, db_path, logger, uid):
    logger.info("Интеграционный тест: API -> DB -> UI")
    email = f"alex_int_{uid}@test.com"
    payload = {"name": "Alex", "email": email}
    resp = requests.post(api_url, json=payload)
    assert resp.status_code == 201
    user_id = resp.json()["id"]

    conn = sqlite3.connect(db_path, timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    assert user == ("Alex", email)

    driver.get(base_url)
    time.sleep(1)
    assert f"Alex ({email})" in driver.page_source
