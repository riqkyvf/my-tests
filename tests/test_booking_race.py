import allure
from playwright.sync_api import expect

from components.header import Header
from config import BASE_URL
from pages.catalog_page import CatalogPage
from pages.meetings_page import MeetingsPage
from pages.person_page import PersonPage
from pages.slots_page import SlotsPage


@allure.feature("Бронирование")
@allure.title("В гонке за один слот создаётся ровно одна бронь")
def test_two_users_compete_for_one_slot_and_only_one_booking_is_created(
    booking_race_participants, confirm_bookings_together
):
    with allure.step("Открыть подтверждение одного слота у двух гостей"):
        prepared = booking_race_participants["slot"]
        host = prepared["person"]
        guests = booking_race_participants["guests"]
        persons = []

        for guest in guests:
            catalog = CatalogPage(guest["page"])
            catalog.open()
            catalog.card_by_name(host["user"]["name"]).click()
            person = PersonPage(guest["page"])
            person.select_slot(prepared["slot_date"], prepared["slot_time"])
            expect(person.booking_slot_id).to_have_value(prepared["slot_id"])
            persons.append(person)

    with allure.step("Отправить оба подтверждения без ожидания первого результата"):
        confirm_bookings_together(persons)

    with allure.step("Проверить единственного победителя и ошибку проигравшего"):
        for person in persons:
            expect(person.booking_success.or_(person.booking_error)).to_be_visible()

        successful = [person.booking_success.is_visible() for person in persons]
        assert sum(successful) == 1, "Ровно один участник должен получить подтверждение брони"
        winner_index = successful.index(True)
        loser_index = successful.index(False)
        expect(persons[winner_index].booking_success).to_contain_text("Забронировано!")
        expect(persons[loser_index].booking_error).to_have_text(
            "Этот слот только что забронировали — выбери другой"
        )
        expect(persons[loser_index].booking_success).to_be_hidden()

    with allure.step("Проверить встречу у победителя"):
        winner = guests[winner_index]
        loser = guests[loser_index]
        winner_meetings = MeetingsPage(winner["page"])
        winner_meetings.open()
        expect(winner_meetings.cards).to_have_count(1)
        winner_meeting = winner_meetings.meeting_with(host["user"]["name"])
        expect(winner_meeting).to_have_count(1)
        booking_id = winner_meeting.get_attribute("data-booking-id")
        assert booking_id, "У победителя отсутствует ID бронирования"

    with allure.step("Проверить отсутствие встречи у проигравшего"):
        loser_meetings = MeetingsPage(loser["page"])
        loser_meetings.open()
        expect(loser["page"]).to_have_url(f"{BASE_URL}/pomidorqa/bookings")
        expect(Header(loser["page"]).logout_button).to_be_visible()
        expect(loser_meetings.cards).to_have_count(0)

    with allure.step("Проверить единственную встречу у ведущего"):
        host_meetings = MeetingsPage(host["page"])
        host_meetings.open()
        expect(host_meetings.cards).to_have_count(1)
        host_meeting = host_meetings.upcoming_by_id(booking_id)
        expect(host_meeting).to_contain_text(winner["user"]["name"])

    with allure.step("Проверить статус booked у спорного слота"):
        slots = SlotsPage(host["page"])
        slots.open()
        expect(slots.slot_by_id(prepared["slot_id"])).to_have_attribute(
            "data-slot-status", "booked"
        )
