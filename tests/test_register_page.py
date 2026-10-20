import allure
import pytest
from playwright.sync_api import expect

from config import BASE_URL, REQUEST_TIMEOUT_MS


@pytest.mark.parametrize("password_length", [8, 9], ids=["exactly_8_chars", "exactly_9_chars"])
@allure.feature("Регистрация")
@allure.title("Регистрация авторизует участника и создаёт профиль ({param_id})")
def test_registration_logs_user_in_and_creates_profile(
    page, register_page, registration_user, header, profile_page, password_length
):
    with allure.step("Открыть форму регистрации"):
        user = registration_user
        register_page.open()

    with allure.step("Зарегистрировать нового участника"):
        password = "1" * password_length
        register_page.register(user["name"], user["email"], password)

    with allure.step("Проверить автоматический вход"):
        expect(page).to_have_url(f"{BASE_URL}/pomidorqa", timeout=REQUEST_TIMEOUT_MS)
        expect(header.logout_button).to_be_visible()
        expect(header.login_link).to_be_hidden()

    with allure.step("Проверить имя и часовой пояс созданного профиля"):
        profile_page.open()
        expect(profile_page.name_input).to_have_value(user["name"])
        expect(profile_page.timezone_list).to_have_value("Europe/Moscow")


@pytest.mark.parametrize(
    "field_key, field_name",
    [("name", "name_input"), ("email", "email_input"), ("password", "password_input")],
    ids=["missing_name", "missing_email", "missing_password"],
)
@allure.feature("Регистрация")
@allure.title("Регистрация отклоняет пустое обязательное поле ({field_key})")
def test_registration_requires_each_field(
    page, register_page, registration_user, header, field_key, field_name
):
    with allure.step("Открыть регистрацию с одним незаполненным полем"):
        user = {**registration_user, field_key: ""}
        register_page.open()

    with allure.step("Попытаться зарегистрироваться"):
        register_page.register(user["name"], user["email"], user["password"])

    with allure.step("Проверить HTML-валидацию и отсутствие авторизации"):
        field = getattr(register_page, field_name)
        expect(field).to_be_empty()
        expect(field).to_have_attribute("required", "")
        expect(field.and_(page.locator(":invalid"))).to_have_count(1)
        expect(field).to_be_focused()
        expect(page).to_have_url(f"{BASE_URL}/pomidorqa/auth/register")
        expect(header.login_link).to_be_visible()
        expect(header.logout_button).to_be_hidden()


@allure.feature("Регистрация")
@allure.title("Регистрация отклоняет пароль из семи символов")
def test_registration_rejects_seven_character_password(
    page, register_page, registration_user, header
):
    with allure.step("Открыть форму регистрации"):
        user = registration_user
        register_page.open()

    with allure.step("Попытаться зарегистрироваться с коротким паролем"):
        register_page.register(user["name"], user["email"], "1234567")

    with allure.step("Проверить минимальную длину и отсутствие авторизации"):
        password = register_page.password_input
        expect(password).to_have_value("1234567")
        expect(password).to_have_attribute("minlength", "8")
        expect(password.and_(page.locator(":invalid"))).to_have_count(1)
        expect(password).to_be_focused()
        expect(page).to_have_url(f"{BASE_URL}/pomidorqa/auth/register")
        expect(header.login_link).to_be_visible()
        expect(header.logout_button).to_be_hidden()


@allure.feature("Регистрация")
@allure.title("Повторная регистрация на занятый email запрещена")
def test_registration_rejects_existing_email(
    page, register_page, registration_user, created_account, header
):
    with allure.step("Открыть форму регистрации"):
        register_page.open()

    with allure.step("Отправить данные с уже зарегистрированным email"):
        register_page.register(
            registration_user["name"],
            created_account["user"]["email"],
            registration_user["password"],
        )

    with allure.step("Проверить понятную ошибку и отсутствие авторизации"):
        expect(register_page.error).to_have_text("Этот email уже зарегистрирован")
        expect(page).to_have_url(f"{BASE_URL}/pomidorqa/auth/register")
        expect(header.login_link).to_be_visible()
        expect(header.logout_button).to_be_hidden()


@pytest.mark.parametrize(
    "email",
    ["not-an-email", "@example.com", "user@"],
    ids=["missing_at", "missing_local_part", "missing_domain"],
)
@allure.feature("Регистрация")
@allure.title("Регистрация блокирует неверный формат email ({param_id})")
def test_registration_rejects_invalid_email_format(
    page, register_page, registration_user, header, email
):
    with allure.step("Открыть форму регистрации"):
        register_page.open()

    with allure.step("Отправить данные с некорректным email"):
        register_page.register(registration_user["name"], email, registration_user["password"])

    with allure.step("Проверить HTML-валидацию email и отсутствие авторизации"):
        expect(register_page.email_input).to_have_value(email)
        expect(register_page.email_input).to_have_attribute("type", "email")
        expect(register_page.email_input.and_(page.locator(":invalid"))).to_have_count(1)
        expect(register_page.email_input).to_be_focused()
        expect(page).to_have_url(f"{BASE_URL}/pomidorqa/auth/register")
        expect(header.login_link).to_be_visible()
        expect(header.logout_button).to_be_hidden()
