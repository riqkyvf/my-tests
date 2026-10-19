import uuid

import allure
from playwright.sync_api import Page, expect

from config import BASE_URL


@allure.feature("Авторизация")
@allure.title("Неизвестный email вызывает общую ошибку входа")
def test_login_with_invalid_credentials(page: Page, login_page):
    with allure.step("Открыть страницу входа"):
        login_page.open()

    with allure.step("Войти с неизвестным email"):
        login_page.login(uuid.uuid4().hex + "@example.com", "12345678")

    with allure.step("Проверить общую ошибку и сохранение формы входа"):
        expect(login_page.error).to_be_visible()
        expect(login_page.error).to_have_text("Неверный email или пароль")

        expect(page).to_have_url(f"{BASE_URL}/pomidorqa/auth/login")


@allure.feature("Авторизация")
@allure.title("Участник входит с правильными email и паролем")
def test_login_with_valid_credentials(page: Page, created_account, login_page, header):
    user = created_account["user"]

    with allure.step("Открыть страницу входа"):
        login_page.open()

    with allure.step("Войти с данными зарегистрированного участника"):
        login_page.login(user["email"], user["password"])

    with allure.step("Проверить успешный вход"):
        expect(page).to_have_url(f"{BASE_URL}/pomidorqa")
        expect(header.logout_button).to_be_visible()


@allure.feature("Авторизация")
@allure.title("Неверный пароль вызывает общую ошибку входа")
def test_login_with_invalid_password(page: Page, created_account, login_page, header):
    with allure.step("Открыть страницу входа для существующего аккаунта"):
        user = created_account["user"]

        login_page.open()

    with allure.step("Войти с неверным паролем"):
        login_page.login(user["email"], "invalidpass123")

    with allure.step("Проверить общую ошибку и отсутствие авторизации"):
        expect(login_page.error).to_be_visible()
        expect(login_page.error).to_have_text("Неверный email или пароль")

        expect(header.login_link).to_be_visible()

        expect(page).to_have_url(f"{BASE_URL}/pomidorqa/auth/login")


@allure.feature("Авторизация")
@allure.title("Выход сохраняет гостевое состояние после перезагрузки")
def test_logout(page: Page, header, logged_in_page):
    with allure.step("Выйти из аккаунта"):
        header.logout()

    with allure.step("Проверить гостевую шапку"):
        expect(header.login_link).to_be_visible()
        expect(header.logout_button).to_be_hidden()

    with allure.step("Перезагрузить страницу и проверить сохранение выхода"):
        page.reload()

        expect(header.login_link).to_be_visible()
        expect(header.logout_button).to_be_hidden()
