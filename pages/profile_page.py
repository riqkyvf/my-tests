from playwright.sync_api import Page

from config import BASE_URL, REQUEST_TIMEOUT_MS


class ProfilePage:
    def __init__(self, page: Page):
        self.page = page
        self.name_input = page.get_by_label("Имя")
        self.telegram_input = page.get_by_label("Telegram")
        self.timezone_list = page.get_by_label("Часовой пояс")
        self.about_info_input = page.get_by_label("О себе")
        self.save_button = page.get_by_role("button", name="Сохранить")
        self.skill_input = page.get_by_label("Навык")
        self.skill_tags = page.locator("[data-skill-tag]")
        self.type_skill = page.locator("select[id='pomidorqa-profile-skill-type']")
        self.add_skill_button = page.get_by_role("button", name="Добавить")
        self.can_help_skills = page.get_by_test_id("can-help-skills")
        self.want_to_learn_skills = page.locator('[data-skills="want_to_learn"]')

    def open(self):
        self.page.goto(f"{BASE_URL}/pomidorqa/profile")

    def timezone_option(self, value: str):
        return self.timezone_list.locator(f'option[value="{value}"]')

    @property
    def timezone_options(self):
        return self.timezone_list.get_by_role("option")

    def fill_text_data(self, name, telegram, about_info):
        self.name_input.fill(name)
        self.telegram_input.fill(telegram)
        self.about_info_input.fill(about_info)

    def add_skill(self, name: str, skill_type: str):
        self.skill_input.fill(name)
        self.type_skill.select_option(value=skill_type)

        with self._expect_form_response():
            self.add_skill_button.click()

    def remove_skill(self, skill_name: str, skill_type: str):
        skill = self.saved_skill(skill_name, skill_type)

        with self._expect_form_response():
            skill.get_by_role("button", name=f"Убрать {skill_name}", exact=True).click()

    def saved_skill(self, skill_name: str, skill_type: str):
        blocks = {
            "can_help": self.can_help_skills,
            "want_to_learn": self.want_to_learn_skills,
        }
        block = blocks[skill_type]

        return block.locator("[data-skill-tag]").filter(
            has=self.page.get_by_role("button", name=f"Убрать {skill_name}", exact=True)
        )

    def save(self):
        with self._expect_form_response():
            self.save_button.click()

    def _expect_form_response(self):
        return self.page.expect_response(
            lambda response: (
                response.url == f"{BASE_URL}/pomidorqa/profile"
                and response.request.method == "POST"
            ),
            timeout=REQUEST_TIMEOUT_MS,
        )
