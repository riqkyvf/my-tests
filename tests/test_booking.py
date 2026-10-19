import uuid
from datetime import date, timedelta

import allure
from playwright.sync_api import expect

from components.header import Header
from helpers.dates import format_slot_date, today_in_moscow
from pages.catalog_page import CatalogPage
from pages.meetings_page import MeetingsPage
from pages.person_page import PersonPage
from pages.profile_page import ProfilePage
from pages.slots_page import SlotsPage


@allure.feature("Бронирование")
@allure.title("Участник бронирует слот, и встреча видна обеим сторонам")
def test_guest_books_host_slot_and_both_see_meeting(user_factory):
    with allure.step("Подготовить ведущего и гостя"):
        host = user_factory("host")
        guest = user_factory("guest")

    with allure.step("Добавить ведущему навык для поиска в каталоге"):
        host_profile = ProfilePage(host["page"])

        host_skill_name = f"booking-{uuid.uuid4().hex} \"QA\" 'Python'"
        host_skill_type = "can_help"

        host_profile.open()

        host_profile.add_skill(host_skill_name, host_skill_type)

        expect(host_profile.can_help_skills).to_be_visible()

        saved_skill = host_profile.saved_skill(host_skill_name, host_skill_type)

        expect(saved_skill).to_be_visible()

    with allure.step("Создать и проверить свободный будущий слот"):
        host_slots = SlotsPage(host["page"])

        host_slots.open()

        slot_day = today_in_moscow() + timedelta(days=2)
        slot_date = slot_day.isoformat()
        slot_time = "23:50"
        expected_date = format_slot_date(slot_day)
        expected_datetime = f", {expected_date}, {slot_time}"

        host_slots.create_slot(slot_date, slot_time)

        expect(host_slots.slot_cards).to_have_count(1)
        expect(host_slots.slot_cards).to_have_attribute("data-slot-status", "free")
        expect(host_slots.slot_cards).to_contain_text(expected_datetime)

        slot_id = host_slots.slot_cards.get_attribute("data-slot-id")

        assert slot_id, "У созданного слота отсутствует ID"

    with allure.step("Открыть профиль ведущего из каталога гостя"):
        catalog_guest = CatalogPage(guest["page"])

        catalog_guest.open()

        host_card = catalog_guest.card_by_skill(host_skill_name)
        expect(host_card).to_have_count(1)
        expect(host_card).to_be_visible()
        host_card.click()

        person_page = PersonPage(guest["page"])
        creator_name = person_page.get_creator_name(host["user"]["name"])

        expect(creator_name).to_be_visible()

    with allure.step("Выбрать слот и подтвердить бронирование"):
        person_page.select_slot(slot_date, slot_time)

        expect(person_page.booking_dialog).to_be_visible()
        expect(person_page.booking_dialog).to_contain_text(expected_datetime)

        success_message = person_page.confirm_booking_and_close()
        assert "Забронировано!" in success_message

    with allure.step("Проверить дату и время встречи у гостя"):
        guest_meetings = MeetingsPage(guest["page"])
        host_meetings = MeetingsPage(host["page"])

        guest_meetings.open()
        guest_meeting = guest_meetings.meeting_with(host["user"]["name"])

        expect(guest_meeting).to_be_visible()
        expect(guest_meeting).to_have_count(1)
        expect(guest_meeting).to_contain_text(expected_date)
        expect(guest_meeting).to_contain_text(slot_time)

    with allure.step("Проверить встречу у ведущего и общий ID бронирования"):
        host_meetings.open()
        host_meeting = host_meetings.meeting_with(guest["user"]["name"])

        expect(host_meeting).to_be_visible()
        expect(host_meeting).to_have_count(1)
        expect(host_meeting).to_contain_text(expected_date)
        expect(host_meeting).to_contain_text(slot_time)

        booking_id = guest_meeting.get_attribute("data-booking-id")
        assert booking_id, "У созданной встречи отсутствует ID"
        expect(host_meeting).to_have_attribute("data-booking-id", booking_id)

    with allure.step("Проверить статус booked у исходного слота"):
        host_slots.open()

        booked_slot = host_slots.slot_by_id(slot_id)

        expect(booked_slot).to_be_visible()
        expect(booked_slot).to_have_attribute("data-slot-status", "booked")


@allure.feature("Бронирование")
@allure.title("Владелец не может забронировать собственный слот")
def test_owner_cannot_book_own_slot(catalog_page, catalog_candidate_with_slot):
    with allure.step("Найти публичный профиль владельца"):
        prepared = catalog_candidate_with_slot
        owner = prepared["person"]

        # Другой посетитель видит карточку и позволяет получить ID публичного профиля.
        catalog_page.open()
        owner_card = catalog_page.card_by_name(owner["user"]["name"])
        expect(owner_card).to_have_count(1)
        person_id = owner_card.get_attribute("data-person-id")
        assert person_id, "У карточки владельца отсутствует ID"

    with allure.step("Попытаться забронировать слот в контексте владельца"):
        person = PersonPage(owner["page"])
        person.open(person_id)
        expect(person.get_creator_name(owner["user"]["name"])).to_be_visible()
        person.select_slot(prepared["slot_date"], prepared["slot_time"])
        expect(person.booking_slot_id).to_have_value(prepared["slot_id"])
        person.confirm_booking()

    with allure.step("Проверить ошибку собственного слота"):
        expect(person.booking_error).to_have_text("Нельзя забронировать собственный слот")
        expect(person.booking_success).to_be_hidden()

    with allure.step("Проверить сохранение свободного слота"):
        slots = SlotsPage(owner["page"])
        slots.open()
        expect(slots.slot_cards).to_have_count(1)
        expect(slots.slot_by_id(prepared["slot_id"])).to_have_attribute("data-slot-status", "free")

    with allure.step("Проверить отсутствие созданной встречи"):
        meetings = MeetingsPage(owner["page"])
        meetings.open()
        expect(Header(owner["page"]).logout_button).to_be_visible()
        expect(meetings.cards).to_have_count(0)


@allure.feature("Бронирование")
@allure.title("Бронируется выбранный слот, остальные остаются свободными")
def test_booking_selected_slot_keeps_other_slots_free(
    person_with_multiple_free_slots, user_factory
):
    with allure.step("Открыть профиль участника с несколькими слотами"):
        prepared = person_with_multiple_free_slots
        host = prepared["person"]
        first_day_slot, second_day_early, selected = prepared["slots"]
        guest = user_factory("multi-booker")
        catalog = CatalogPage(guest["page"])
        catalog.open()
        catalog.card_by_name(host["user"]["name"]).click()
        person = PersonPage(guest["page"])

    with allure.step("Проверить переключение дней и доступные времена"):
        person.day_button(first_day_slot["date"]).click()
        expect(person.slot_button(first_day_slot["id"])).to_have_text(first_day_slot["time"])
        expect(person.slot_button(selected["id"])).to_have_count(0)
        person.day_button(selected["date"]).click()
        expect(person.slot_button(first_day_slot["id"])).to_have_count(0)
        expect(person.slot_button(second_day_early["id"])).to_have_text(second_day_early["time"])
        expect(person.slot_button(selected["id"])).to_have_text(selected["time"])

    with allure.step("Подтвердить бронирование выбранных даты и времени"):
        person.select_slot(selected["date"], selected["time"])
        expect(person.booking_slot_id).to_have_value(selected["id"])
        expected_date = format_slot_date(date.fromisoformat(selected["date"]))
        expect(person.booking_dialog).to_contain_text(f", {expected_date}, {selected['time']}")
        assert "Забронировано!" in person.confirm_booking_and_close()

    with allure.step("Проверить выбранную встречу у гостя"):
        guest_meetings = MeetingsPage(guest["page"])
        guest_meetings.open()
        expect(guest_meetings.cards).to_have_count(1)
        guest_meeting = guest_meetings.meeting_with(host["user"]["name"])
        expect(guest_meeting).to_have_count(1)
        expect(guest_meeting).to_contain_text(expected_date)
        expect(guest_meeting).to_contain_text(selected["time"])
        booking_id = guest_meeting.get_attribute("data-booking-id")
        assert booking_id, "У выбранного слота должна появиться встреча"

    with allure.step("Проверить ту же встречу у ведущего"):
        host_meetings = MeetingsPage(host["page"])
        host_meetings.open()
        expect(host_meetings.cards).to_have_count(1)
        host_meeting = host_meetings.upcoming_by_id(booking_id)
        expect(host_meeting).to_contain_text(guest["user"]["name"])
        expect(host_meeting).to_contain_text(expected_date)
        expect(host_meeting).to_contain_text(selected["time"])

    with allure.step("Проверить booked выбранного слота и free остальных"):
        slots = SlotsPage(host["page"])
        slots.open()
        expect(slots.slot_cards).to_have_count(3)
        expect(slots.slot_by_id(selected["id"])).to_have_attribute("data-slot-status", "booked")
        for other in (first_day_slot, second_day_early):
            expect(slots.slot_by_id(other["id"])).to_have_attribute("data-slot-status", "free")


@allure.feature("Бронирование")
@allure.title("Отказ от подтверждения не создаёт бронирование")
def test_dismissing_booking_confirmation_keeps_slot_free(catalog_candidate_with_slot, user_factory):
    with allure.step("Открыть профиль ведущего другим участником"):
        prepared = catalog_candidate_with_slot
        host = prepared["person"]
        guest = user_factory("dismiss-booker")
        catalog = CatalogPage(guest["page"])
        catalog.open()
        card = catalog.card_by_name(host["user"]["name"])
        expect(card).to_have_count(1)
        card.click()

    with allure.step("Открыть подтверждение выбранного слота"):
        person = PersonPage(guest["page"])
        person.select_slot(prepared["slot_date"], prepared["slot_time"])
        expect(person.booking_dialog).to_be_visible()
        expect(person.booking_slot_id).to_have_value(prepared["slot_id"])

    with allure.step("Отказаться от бронирования"):
        person.cancel_booking_confirmation()
        expect(person.booking_dialog).to_be_hidden()

    with allure.step("Проверить доступность слота после перезагрузки"):
        guest["page"].reload()
        person.day_button(prepared["slot_date"]).click()
        expect(person.slot_button(prepared["slot_id"])).to_have_text(prepared["slot_time"])

    with allure.step("Проверить свободный слот у ведущего"):
        slots = SlotsPage(host["page"])
        slots.open()
        expect(slots.slot_cards).to_have_count(1)
        expect(slots.slot_by_id(prepared["slot_id"])).to_have_attribute("data-slot-status", "free")

    with allure.step("Проверить отсутствие встреч у обеих сторон"):
        for participant in (host, guest):
            meetings = MeetingsPage(participant["page"])
            meetings.open()
            expect(Header(participant["page"]).logout_button).to_be_visible()
            expect(meetings.cards).to_have_count(0)
            expect(meetings.past_cards).to_have_count(0)
