from playwright.sync_api import Page

from config import BASE_URL, REQUEST_TIMEOUT_MS


class PersonPage:
    def __init__(self, page: Page):
        self.page = page
        self.main = page.get_by_role("main")
        self.can_help_skills = self.main.get_by_text("Может помочь с", exact=True).locator("..")
        self.want_to_learn_skills = self.main.get_by_text("Хочет разобрать", exact=True).locator(
            ".."
        )
        self.days = page.get_by_role("group", name="Дни со слотами")
        self.times = page.get_by_role("group", name="Время слотов")
        self.slots_timezone = page.get_by_test_id("slots-timezone")
        self.booking_dialog = page.get_by_role("dialog")
        self.booking_slot_id = self.booking_dialog.locator('input[name="slotId"]')
        self.booking_submit_button = self.booking_dialog.locator('button[type="submit"]')
        self.confirm_button = self.booking_dialog.get_by_role(
            "button", name="Подтвердить", exact=True
        )
        self.cancel_confirmation_button = self.booking_dialog.get_by_role(
            "button", name="Отмена", exact=True
        )
        self.booking_success = self.booking_dialog.get_by_role("status")
        self.booking_error = self.booking_dialog.get_by_role("alert")
        self.close_button = self.booking_dialog.get_by_role("button", name="Закрыть", exact=True)

    def open(self, person_id: str):
        self.page.goto(f"{BASE_URL}/pomidorqa/people/{person_id}")

    def get_creator_name(self, name: str):
        return self.main.get_by_role("heading", name=name, exact=True)

    def skill_tag(self, skill_name: str, skill_type: str):
        blocks = {
            "can_help": self.can_help_skills,
            "want_to_learn": self.want_to_learn_skills,
        }
        return (
            blocks[skill_type]
            .locator("[data-skill-tag]")
            .and_(self.page.get_by_text(skill_name, exact=True))
        )

    def day_button(self, slot_date: str):
        return self.days.locator(f'button[data-date="{slot_date}"]')

    def slot_button(self, slot_id: str):
        return self.times.locator(f'button[data-slot-id="{slot_id}"]')

    def select_slot(self, slot_date: str, slot_time: str):
        self.day_button(slot_date).click()

        self.times.get_by_role(
            "button",
            name=slot_time,
            exact=True,
        ).click()

    def confirm_booking(self):
        self.confirm_button.click()

    def cancel_booking_confirmation(self):
        self.cancel_confirmation_button.click()

    def close_booking_dialog(self):
        self.close_button.click()

    def profile_text(self, text: str):
        return self.main.get_by_text(text, exact=True)

    def confirm_booking_and_close(self) -> str:
        self.confirm_booking()
        self.booking_success.wait_for(state="visible", timeout=REQUEST_TIMEOUT_MS)
        success_message = self.booking_success.inner_text()
        self.close_booking_dialog()
        self.booking_dialog.wait_for(state="hidden", timeout=REQUEST_TIMEOUT_MS)
        return success_message
