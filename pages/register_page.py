from playwright.sync_api import Page

from config import BASE_URL


class RegisterPage:
    def __init__(self, page: Page):
        self.page = page
        self.name_input = page.get_by_label("Имя", exact=True)
        self.email_input = page.get_by_label("Email", exact=True)
        # Подпись пароля также включает подсказку «Не короче 8 символов».
        self.password_input = page.get_by_label("Пароль")
        self.error = page.get_by_role("main").get_by_role("alert")
        self.submit_button = page.get_by_role("button", name="Зарегистрироваться", exact=True)

    def open(self):
        self.page.goto(f"{BASE_URL}/pomidorqa/auth/register")

    def register(self, name: str, email: str, password: str):
        self.name_input.fill(name)
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()
