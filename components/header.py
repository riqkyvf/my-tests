from playwright.sync_api import Page


class Header:
    def __init__(self, page: Page):
        self.page = page
        self.logout_button = page.get_by_test_id("PomidorqaHeader-logout-button")
        self.login_link = page.get_by_test_id("PomidorqaHeader-login-link")
        self.profile_link = page.get_by_test_id("PomidorqaHeader-profile-link")

    def logout(self):
        self.logout_button.click()

    def open_profile(self):
        self.profile_link.click()
