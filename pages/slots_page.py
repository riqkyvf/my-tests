from playwright.sync_api import Page, expect

from config import BASE_URL, REQUEST_TIMEOUT_MS


class SlotsPage:
    def __init__(self, page: Page):
        self.page = page
        self.date_input = page.locator('[id="pomidorqa-slots-date"]')
        self.time_input = page.locator('[id="pomidorqa-slots-time"]')
        self.add_button = page.get_by_role("button", name="Добавить слот")
        self.slot_cards = page.locator("[data-slot-id]")
        self.free_slot_cards = page.locator('[data-slot-id][data-slot-status="free"]')

    def open(self):
        self.page.goto(f"{BASE_URL}/pomidorqa/profile/slots")

    def create_slot(self, date, time):
        self.date_input.fill(date)
        self.time_input.fill(time)
        self.add_button.click()

    def create_slot_and_wait(self, date: str, time: str):
        with self.page.expect_response(
            lambda response: (
                response.url == f"{BASE_URL}/pomidorqa/profile/slots"
                and response.request.method == "POST"
            ),
            timeout=REQUEST_TIMEOUT_MS,
        ) as response_info:
            self.create_slot(date, time)

        response = response_info.value
        assert response.status in (200, 303), f"Обработка формы слота: HTTP {response.status}"
        expect(self.add_button).to_be_enabled(timeout=REQUEST_TIMEOUT_MS)

    def slot_ids(self) -> list[str]:
        return self.slot_cards.evaluate_all("cards => cards.map(card => card.dataset.slotId)")

    def slot_by_id(self, slot_id):
        return self.page.locator(f'[data-slot-id="{slot_id}"]')

    def remove_button_for_slot(self, slot_id: str):
        return self.slot_by_id(slot_id).get_by_role("button", name="Удалить", exact=True)

    def remove_slot(self, slot_id: str):

        with self.page.expect_response(
            lambda response: (
                response.url == f"{BASE_URL}/pomidorqa/profile/slots"
                and response.request.method == "POST"
            ),
            timeout=REQUEST_TIMEOUT_MS,
        ):
            self.remove_button_for_slot(slot_id).click()
