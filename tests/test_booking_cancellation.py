from datetime import date, timedelta

import allure
import pytest
from playwright.sync_api import expect

from helpers.dates import format_slot_date, now_in_moscow
from pages.meetings_page import MeetingsPage
from pages.person_page import PersonPage
from pages.slots_page import SlotsPage


@pytest.mark.parametrize("cancelled_by", ["host", "guest"])
@allure.feature("Отмена бронирования")
@allure.title("Отмена освобождает слот для повторной брони ({cancelled_by})")
def test_cancelled_meeting_frees_slot_for_another_user(booked_meeting, user_factory, cancelled_by):
    with allure.step("Открыть встречу отменяющего участника"):
        host = booked_meeting["host"]
        guest = booked_meeting["guest"]
        old_booking_id = booked_meeting["booking_id"]
        slot_id = booked_meeting["slot_id"]

        canceller = booked_meeting[cancelled_by]
        meetings = MeetingsPage(canceller["page"])
        meetings.open()
        expect(meetings.upcoming_by_id(old_booking_id)).to_be_visible()

    with allure.step("Отменить бронирование"):
        meetings.cancel_meeting(old_booking_id)
        expect(meetings.past_by_id(old_booking_id)).to_contain_text("отменено")

    with allure.step("Проверить отменённую встречу у обеих сторон"):
        for participant in (host, guest):
            participant_meetings = MeetingsPage(participant["page"])
            participant_meetings.open()
            expect(participant_meetings.past_by_id(old_booking_id)).to_contain_text("отменено")
            expect(participant_meetings.upcoming_by_id(old_booking_id)).to_have_count(0)
            expect(participant_meetings.past_cancel_button(old_booking_id)).to_have_count(0)

    with allure.step("Проверить освобождение исходного слота"):
        host_slots = SlotsPage(host["page"])
        host_slots.open()
        expect(host_slots.slot_by_id(slot_id)).to_have_attribute("data-slot-status", "free")

    with allure.step("Забронировать освобождённый слот третьим участником"):
        new_guest = user_factory("replacement")
        person = PersonPage(new_guest["page"])
        person.open(booked_meeting["person_id"])
        person.select_slot(booked_meeting["slot_date"], booked_meeting["slot_time"])
        expect(person.booking_slot_id).to_have_value(slot_id)
        success_message = person.confirm_booking_and_close()
        assert "Забронировано!" in success_message

    with allure.step("Проверить новый ID повторного бронирования"):
        new_guest_meetings = MeetingsPage(new_guest["page"])
        new_guest_meetings.open()
        new_meeting = new_guest_meetings.meeting_with(host["user"]["name"])
        expect(new_meeting).to_have_count(1)
        new_booking_id = new_meeting.get_attribute("data-booking-id")
        assert new_booking_id, "У повторного бронирования отсутствует ID"
        assert new_booking_id != old_booking_id, (
            "Повторное бронирование должно создать новую встречу"
        )

    with allure.step("Проверить новую встречу и сохранение старой отменённой записи"):
        host_meetings = MeetingsPage(host["page"])
        host_meetings.open()
        host_new_meeting = host_meetings.upcoming_by_id(new_booking_id)
        expect(host_meetings.cards).to_have_count(1)
        expect(host_new_meeting).to_contain_text(new_guest["user"]["name"])
        expect(host_meetings.past_by_id(old_booking_id)).to_contain_text("отменено")

        expected_date = format_slot_date(date.fromisoformat(booked_meeting["slot_date"]))
        for meeting in (new_meeting, host_new_meeting):
            expect(meeting).to_contain_text(expected_date)
            expect(meeting).to_contain_text(booked_meeting["slot_time"])

    with allure.step("Проверить повторный статус booked"):
        host_slots.open()
        expect(host_slots.slot_by_id(slot_id)).to_have_attribute("data-slot-status", "booked")


@pytest.mark.parametrize("cancelled_by", ["host", "guest"])
@pytest.mark.parametrize(
    "meeting_for_cancellation_deadline, can_cancel",
    [(60, False), (115, False), (125, True)],
    indirect=["meeting_for_cancellation_deadline"],
    ids=["one_hour_before", "below_two_hours", "above_two_hours"],
)
@allure.feature("Отмена бронирования")
@allure.title("Отмена соблюдает двухчасовое ограничение ({param_id})")
def test_cancellation_respects_two_hour_deadline(
    meeting_for_cancellation_deadline, cancelled_by, can_cancel
):
    with allure.step("Открыть подготовленную ближайшую встречу"):
        prepared = meeting_for_cancellation_deadline
        booking_id = prepared["booking_id"]
        canceller = prepared[cancelled_by]
        meetings = MeetingsPage(canceller["page"])
        meetings.open()
        expect(meetings.upcoming_by_id(booking_id)).to_be_visible()

    with allure.step("Проверить фактический остаток до начала встречи"):
        remaining = prepared["starts_at"] - now_in_moscow()
        assert remaining > timedelta(0), "Встреча должна быть в будущем"
        if can_cancel:
            assert remaining > timedelta(hours=2), "Подготовка пересекла границу отмены"
        else:
            assert remaining < timedelta(hours=2), (
                "Встреча должна начинаться менее чем через два часа"
            )

    with allure.step("Попытаться отменить встречу"):
        meetings.cancel_meeting(booking_id)

    with allure.step("Проверить результат отмены у обеих сторон"):
        for participant in (prepared["host"], prepared["guest"]):
            participant_meetings = MeetingsPage(participant["page"])
            participant_meetings.open()
            if can_cancel:
                expect(participant_meetings.past_by_id(booking_id)).to_contain_text("отменено")
                expect(participant_meetings.upcoming_by_id(booking_id)).to_have_count(0)
            else:
                expect(participant_meetings.upcoming_by_id(booking_id)).to_be_visible()
                expect(participant_meetings.past_by_id(booking_id)).to_have_count(0)

    with allure.step("Проверить соответствующий статус слота"):
        slots = SlotsPage(prepared["host"]["page"])
        slots.open()
        expect(slots.slot_by_id(prepared["slot_id"])).to_have_attribute(
            "data-slot-status", "free" if can_cancel else "booked"
        )
