import allure


@allure.feature("Тестовый API аккаунтов")
@allure.title("Созданный через API аккаунт получает сессионную cookie")
def test_created_account_has_session_cookie(created_account):
    with allure.step("Прочитать имена cookies созданного аккаунта"):
        api = created_account["api_context"]
        cookies = api.storage_state()["cookies"]

        cookie_names = [cookie["name"] for cookie in cookies]

    with allure.step("Проверить наличие сессионной cookie"):
        assert "pomidorqa_session" in cookie_names
