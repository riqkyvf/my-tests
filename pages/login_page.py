from playwright.sync_api import Page

from config import BASE_URL


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.email_input = page.get_by_label("Email")
        self.password_input = page.get_by_label("Пароль")
        self.submit_button = page.get_by_role("button", name="Войти")
        self.error = page.locator("form").get_by_role("alert")

    def open(self):
        self.page.goto(f"{BASE_URL}/pomidorqa/auth/login")

    def login(self, email, password):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()
