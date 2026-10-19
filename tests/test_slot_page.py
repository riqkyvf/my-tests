from datetime import date, timedelta

import allure
import pytest
from playwright.sync_api import Page, expect

from helpers.dates import format_slot_date, now_in_moscow, today_in_moscow
from pages.catalog_page import CatalogPage
from pages.meetings_page import MeetingsPage
from pages.person_page import PersonPage
from pages.profile_page import ProfilePage
from pages.slots_page import SlotsPage


@allure.feature("Слоты")
@allure.title("Свободный будущий слот сохраняется после перезагрузки")
def test_user_can_create_slot(page: Page, logged_in_page, slots_page):
    with allure.step("Подготовить будущие дату и время слота"):
        slot_day = today_in_moscow() + timedelta(days=2)
        slot_date = slot_day.isoformat()
        slot_time = "23:50"
        expected_date = format_slot_date(slot_day)
        expected_datetime = f", {expected_date}, {slot_time}"

    with allure.step("Создать и проверить свободный слот"):
        slots_page.open()
        slots_page.create_slot(slot_date, slot_time)

        expect(slots_page.slot_cards).to_have_count(1)
        expect(slots_page.slot_cards).to_have_attribute("data-slot-status", "free")
        expect(slots_page.slot_cards).to_contain_text(expected_datetime)

    with allure.step("Перезагрузить страницу и проверить сохранённый слот"):
        page.reload()

        expect(slots_page.slot_cards).to_have_count(1)
        expect(slots_page.slot_cards).to_have_attribute("data-slot-status", "free")
        expect(slots_page.slot_cards).to_contain_text(expected_datetime)


@allure.feature("Слоты")
@allure.title("Удалённый свободный слот не появляется после перезагрузки")
def test_removed_free_slot_stays_absent_after_reload(page: Page, logged_in_page, slots_page):
    with allure.step("Создать и проверить свободный слот"):
        slot_date = (today_in_moscow() + timedelta(days=2)).isoformat()
        slots_page.open()
        slots_page.create_slot(slot_date, "23:50")

        expect(slots_page.slot_cards).to_have_count(1)
        expect(slots_page.slot_cards).to_have_attribute("data-slot-status", "free")

        slot_id = slots_page.slot_cards.get_attribute("data-slot-id")
        assert slot_id, "У созданного слота отсутствует ID"
        slot = slots_page.slot_by_id(slot_id)

    with allure.step("Удалить конкретный слот и проверить его отсутствие"):
        slots_page.remove_slot(slot_id)

        expect(slot).to_have_count(0)
        expect(slots_page.slot_cards).to_have_count(0)

    with allure.step("Перезагрузить страницу и проверить сохранение удаления"):
        page.reload()

        expect(slots_page.date_input).to_be_visible()
        expect(slot).to_have_count(0)
        expect(slots_page.slot_cards).to_have_count(0)


@pytest.mark.parametrize("browser_timezone", ["Europe/Kaliningrad", "Asia/Vladivostok"])
@allure.feature("Слоты")
@allure.title("Время слота зависит от пояса владельца, а не браузера зрителя ({browser_timezone})")
def test_slot_display_uses_owner_timezone_independently_of_browser(
    user_factory, slot_for_timezone_test, browser_timezone
):
    with allure.step("Открыть профиль владельца в другом часовом поясе браузера"):
        prepared_slot = slot_for_timezone_test
        owner = prepared_slot["owner"]
        slot_id = prepared_slot["slot_id"]
        original_day = date.fromisoformat(prepared_slot["slot_date"])
        viewer = user_factory("timezone-viewer", timezone_id=browser_timezone)

        catalog = CatalogPage(viewer["page"])
        catalog.open()
        owner_card = catalog.card_by_skill(prepared_slot["skill_name"])
        expect(owner_card).to_have_count(1)
        owner_card.click()

    with allure.step("Проверить исходное время в часовом поясе владельца"):
        person = PersonPage(viewer["page"])
        expect(person.slots_timezone).to_contain_text("Europe/Moscow")
        expect(person.day_button(original_day.isoformat())).to_be_visible()
        expect(person.slot_button(slot_id)).to_have_text("23:50")

    with allure.step("Изменить и сохранить часовой пояс владельца"):
        profile = ProfilePage(owner["page"])
        profile.open()
        profile.timezone_list.select_option(value="Asia/Irkutsk")
        profile.save()
        owner["page"].reload()
        expect(profile.timezone_list).to_have_value("Asia/Irkutsk")

    with allure.step("Проверить сдвиг времени и даты у владельца"):
        # Москва UTC+3, Иркутск UTC+8: 23:50 превращается в 04:50 следующего дня.
        expected_day = original_day + timedelta(days=1)
        expected_datetime = f", {format_slot_date(expected_day)}, 04:50"
        owner_slots = SlotsPage(owner["page"])
        owner_slots.open()
        expect(owner_slots.slot_by_id(slot_id)).to_contain_text(expected_datetime)

    with allure.step("Обновить публичный профиль и проверить то же время у зрителя"):
        viewer["page"].reload()
        expect(person.slots_timezone).to_contain_text("Asia/Irkutsk")
        expect(person.day_button(expected_day.isoformat())).to_be_visible()
        expect(person.day_button(original_day.isoformat())).to_have_count(0)
        expect(person.slot_button(slot_id)).to_have_text("04:50")


@allure.feature("Слоты")
@allure.title("Форма слотов запрещает прошедшую календарную дату")
def test_slot_calendar_rejects_past_dates(page: Page, logged_in_page, slots_page):
    with allure.step("Проверить минимальную дату и отсутствие слотов"):
        slots_page.open()
        today = today_in_moscow()
        past_date = (today - timedelta(days=1)).isoformat()
        expect(slots_page.date_input).to_have_attribute("min", today.isoformat())
        expect(slots_page.slot_cards).to_have_count(0)

    with allure.step("Попытаться создать слот на вчера"):
        # fill() позволяет ввести прошлую дату вручную; HTML-валидация должна её отклонить.
        slots_page.create_slot(past_date, "12:10")

    with allure.step("Проверить HTML-валидацию даты"):
        expect(slots_page.date_input).to_have_value(past_date)
        expect(slots_page.date_input.and_(page.locator(":invalid"))).to_have_count(1)
        expect(slots_page.date_input).to_be_focused()

    with allure.step("Перезагрузить страницу и проверить отсутствие слота"):
        page.reload()
        expect(slots_page.date_input).to_be_visible()
        expect(slots_page.slot_cards).to_have_count(0)


@allure.feature("Слоты")
@allure.title("Забронированный слот не имеет действия удаления")
def test_booked_slot_has_no_delete_action_and_stays_booked(booked_meeting):
    with allure.step("Открыть забронированный слот и проверить отсутствие кнопки удаления"):
        prepared = booked_meeting
        owner = prepared["host"]
        slots = SlotsPage(owner["page"])
        slots.open()
        slot = slots.slot_by_id(prepared["slot_id"])
        delete_button = slots.remove_button_for_slot(prepared["slot_id"])

        expect(slot).to_have_attribute("data-slot-status", "booked")
        expect(delete_button).to_have_count(0)

    with allure.step("Перезагрузить страницу и проверить сохранение booked"):
        owner["page"].reload()
        expect(slot).to_have_attribute("data-slot-status", "booked")
        expect(delete_button).to_have_count(0)

    with allure.step("Проверить сохранение встречи у обеих сторон"):
        for participant in (owner, prepared["guest"]):
            meetings = MeetingsPage(participant["page"])
            meetings.open()
            expect(meetings.upcoming_by_id(prepared["booking_id"])).to_be_visible()
            expect(meetings.past_by_id(prepared["booking_id"])).to_have_count(0)


@allure.feature("Слоты")
@allure.title("Прошедшее время сегодня не создаёт слот")
def test_slot_cannot_be_created_for_past_time_today(user_factory):
    with allure.step("Открыть слоты и выбрать уже прошедшее время по Москве"):
        owner = user_factory("past-time-today", timezone_id="Europe/Moscow")
        page = owner["page"]
        slots = SlotsPage(page)
        slots.open()
        # Часовой пояс нового профиля — Europe/Moscow (UTC+3), как и у браузера.
        now = now_in_moscow()
        if now.hour == 0 and now.minute == 0:
            pytest.skip("В первую минуту суток ещё нет прошедшего времени с точностью до минуты")
        today = now.date().isoformat()
        expect(slots.date_input).to_have_attribute("min", today)
        expect(slots.slot_cards).to_have_count(0)

    with allure.step("Отправить слот с прошедшим временем и проверить отказ"):
        slots.create_slot_and_wait(today, "00:00")
        expect(slots.slot_cards).to_have_count(0)

    with allure.step("Перезагрузить страницу и проверить отсутствие слота"):
        page.reload()
        expect(slots.date_input).to_be_visible()
        expect(slots.slot_cards).to_have_count(0)


@allure.feature("Слоты")
@allure.title("Удаление одного слота сохраняет остальные свободные слоты")
def test_removing_one_slot_keeps_other_free_slots(person_with_multiple_free_slots):
    with allure.step("Открыть три подготовленных свободных слота"):
        prepared = person_with_multiple_free_slots
        owner = prepared["person"]
        first, to_remove, last = prepared["slots"]
        slots = SlotsPage(owner["page"])
        slots.open()
        expect(slots.slot_cards).to_have_count(3)
        expect(slots.slot_by_id(to_remove["id"])).to_have_attribute("data-slot-status", "free")

    with allure.step("Удалить выбранный слот и проверить остальные"):
        slots.remove_slot(to_remove["id"])
        expect(slots.slot_by_id(to_remove["id"])).to_have_count(0)
        expect(slots.slot_cards).to_have_count(2)
        for remaining in (first, last):
            expect(slots.slot_by_id(remaining["id"])).to_have_attribute("data-slot-status", "free")

    with allure.step("Проверить ID, даты и время оставшихся слотов после перезагрузки"):
        owner["page"].reload()
        expect(slots.date_input).to_be_visible()
        expect(slots.slot_cards).to_have_count(2)
        expect(slots.slot_by_id(to_remove["id"])).to_have_count(0)
        for remaining in (first, last):
            card = slots.slot_by_id(remaining["id"])
            expect(card).to_have_attribute("data-slot-status", "free")
            expected_date = format_slot_date(date.fromisoformat(remaining["date"]))
            expect(card).to_contain_text(f", {expected_date}, {remaining['time']}")
