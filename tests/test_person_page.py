from datetime import date

import allure
import pytest
from playwright.sync_api import expect

from helpers.dates import format_slot_date
from pages.person_page import PersonPage
from pages.slots_page import SlotsPage


@allure.feature("Публичный профиль")
@allure.title("Гость видит публичный слот, но для бронирования нужен вход")
def test_anonymous_guest_sees_public_slot_but_must_log_in_to_book(
    page, header, catalog_page, catalog_candidate_with_slot
):
    with allure.step("Открыть публичный профиль без авторизации"):
        prepared = catalog_candidate_with_slot
        owner = prepared["person"]
        slot_id = prepared["slot_id"]

        catalog_page.open()
        expect(header.login_link).to_be_visible()
        expect(header.logout_button).to_be_hidden()
        catalog_page.open_person(catalog_page.card_by_name(owner["user"]["name"]))

    with allure.step("Проверить владельца и свободный слот"):
        person = PersonPage(page)
        expect(person.get_creator_name(owner["user"]["name"])).to_be_visible()
        expect(person.day_button(prepared["slot_date"])).to_be_visible()
        expect(person.slot_button(slot_id)).to_have_text(prepared["slot_time"])

    with allure.step("Попытаться подтвердить бронирование гостем"):
        person.select_slot(prepared["slot_date"], prepared["slot_time"])
        expected_date = format_slot_date(date.fromisoformat(prepared["slot_date"]))
        expect(person.booking_dialog).to_contain_text(f", {expected_date}, {prepared['slot_time']}")
        expect(person.booking_slot_id).to_have_value(slot_id)
        person.confirm_booking()

    with allure.step("Проверить требование входа"):
        expect(person.booking_error).to_have_text("Нужно войти в аккаунт PomidorQA")
        expect(person.booking_success).to_be_hidden()
        expect(header.login_link).to_be_visible()

    with allure.step("Проверить сохранение статуса free у владельца"):
        owner_slots = SlotsPage(owner["page"])
        owner_slots.open()
        expect(owner_slots.slot_by_id(slot_id)).to_have_attribute("data-slot-status", "free")


@pytest.mark.parametrize(
    "public_profile_with_booked_slot",
    ["different_days", "same_day"],
    indirect=True,
    ids=["different_days", "same_day"],
)
@allure.feature("Публичный профиль")
@allure.title("Публичный профиль показывает свободный и скрывает занятый слот ({param_id})")
def test_public_profile_hides_booked_slot_but_shows_free_slot(
    page, public_profile_with_booked_slot
):
    with allure.step("Открыть публичный профиль с обоими типами слотов"):
        prepared = public_profile_with_booked_slot
        person = PersonPage(page)
        person.open(prepared["person_id"])

    with allure.step("Проверить доступность свободного слота"):
        expect(person.get_creator_name(prepared["host"]["user"]["name"])).to_be_visible()
        expect(person.day_button(prepared["free_slot_date"])).to_be_visible()
        expect(person.slot_button(prepared["free_slot_id"])).to_have_text(
            prepared["free_slot_time"]
        )

    with allure.step("Проверить отсутствие занятого времени и дня без свободных слотов"):
        if prepared["booked_slot_date"] != prepared["free_slot_date"]:
            expect(person.day_button(prepared["booked_slot_date"])).to_have_count(0)
        expect(person.slot_button(prepared["booked_slot_id"])).to_have_count(0)
