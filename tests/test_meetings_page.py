import allure
from playwright.sync_api import expect

from pages.meetings_page import MeetingsPage


@allure.feature("Мои встречи")
@allure.title("Ведущий и гость видят только свои ближайшие и отменённые встречи")
def test_meetings_lists_show_only_current_participants_bookings(mixed_meetings):
    for group_index, group in enumerate(mixed_meetings):
        other_group = mixed_meetings[1 - group_index]
        for role, partner_role in (("host", "guest"), ("guest", "host")):
            with allure.step(f"Открыть встречи участника {role} пары {group_index + 1}"):
                meetings = MeetingsPage(group[role]["page"])
                meetings.open()
                partner_name = group[partner_role]["user"]["name"]

            with allure.step("Проверить свою ближайшую и свою отменённую встречу"):
                expect(meetings.cards).to_have_count(1)
                expect(meetings.past_cards).to_have_count(1)
                expect(meetings.upcoming_by_id(group["upcoming_id"])).to_contain_text(partner_name)
                cancelled = meetings.past_by_id(group["cancelled_id"])
                expect(cancelled).to_contain_text(partner_name)
                expect(cancelled).to_contain_text("отменено")

            with allure.step("Проверить распределение своих записей по разделам"):
                expect(meetings.past_by_id(group["upcoming_id"])).to_have_count(0)
                expect(meetings.upcoming_by_id(group["cancelled_id"])).to_have_count(0)

            with allure.step("Проверить отсутствие чужих записей в обоих разделах"):
                for booking_id in (other_group["upcoming_id"], other_group["cancelled_id"]):
                    expect(meetings.upcoming_by_id(booking_id)).to_have_count(0)
                    expect(meetings.past_by_id(booking_id)).to_have_count(0)
