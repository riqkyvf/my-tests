from datetime import date

import allure
from playwright.sync_api import expect

from helpers.dates import format_slot_date
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


@allure.feature("Мои встречи")
@allure.title("Один участник видит встречи, в которых он ведущий и гость")
def test_participant_sees_meetings_in_both_roles(meetings_in_both_roles):
    with allure.step("Открыть встречи участника, выступающего в обеих ролях"):
        prepared = meetings_in_both_roles
        participant = prepared["participant"]
        meetings = MeetingsPage(participant["page"])
        meetings.open()

    with allure.step("Проверить обе ближайшие встречи, собеседников, даты и время"):
        expect(meetings.cards).to_have_count(2)
        expect(meetings.past_cards).to_have_count(0)
        for role, partner_role in (("as_host", "guest"), ("as_guest", "host")):
            booking = prepared[role]
            card = meetings.upcoming_by_id(booking["booking_id"])
            expect(card).to_contain_text(booking[partner_role]["user"]["name"])
            expect(card).to_contain_text(format_slot_date(date.fromisoformat(booking["slot_date"])))
            expect(card).to_contain_text(booking["slot_time"])

    with allure.step("Проверить сохранение обеих встреч после перезагрузки"):
        participant["page"].reload()
        expect(meetings.cards).to_have_count(2)
        for role in ("as_host", "as_guest"):
            expect(meetings.upcoming_by_id(prepared[role]["booking_id"])).to_be_visible()

    with allure.step("Проверить общий ID у собеседников и отсутствие чужой встречи"):
        for role, partner_role, other_role in (
            ("as_host", "guest", "as_guest"),
            ("as_guest", "host", "as_host"),
        ):
            booking = prepared[role]
            partner_meetings = MeetingsPage(booking[partner_role]["page"])
            partner_meetings.open()
            expect(partner_meetings.cards).to_have_count(1)
            expect(partner_meetings.upcoming_by_id(booking["booking_id"])).to_contain_text(
                participant["user"]["name"]
            )
            expect(
                partner_meetings.upcoming_by_id(prepared[other_role]["booking_id"])
            ).to_have_count(0)
