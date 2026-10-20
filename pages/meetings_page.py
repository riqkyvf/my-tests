from playwright.sync_api import Page, Response

from config import BASE_URL, REQUEST_TIMEOUT_MS


class MeetingsPage:
    def __init__(self, page: Page):
        self.page = page
        self.upcoming = page.locator("[data-testid='upcoming-meetings']")
        self.cards = self.upcoming.locator("[data-booking-id]")
        self.past = page.locator("section").filter(
            has=page.get_by_role("heading", name="Прошедшие и отменённые", exact=True)
        )

        self.past_cards = self.past.locator("[data-booking-id]")
        self.cancel_error = page.get_by_test_id("cancel-error")

    def open(self):
        self.page.goto(f"{BASE_URL}/pomidorqa/bookings")

    def meeting_with(self, participant_name: str):
        return self.cards.filter(has=self.page.get_by_text(participant_name, exact=True))

    def upcoming_by_id(self, booking_id: str):
        return self.upcoming.locator(f'[data-booking-id="{booking_id}"]')

    def past_by_id(self, booking_id: str):
        return self.past.locator(f'[data-booking-id="{booking_id}"]')

    def past_cancel_button(self, booking_id: str):
        return self.past_by_id(booking_id).get_by_role("button", name="Отменить", exact=True)

    def cancel_meeting(self, booking_id: str) -> Response:
        with self.page.expect_response(
            lambda response: (
                response.url == f"{BASE_URL}/pomidorqa/bookings"
                and response.request.method == "POST"
            ),
            timeout=REQUEST_TIMEOUT_MS,
        ) as response_info:
            self.upcoming_by_id(booking_id).get_by_role(
                "button", name="Отменить", exact=True
            ).click()
        return response_info.value
