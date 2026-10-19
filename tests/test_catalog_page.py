import uuid
from urllib.parse import urlencode

import allure
import pytest
from playwright.sync_api import Page, expect

from config import BASE_URL
from pages.catalog_page import CatalogPage
from pages.person_page import PersonPage
from pages.profile_page import ProfilePage
from pages.slots_page import SlotsPage


@allure.feature("Каталог участников")
@allure.title("Поиск находит can_help и исключает совпадение только в want_to_learn")
def test_catalog_search_finds_people_by_can_help_skill(page: Page, catalog_page, searchable_people):
    with allure.step("Проверить наличие обоих участников в общем каталоге"):
        catalog_page.open()

        matching_card = catalog_page.card_by_name(searchable_people["matching_name"])
        other_card = catalog_page.card_by_name(searchable_people["other_name"])
        expect(matching_card).to_be_visible()
        expect(other_card).to_be_visible()

    with allure.step("Выполнить поиск по общему навыку"):
        skill_name = searchable_people["skill_name"]
        catalog_page.search_by_skill(skill_name)

    with allure.step("Проверить запрос и единственную подходящую карточку"):
        query = urlencode({"skill": skill_name})
        expect(page).to_have_url(f"{BASE_URL}/pomidorqa?{query}")
        expect(catalog_page.cards).to_have_count(1)
        expect(matching_card).to_be_visible()
        expect(other_card).to_have_count(0)


@allure.feature("Каталог участников")
@allure.title("Участник виден другому посетителю и скрыт от себя в каталоге")
def test_catalog_excludes_current_user(catalog_page, catalog_candidate_with_slot, catalog_control):
    with allure.step("Проверить карточки участника и контрольного пользователя"):
        participant = catalog_candidate_with_slot["person"]
        catalog_page.open()
        expect(catalog_page.card_by_name(participant["user"]["name"])).to_be_visible()
        expect(catalog_page.card_by_name(catalog_control["user"]["name"])).to_be_visible()

    with allure.step("Проверить каталог в контексте самого участника"):
        own_catalog = CatalogPage(participant["page"])
        own_catalog.open()
        expect(own_catalog.card_by_name(catalog_control["user"]["name"])).to_be_visible()
        expect(own_catalog.card_by_name(participant["user"]["name"])).to_have_count(0)


@allure.feature("Каталог участников")
@allure.title("Участник без слотов скрыт из каталога")
def test_catalog_excludes_user_without_slots(catalog_page, catalog_candidate, catalog_control):
    with allure.step("Проверить отсутствие слотов у участника"):
        slots = SlotsPage(catalog_candidate["page"])
        slots.open()
        expect(slots.date_input).to_be_visible()
        expect(slots.slot_cards).to_have_count(0)

    with allure.step("Проверить скрытую карточку и видимого контрольного участника"):
        catalog_page.open()
        expect(catalog_page.card_by_name(catalog_control["user"]["name"])).to_be_visible()
        expect(catalog_page.card_by_name(catalog_candidate["user"]["name"])).to_have_count(0)


@allure.feature("Каталог участников")
@allure.title("Удаление последнего свободного слота скрывает участника")
def test_catalog_excludes_user_after_last_free_slot_is_removed(
    catalog_page, catalog_candidate_with_slot, catalog_control
):
    with allure.step("Проверить исходную видимость участника со слотом"):
        prepared = catalog_candidate_with_slot
        participant = prepared["person"]
        slots = SlotsPage(participant["page"])
        slots.open()

        catalog_page.open()
        participant_card = catalog_page.card_by_name(participant["user"]["name"])
        expect(participant_card).to_be_visible()

    with allure.step("Удалить последний свободный слот"):
        slots.remove_slot(prepared["slot_id"])
        expect(slots.slot_cards).to_have_count(0)

    with allure.step("Проверить отсутствие участника после обновления каталога"):
        catalog_page.open()
        expect(catalog_page.card_by_name(catalog_control["user"]["name"])).to_be_visible()
        expect(participant_card).to_have_count(0)


@allure.feature("Каталог участников")
@allure.title("Участник только с забронированными слотами скрыт из каталога")
def test_catalog_excludes_user_with_only_booked_slots(
    catalog_page, booked_meeting, catalog_control
):
    with allure.step("Проверить единственный забронированный слот"):
        slots = SlotsPage(booked_meeting["host"]["page"])
        slots.open()
        expect(slots.slot_cards).to_have_count(1)
        expect(slots.slot_by_id(booked_meeting["slot_id"])).to_have_attribute(
            "data-slot-status", "booked"
        )

    with allure.step("Проверить отсутствие карточки при наличии контрольной"):
        catalog_page.open()
        expect(catalog_page.card_by_name(catalog_control["user"]["name"])).to_be_visible()
        expect(catalog_page.card_by_id(booked_meeting["person_id"])).to_have_count(0)


@allure.feature("Каталог участников")
@allure.title("Свободный слот сохраняет участника в каталоге при наличии занятого")
def test_catalog_keeps_user_with_both_free_and_booked_slots(
    catalog_page, public_profile_with_booked_slot
):
    with allure.step("Проверить свободный и забронированный слоты владельца"):
        prepared = public_profile_with_booked_slot
        slots = SlotsPage(prepared["host"]["page"])
        slots.open()
        expect(slots.slot_by_id(prepared["booked_slot_id"])).to_have_attribute(
            "data-slot-status", "booked"
        )
        expect(slots.slot_by_id(prepared["free_slot_id"])).to_have_attribute(
            "data-slot-status", "free"
        )

    with allure.step("Проверить видимость владельца в каталоге"):
        catalog_page.open()
        card = catalog_page.card_by_id(prepared["person_id"])
        expect(card).to_have_count(1)
        expect(card).to_be_visible()


@pytest.mark.parametrize("skill_type", ["can_help", "want_to_learn"])
@allure.feature("Каталог участников")
@allure.title("Изменение навыка отражается в публичном профиле и поиске ({skill_type})")
def test_skill_updates_are_visible_in_public_profile_and_search(
    user_factory, available_person_factory, skill_type
):
    with allure.step("Открыть опубликованный профиль с исходными навыками"):
        unique_id = uuid.uuid4().hex
        initial_skills = {
            "can_help": f"baseline-help-{unique_id}",
            "want_to_learn": f"baseline-learn-{unique_id}",
        }
        prepared = available_person_factory("skill-owner", list(initial_skills.items()))
        owner = prepared["person"]
        viewer = user_factory("skill-reader")
        catalog = CatalogPage(viewer["page"])
        catalog.open()
        card = catalog.card_by_skill(initial_skills["can_help"])
        expect(card).to_have_count(1)
        person_id = card.get_attribute("data-person-id")
        assert person_id, "У опубликованного профиля отсутствует ID"
        card.click()

        person = PersonPage(viewer["page"])
        for initial_type, initial_name in initial_skills.items():
            expect(person.skill_tag(initial_name, initial_type)).to_be_visible()
        skill_name = f'updated-{unique_id} "QA"'
        expect(person.skill_tag(skill_name, skill_type)).to_have_count(0)

    with allure.step("Добавить владельцу новый навык"):
        profile = ProfilePage(owner["page"])
        profile.open()
        profile.add_skill(skill_name, skill_type)
        expect(profile.saved_skill(skill_name, skill_type)).to_be_visible()

    with allure.step("Проверить новый навык после обновления публичного профиля"):
        viewer["page"].reload()
        expect(person.skill_tag(skill_name, skill_type)).to_be_visible()

    with allure.step("Проверить поиск с учётом типа добавленного навыка"):
        catalog.open()
        catalog.search_by_skill(skill_name)
        search_url = f"{BASE_URL}/pomidorqa?{urlencode({'skill': skill_name})}"
        expect(viewer["page"]).to_have_url(search_url)
        expect(catalog.skill_input).to_have_value(skill_name)
        # В поиске участвуют только навыки «могу помочь».
        expected_matches = 1 if skill_type == "can_help" else 0
        expect(catalog.cards).to_have_count(expected_matches)
        expect(catalog.card_by_id(person_id)).to_have_count(expected_matches)
        if skill_type == "can_help":
            expect(catalog.card_by_skill(skill_name)).to_be_visible()

    with allure.step("Удалить навык и проверить сохранение удаления"):
        profile.remove_skill(skill_name, skill_type)
        expect(profile.saved_skill(skill_name, skill_type)).to_have_count(0)
        owner["page"].reload()
        expect(profile.saved_skill(skill_name, skill_type)).to_have_count(0)

    with allure.step("Проверить удаление в публичном профиле и сохранение других навыков"):
        person.open(person_id)
        expect(person.get_creator_name(owner["user"]["name"])).to_be_visible()
        expect(person.skill_tag(skill_name, skill_type)).to_have_count(0)
        for initial_type, initial_name in initial_skills.items():
            expect(person.skill_tag(initial_name, initial_type)).to_be_visible()

    with allure.step("Проверить отсутствие удалённого навыка в поиске"):
        catalog.open()
        catalog.search_by_skill(skill_name)
        expect(viewer["page"]).to_have_url(search_url)
        expect(catalog.skill_input).to_have_value(skill_name)
        expect(catalog.cards).to_have_count(0)

    with allure.step("Проверить доступность владельца по оставшемуся навыку"):
        # Владелец остаётся в каталоге: удалён только навык, свободный слот сохранён.
        catalog.search_by_skill(initial_skills["can_help"])
        expect(catalog.card_by_id(person_id)).to_be_visible()


@allure.feature("Каталог участников")
@allure.title("Поиск неизвестного навыка показывает пустую выдачу")
def test_catalog_search_without_matches_shows_empty_results(page, catalog_page, catalog_control):
    with allure.step("Проверить непустой исходный каталог"):
        catalog_page.open()
        expect(catalog_page.card_by_name(catalog_control["user"]["name"])).to_be_visible()

    with allure.step("Найти уникальный навык без совпадений"):
        skill_name = f"no-match-{uuid.uuid4().hex}"
        catalog_page.search_by_skill(skill_name)

    with allure.step("Проверить пустую выдачу и поясняющее сообщение"):
        expect(page).to_have_url(f"{BASE_URL}/pomidorqa?{urlencode({'skill': skill_name})}")
        expect(catalog_page.skill_input).to_have_value(skill_name)
        expect(catalog_page.empty_results).to_be_visible()
        expect(catalog_page.cards).to_have_count(0)


@allure.feature("Каталог участников")
@allure.title("Очистка поискового запроса возвращает каталог без фильтра")
def test_clearing_skill_search_restores_unfiltered_catalog(page, catalog_page, searchable_people):
    with allure.step("Проверить обоих участников в общем каталоге"):
        catalog_page.open()
        matching_card = catalog_page.card_by_name(searchable_people["matching_name"])
        other_card = catalog_page.card_by_name(searchable_people["other_name"])
        expect(matching_card).to_be_visible()
        expect(other_card).to_be_visible()

    with allure.step("Ограничить выдачу поиском по навыку"):
        catalog_page.search_by_skill(searchable_people["skill_name"])
        expect(catalog_page.cards).to_have_count(1)
        expect(matching_card).to_be_visible()
        expect(other_card).to_have_count(0)

    with allure.step("Отправить пустой поисковый запрос"):
        catalog_page.search_by_skill("")

    with allure.step("Проверить возвращение обоих участников"):
        expect(page).to_have_url(f"{BASE_URL}/pomidorqa?skill=")
        expect(catalog_page.skill_input).to_be_empty()
        expect(matching_card).to_be_visible()
        expect(other_card).to_be_visible()
        expect(catalog_page.empty_results).to_have_count(0)
