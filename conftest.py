import uuid
from datetime import date, timedelta

import pytest
from playwright.sync_api import expect

from api.accounts import create_account, delete_account
from components.header import Header
from config import BASE_URL, DEFAULT_PROFILE_TIMEZONE, REQUEST_TIMEOUT_MS
from helpers.dates import MOSCOW_TIMEZONE, format_slot_date, now_in_moscow, today_in_moscow
from helpers.users import make_user_data
from pages.catalog_page import CatalogPage
from pages.login_page import LoginPage
from pages.meetings_page import MeetingsPage
from pages.person_page import PersonPage
from pages.profile_page import ProfilePage
from pages.register_page import RegisterPage
from pages.slots_page import SlotsPage


@pytest.fixture
def new_context(new_context):
    def create_context(**context_options):
        context_options.setdefault("timezone_id", DEFAULT_PROFILE_TIMEZONE)
        return new_context(**context_options)

    return create_context


@pytest.fixture
def api_context(playwright):
    api = playwright.request.new_context()

    try:
        yield api
    finally:
        api.dispose()


@pytest.fixture
def created_account(api_context):
    user = make_user_data()
    created = False

    try:
        response = create_account(api_context, user)
        created = response.status == 201
        assert created, f"Создание аккаунта: HTTP {response.status}. {response.text()}"

        yield {
            "api_context": api_context,
            "user": user,
        }
    finally:
        if created or any(
            cookie["name"] == "pomidorqa_session"
            for cookie in api_context.storage_state()["cookies"]
        ):
            response = delete_account(api_context)
            assert response.status == 200, (
                f"Удаление аккаунта: HTTP {response.status}. {response.text()}"
            )


@pytest.fixture
def registration_user(page):
    user = make_user_data("ui-signup")
    try:
        yield user
    finally:
        # Аккаунт создаёт UI-тест. Удаляем его и при падении проверки после регистрации.
        # При HTML-валидации сессия не появляется и удалять ещё нечего.
        if any(cookie["name"] == "pomidorqa_session" for cookie in page.context.cookies()):
            response = delete_account(page.context.request)
            assert response.status == 200, (
                f"Удаление UI-аккаунта: HTTP {response.status}. {response.text()}"
            )


@pytest.fixture
def register_page(page):
    return RegisterPage(page)


@pytest.fixture
def user_factory(new_context):
    account_attempts = []

    def create_user(role, **context_options):
        user = make_user_data(role)
        context = new_context(**context_options)
        # Учитываем попытку до запроса: сессия может появиться и при неожиданном ответе.
        account = {"context": context, "created": False}
        account_attempts.append(account)

        response = create_account(context.request, user)
        account["created"] = response.status == 201

        assert account["created"], (
            f"Создание пользователя {user['email']}: HTTP {response.status}. {response.text()}"
        )

        page = context.new_page()

        return {
            "user": user,
            "context": context,
            "page": page,
        }

    try:
        yield create_user
    finally:
        errors = []

        for account in account_attempts:
            context = account["context"]
            try:
                if not account["created"] and not any(
                    cookie["name"] == "pomidorqa_session" for cookie in context.cookies()
                ):
                    continue
                response = delete_account(context.request)

                assert response.status == 200, (
                    f"Удаление пользователя: HTTP {response.status}. {response.text()}"
                )
            except Exception as error:
                errors.append(str(error))

        if errors:
            pytest.fail("Ошибки уборки:\n" + "\n".join(errors))


@pytest.fixture
def available_person_factory(user_factory):
    def create_person(
        role,
        skills,
        *,
        profile_data=None,
        slot_date=None,
        slot_time="23:50",
        **context_options,
    ):
        person = user_factory(role, **context_options)
        profile = ProfilePage(person["page"])
        profile.open()

        if profile_data is not None:
            profile.fill_text_data(
                profile_data["name"], profile_data["telegram"], profile_data["bio"]
            )
            profile.save()
            person["page"].reload()
            expect(profile.name_input).to_have_value(profile_data["name"])
            expect(profile.telegram_input).to_have_value(profile_data["telegram"])
            expect(profile.about_info_input).to_have_value(profile_data["bio"])

        for skill_type, skill_name in skills:
            profile.add_skill(skill_name, skill_type)
            expect(profile.saved_skill(skill_name, skill_type)).to_be_visible()

        if slot_date is None:
            slot_date = (today_in_moscow() + timedelta(days=2)).isoformat()
        slots = SlotsPage(person["page"])
        slots.open()
        expect(slots.date_input).to_be_visible()
        expect(slots.slot_cards).to_have_count(0)
        slots.create_slot(slot_date, slot_time)
        expect(slots.slot_cards).to_have_count(1)
        expect(slots.slot_cards).to_have_attribute("data-slot-status", "free")
        expect(slots.slot_cards).to_contain_text(slot_time)
        slot_id = slots.slot_cards.get_attribute("data-slot-id")
        assert slot_id, "У подготовленного слота отсутствует ID"

        return {
            "person": person,
            "slot_id": slot_id,
            "slot_date": slot_date,
            "slot_time": slot_time,
        }

    return create_person


@pytest.fixture
def searchable_people(available_person_factory):
    unique_id = uuid.uuid4().hex
    skill_name = f"search-{unique_id}"
    matching = available_person_factory(f"search-match-{unique_id[:8]}", [("can_help", skill_name)])
    other = available_person_factory(
        f"search-other-{unique_id[:8]}",
        [("can_help", f"other-{unique_id}"), ("want_to_learn", skill_name)],
    )
    return {
        "skill_name": skill_name,
        "matching_name": matching["person"]["user"]["name"],
        "other_name": other["person"]["user"]["name"],
    }


@pytest.fixture
def catalog_page(page):
    return CatalogPage(page)


@pytest.fixture
def login_page(page):
    return LoginPage(page)


@pytest.fixture
def header(page):
    return Header(page)


@pytest.fixture
def profile_page(page):
    return ProfilePage(page)


@pytest.fixture
def slots_page(page):
    return SlotsPage(page)


@pytest.fixture
def logged_in_page(page, created_account, header):
    api = created_account["api_context"]
    cookies = api.storage_state()["cookies"]
    page.context.add_cookies(cookies)

    page.goto(f"{BASE_URL}/pomidorqa")
    expect(header.logout_button).to_be_visible()

    return page


@pytest.fixture
def published_profile(available_person_factory):
    unique_id = uuid.uuid4().hex[:8]
    profile_data = {
        "name": f"QA Profile {unique_id}",
        "telegram": f"@qa_{unique_id}",
        "bio": f"Помогаю с автоматизацией тестирования — {unique_id}",
    }
    skills = {"can_help": 'Python "advanced"', "want_to_learn": "SQL"}
    prepared = available_person_factory(
        "profile-owner", list(skills.items()), profile_data=profile_data
    )
    return {"data": profile_data, "skills": skills, "person": prepared["person"]}


@pytest.fixture
def booked_slot_factory(available_person_factory, user_factory):
    def create_booked_slot(*, starts_at=None, guest=None):
        skill_name = f"cancel-{uuid.uuid4().hex}"
        slot_options = {}
        if starts_at is not None:
            assert starts_at.tzinfo is not None, "Дата начала должна содержать часовой пояс"
            starts_at = starts_at.astimezone(MOSCOW_TIMEZONE).replace(second=0, microsecond=0)
            slot_options = {
                "slot_date": starts_at.date().isoformat(),
                "slot_time": starts_at.strftime("%H:%M"),
            }
        prepared = available_person_factory(
            "cancel-host", [("can_help", skill_name)], **slot_options
        )
        host = prepared["person"]
        if guest is None:
            guest = user_factory("cancel-guest")

        catalog = CatalogPage(guest["page"])
        catalog.open()
        host_card = catalog.card_by_skill(skill_name)
        expect(host_card).to_have_count(1)
        person_id = host_card.get_attribute("data-person-id")
        assert person_id, "У карточки участника отсутствует ID"
        catalog.open_person(host_card)

        person = PersonPage(guest["page"])
        person.select_slot(prepared["slot_date"], prepared["slot_time"])
        expect(person.booking_slot_id).to_have_value(prepared["slot_id"])
        success_message = person.confirm_booking_and_close()
        assert "Забронировано!" in success_message

        return {
            "host": host,
            "guest": guest,
            "person_id": person_id,
            "slot_id": prepared["slot_id"],
            "slot_date": prepared["slot_date"],
            "slot_time": prepared["slot_time"],
            "starts_at": starts_at,
        }

    return create_booked_slot


@pytest.fixture
def booked_slot(booked_slot_factory):
    return booked_slot_factory()


@pytest.fixture
def booked_meeting_factory(booked_slot_factory):
    def create_meeting(*, starts_at=None, guest=None):
        prepared = booked_slot_factory(starts_at=starts_at, guest=guest)
        host = prepared["host"]
        guest = prepared["guest"]

        meetings = MeetingsPage(guest["page"])
        meetings.open()
        meeting = meetings.meeting_with(host["user"]["name"])
        expect(meeting).to_have_count(1)
        booking_id = meeting.get_attribute("data-booking-id")
        assert booking_id, "У подготовленной встречи отсутствует ID"

        slots = SlotsPage(host["page"])
        slots.open()
        expect(slots.slot_by_id(prepared["slot_id"])).to_have_attribute(
            "data-slot-status", "booked"
        )
        return {**prepared, "booking_id": booking_id}

    return create_meeting


@pytest.fixture
def booked_meeting(booked_meeting_factory):
    return booked_meeting_factory()


@pytest.fixture
def meetings_in_both_roles(booked_meeting_factory):
    as_host = booked_meeting_factory()
    participant = as_host["host"]
    as_guest = booked_meeting_factory(
        guest=participant, starts_at=now_in_moscow() + timedelta(days=3)
    )
    return {"participant": participant, "as_host": as_host, "as_guest": as_guest}


@pytest.fixture
def mixed_meetings(booked_meeting_factory):
    groups = []
    for _ in range(2):
        prepared = booked_meeting_factory()
        host = prepared["host"]
        guest = prepared["guest"]
        meetings = MeetingsPage(guest["page"])
        meetings.open()
        meetings.cancel_meeting(prepared["booking_id"])
        expect(meetings.past_by_id(prepared["booking_id"])).to_contain_text("отменено")

        # Повторная бронь создаёт новую ближайшую встречу у той же пары участников.
        person = PersonPage(guest["page"])
        person.open(prepared["person_id"])
        person.select_slot(prepared["slot_date"], prepared["slot_time"])
        expect(person.booking_slot_id).to_have_value(prepared["slot_id"])
        assert "Забронировано!" in person.confirm_booking_and_close()
        meetings.open()
        meeting = meetings.meeting_with(host["user"]["name"])
        expect(meeting).to_have_count(1)
        upcoming_id = meeting.get_attribute("data-booking-id")
        assert upcoming_id, "У повторной встречи отсутствует ID"
        assert upcoming_id != prepared["booking_id"], "Повторная бронь должна иметь новый ID"
        groups.append(
            {
                "host": host,
                "guest": guest,
                "upcoming_id": upcoming_id,
                "cancelled_id": prepared["booking_id"],
            }
        )
    return groups


@pytest.fixture
def meeting_for_cancellation_deadline(request, booked_meeting_factory):
    starts_at = now_in_moscow() + timedelta(minutes=request.param)
    return booked_meeting_factory(starts_at=starts_at)


@pytest.fixture
def catalog_candidate(user_factory):
    unique_id = uuid.uuid4().hex[:8]
    participant = user_factory(f"candidate-{unique_id}")
    skill_name = f"catalog-{unique_id}"
    profile = ProfilePage(participant["page"])
    profile.open()
    profile.add_skill(skill_name, "can_help")
    expect(profile.saved_skill(skill_name, "can_help")).to_be_visible()
    return participant


@pytest.fixture
def catalog_control(available_person_factory):
    unique_id = uuid.uuid4().hex[:8]
    prepared = available_person_factory(
        f"control-{unique_id}", [("can_help", f"catalog-control-{unique_id}")]
    )
    return prepared["person"]


@pytest.fixture
def slot_for_timezone_test(available_person_factory):
    skill_name = f"timezone-{uuid.uuid4().hex}"
    prepared = available_person_factory(
        "timezone-owner", [("can_help", skill_name)], timezone_id="Europe/Moscow"
    )
    return {
        "owner": prepared["person"],
        "skill_name": skill_name,
        "slot_date": prepared["slot_date"],
        "slot_id": prepared["slot_id"],
    }


@pytest.fixture
def catalog_candidate_with_slot(available_person_factory):
    unique_id = uuid.uuid4().hex[:8]
    return available_person_factory(
        f"candidate-{unique_id}", [("can_help", f"catalog-{unique_id}")]
    )


@pytest.fixture
def public_profile_with_booked_slot(request, booked_slot):
    host = booked_slot["host"]
    slots = SlotsPage(host["page"])
    slots.open()
    same_day = getattr(request, "param", "different_days") == "same_day"
    free_day = date.fromisoformat(booked_slot["slot_date"])
    if not same_day:
        free_day += timedelta(days=1)
    free_date = free_day.isoformat()
    free_time = "12:10"
    slots.create_slot(free_date, free_time)
    expect(slots.slot_cards).to_have_count(2)
    expect(slots.free_slot_cards).to_have_count(1)
    expect(slots.free_slot_cards).to_contain_text(free_time)
    expect(slots.slot_by_id(booked_slot["slot_id"])).to_have_attribute("data-slot-status", "booked")
    free_id = slots.free_slot_cards.get_attribute("data-slot-id")
    assert free_id, "У контрольного свободного слота отсутствует ID"
    return {
        "host": host,
        "person_id": booked_slot["person_id"],
        "booked_slot_id": booked_slot["slot_id"],
        "booked_slot_date": booked_slot["slot_date"],
        "free_slot_id": free_id,
        "free_slot_date": free_date,
        "free_slot_time": free_time,
    }


@pytest.fixture
def booking_race_participants(catalog_candidate_with_slot, user_factory):
    return {
        "slot": catalog_candidate_with_slot,
        "guests": [user_factory("race-first"), user_factory("race-second")],
    }


@pytest.fixture
def confirm_bookings_together():
    def confirm(person_pages):
        pending_routes = []
        registered_routes = []

        def hold_booking_request(route):
            if route.request.method == "POST":
                pending_routes.append(route)
            else:
                route.continue_()

        try:
            for person in person_pages:
                url = person.page.url
                person.page.route(url, hold_booking_request)
                registered_routes.append((person.page, url))

            for person in person_pages:
                url = person.page.url
                with person.page.expect_request(
                    lambda request, target=url: request.url == target and request.method == "POST",
                    timeout=REQUEST_TIMEOUT_MS,
                ):
                    person.confirm_booking()
                expect(person.booking_submit_button).to_be_disabled()

            assert len(pending_routes) == len(person_pages), (
                "Не все участники отправили запрос бронирования"
            )
            while pending_routes:
                route = pending_routes.pop(0)
                route.continue_()
        finally:
            for route in pending_routes:
                route.abort()
            for page, url in registered_routes:
                page.unroute(url, hold_booking_request)

    return confirm


@pytest.fixture
def person_with_multiple_free_slots(available_person_factory):
    unique_id = uuid.uuid4().hex[:8]
    first_day = today_in_moscow() + timedelta(days=2)
    second_day = first_day + timedelta(days=1)
    planned = [
        (first_day.isoformat(), "10:00"),
        (second_day.isoformat(), "10:00"),
        (second_day.isoformat(), "15:00"),
    ]
    prepared = available_person_factory(
        f"multi-{unique_id}",
        [("can_help", f"multi-slots-{unique_id}")],
        slot_date=planned[0][0],
        slot_time=planned[0][1],
    )
    person = prepared["person"]
    slots = SlotsPage(person["page"])
    slots.open()
    created = [{"id": prepared["slot_id"], "date": planned[0][0], "time": planned[0][1]}]

    for slot_date, slot_time in planned[1:]:
        previous_ids = set(slots.slot_ids())
        slots.create_slot(slot_date, slot_time)
        expect(slots.slot_cards).to_have_count(len(created) + 1)
        new_ids = set(slots.slot_ids()) - previous_ids
        assert len(new_ids) == 1, "Должен появиться ровно один новый слот"
        slot_id = next(iter(new_ids))
        expect(slots.slot_by_id(slot_id)).to_have_attribute("data-slot-status", "free")
        expected_date = format_slot_date(date.fromisoformat(slot_date))
        expect(slots.slot_by_id(slot_id)).to_contain_text(f", {expected_date}, {slot_time}")
        created.append({"id": slot_id, "date": slot_date, "time": slot_time})

    return {"person": person, "slots": created}


@pytest.fixture(
    params=[
        (ProfilePage, "/pomidorqa/profile", "name_input"),
        (SlotsPage, "/pomidorqa/profile/slots", "date_input"),
        (MeetingsPage, "/pomidorqa/bookings", "upcoming"),
    ],
    ids=["profile", "slots", "meetings"],
)
def protected_page(request, page):
    page_class, path, content_attribute = request.param
    view = page_class(page)
    return view, f"{BASE_URL}{path}", getattr(view, content_attribute)
