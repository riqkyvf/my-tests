import allure
from playwright.sync_api import expect

from config import BASE_URL


@allure.feature("Доступ и сессия")
@allure.title("Защищённая страница требует входа у гостя ({param_id})")
def test_anonymous_guest_cannot_open_protected_page(page, protected_page, login_page, header):
    with allure.step("Открыть защищённую страницу без авторизации"):
        protected_page.open()

    with allure.step("Проверить перенаправление на вход и гостевое состояние"):
        expect(page).to_have_url(f"{BASE_URL}/pomidorqa/auth/login")
        expect(login_page.email_input).to_be_visible()
        expect(login_page.password_input).to_be_visible()
        expect(header.login_link).to_be_visible()
        expect(header.logout_button).to_be_hidden()


@allure.feature("Доступ и сессия")
@allure.title("После выхода защищённая страница требует входа ({param_id})")
def test_protected_page_requires_login_after_logout(
    page, protected_page, login_page, header, logged_in_page
):
    with allure.step("Проверить доступ авторизованного участника"):
        protected_page.open()
        expect(page).not_to_have_url(f"{BASE_URL}/pomidorqa/auth/login")
        expect(header.logout_button).to_be_visible()

    with allure.step("Выйти и повторно открыть защищённую страницу"):
        header.logout()
        expect(header.login_link).to_be_visible()
        protected_page.open()

    with allure.step("Проверить требование нового входа"):
        expect(page).to_have_url(f"{BASE_URL}/pomidorqa/auth/login")
        expect(login_page.email_input).to_be_visible()
        expect(login_page.password_input).to_be_visible()
        expect(header.logout_button).to_be_hidden()
