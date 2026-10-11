from selenium.webdriver.common.by import By
import time


def test_ui_register_user(driver, base_url, logger, uid):
    logger.info("UI: регистрация пользователя")
    email = f"ivan_ui_{uid}@test.com"
    driver.get(base_url + "/register")
    driver.find_element(By.NAME, "name").send_keys("Ivan")
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.TAG_NAME, "button").click()
    time.sleep(1)
    assert f"Ivan ({email})" in driver.page_source
