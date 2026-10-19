from playwright.sync_api import Page, expect

from config import BASE_URL, REQUEST_TIMEOUT_MS


class SlotsPage:
    def __init__(self, page: Page):
        self.page = page
        self.date_input = page.locator('[id="pomidorqa-slots-date"]')
        self.time_input = page.locator('[id="pomidorqa-slots-time"]')
        self.add_button = page.get_by_role("button", name="Добавить слот")
        self.error = page.get_by_role("main").get_by_role("alert")
        self.slot_cards = page.locator("[data-slot-id]")
        self.free_slot_cards = page.locator('[data-slot-id][data-slot-status="free"]')

    def open(self):
        self.page.goto(f"{BASE_URL}/pomidorqa/profile/slots")

    def submit_slot(self, date: str, time: str):
        self.date_input.fill(date)
        self.time_input.fill(time)
        self.add_button.click()

    def create_slot(self, date: str, time: str):
        with self._expect_form_response():
            self.submit_slot(date, time)

        expect(self.add_button).to_be_enabled(timeout=REQUEST_TIMEOUT_MS)

    def slot_ids(self) -> list[str]:
        return self.slot_cards.evaluate_all("cards => cards.map(card => card.dataset.slotId)")

    def slot_by_id(self, slot_id):
        return self.page.locator(f'[data-slot-id="{slot_id}"]')

    def remove_button_for_slot(self, slot_id: str):
        return self.slot_by_id(slot_id).get_by_role("button", name="Удалить", exact=True)

    def remove_slot(self, slot_id: str):

        with self._expect_form_response():
            self.remove_button_for_slot(slot_id).click()

    def _expect_form_response(self):
        return self.page.expect_response(
            lambda response: (
                response.url == f"{BASE_URL}/pomidorqa/profile/slots"
                and response.request.method == "POST"
            ),
            timeout=REQUEST_TIMEOUT_MS,
        )
