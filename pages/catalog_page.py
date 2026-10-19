from urllib.parse import urljoin

from playwright.sync_api import Locator, Page

from config import BASE_URL, REQUEST_TIMEOUT_MS


class CatalogPage:
    def __init__(self, page: Page):
        self.page = page
        self.cards = page.get_by_test_id("person-card")
        self.skill_input = page.get_by_role("textbox", name="Навык", exact=True)
        self.search_button = page.get_by_role("button", name="Найти", exact=True)
        self.empty_results = page.get_by_role("main").get_by_text(
            "Пока никого не нашли по этому фильтру", exact=True
        )

    def open(self):
        self.page.goto(f"{BASE_URL}/pomidorqa")

    def open_person(self, card: Locator):
        href = card.get_attribute("href")
        if not href:
            raise ValueError("У карточки участника отсутствует ссылка на профиль")
        target_url = urljoin(self.page.url, href)
        card.click()
        self.page.wait_for_url(target_url, timeout=REQUEST_TIMEOUT_MS)

    def search_by_skill(self, skill_name: str):
        self.skill_input.fill(skill_name)
        self.search_button.click()

    def card_by_name(self, name: str):
        return self.cards.filter(has=self.page.get_by_text(name, exact=True))

    def card_by_skill(self, skill_name: str):
        return self.cards.filter(
            has=self.page.locator("[data-skill-tag]").and_(
                self.page.get_by_text(skill_name, exact=True)
            )
        )

    def card_by_id(self, person_id: str):
        return self.cards.and_(self.page.locator(f'[data-person-id="{person_id}"]'))
