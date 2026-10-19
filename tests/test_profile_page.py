import allure
import pytest
from playwright.sync_api import Page, expect

from pages.catalog_page import CatalogPage
from pages.person_page import PersonPage
from pages.profile_page import ProfilePage


@allure.feature("Профиль")
@allure.title("Изменённый часовой пояс сохраняется после перезагрузки")
def test_timezone_persists_after_reload(page: Page, profile_page, logged_in_page):
    with allure.step("Проверить исходный часовой пояс профиля"):
        profile_page.open()
        timezone = profile_page.timezone_list

        expect(timezone).to_have_value("Europe/Moscow")

    with allure.step("Выбрать и сохранить другой часовой пояс"):
        target_timezone = "Asia/Irkutsk"
        timezone.select_option(value=target_timezone)

        profile_page.save()

    with allure.step("Перезагрузить профиль и проверить сохранённый пояс"):
        page.reload()

        expect(timezone).to_have_value(target_timezone)


@pytest.mark.parametrize(
    "field_name, new_value",
    [
        ("name_input", "Evgeniy S"),
        ("telegram_input", "test13"),
        ("about_info_input", "Unique description"),
    ],
)
@allure.feature("Профиль")
@allure.title("Изменение поля профиля сохраняется после перезагрузки ({field_name})")
def test_text_field_persists_after_reload(
    page: Page, logged_in_page, field_name, new_value, profile_page
):
    with allure.step("Открыть редактируемое поле профиля"):
        profile_page.open()

        field = getattr(profile_page, field_name)

    with allure.step("Изменить поле и сохранить профиль"):
        field.fill(new_value)

        profile_page.save()

    with allure.step("Проверить значение после перезагрузки"):
        page.reload()

        expect(field).to_have_value(new_value)


@allure.feature("Профиль")
@allure.title("Имя, Telegram и описание сохраняются одной отправкой")
def test_profile_fields_persist_together(page: Page, logged_in_page, profile_page):
    with allure.step("Открыть профиль и подготовить новые значения"):
        profile_page.open()

        user_data = {
            "name": "Evgeniy S",
            "telegram": "telega13",
            "description": "Unique description",
        }

    with allure.step("Заполнить и сохранить все текстовые поля"):
        profile_page.fill_text_data(
            name=user_data["name"],
            telegram=user_data["telegram"],
            about_info=user_data["description"],
        )
        profile_page.save()

    with allure.step("Перезагрузить профиль и проверить все значения"):
        page.reload()

        expect(profile_page.name_input).to_have_value(user_data["name"])
        expect(profile_page.telegram_input).to_have_value(user_data["telegram"])
        expect(profile_page.about_info_input).to_have_value(user_data["description"])


@pytest.mark.parametrize("skill_name", ['Python "advanced"', "Python 'advanced'"])
@allure.feature("Навыки")
@allure.title("Навык с кавычками сохраняется после перезагрузки ({param_id})")
def test_can_help_skill_persists_after_reload(page: Page, logged_in_page, profile_page, skill_name):
    with allure.step("Добавить и проверить навык «могу помочь»"):
        profile_page.open()
        profile_page.add_skill(skill_name, "can_help")
        skill = profile_page.saved_skill(skill_name, "can_help")
        expect(skill).to_be_visible()

    with allure.step("Перезагрузить профиль и проверить сохранённый навык"):
        page.reload()
        expect(skill).to_be_visible()


@allure.feature("Навыки")
@allure.title("Оба типа навыков сохраняются в правильных разделах")
def test_can_help_and_want_to_learn_skill_persists_after_reload(
    page: Page, logged_in_page, profile_page
):
    with allure.step("Добавить навык «могу помочь»"):
        can_help_name = "Python"
        want_to_learn_name = "SQL"

        profile_page.open()
        profile_page.add_skill(can_help_name, "can_help")
        can_help_skill = profile_page.saved_skill(can_help_name, "can_help")
        expect(can_help_skill).to_be_visible()

    with allure.step("Добавить навык «хочу разобрать»"):
        profile_page.add_skill(want_to_learn_name, "want_to_learn")
        want_to_learn_skill = profile_page.saved_skill(want_to_learn_name, "want_to_learn")
        expect(want_to_learn_skill).to_be_visible()

    with allure.step("Проверить сохранение обоих навыков и их разделы после перезагрузки"):
        page.reload()

        expect(can_help_skill).to_be_visible()
        expect(want_to_learn_skill).to_be_visible()
        expect(profile_page.saved_skill(can_help_name, "want_to_learn")).to_have_count(0)
        expect(profile_page.saved_skill(want_to_learn_name, "can_help")).to_have_count(0)


@pytest.mark.parametrize(
    "skill_type, other_skill_type",
    [
        ("can_help", "want_to_learn"),
        ("want_to_learn", "can_help"),
    ],
)
@allure.feature("Навыки")
@allure.title("Удаляется навык выбранного типа, второй сохраняется ({skill_type})")
def test_removed_skill_stays_absent_after_reload(
    page: Page, logged_in_page, profile_page, skill_type, other_skill_type
):
    with allure.step("Добавить одинаковый текст навыка в оба раздела"):
        skill_name = 'Python "advanced"'
        profile_page.open()

        profile_page.add_skill(skill_name, skill_type)
        skill_to_remove = profile_page.saved_skill(skill_name, skill_type)
        expect(skill_to_remove).to_be_visible()

        profile_page.add_skill(skill_name, other_skill_type)
        skill_to_keep = profile_page.saved_skill(skill_name, other_skill_type)
        expect(skill_to_keep).to_be_visible()

    with allure.step("Удалить навык только выбранного типа"):
        profile_page.remove_skill(skill_name, skill_type)

        expect(skill_to_remove).to_have_count(0)
        expect(skill_to_keep).to_be_visible()

    with allure.step("Проверить сохранение удаления и второго навыка после перезагрузки"):
        page.reload()

        expect(skill_to_remove).to_have_count(0)
        expect(skill_to_keep).to_be_visible()


@allure.feature("Профиль")
@allure.title("Другой участник видит сохранённый профиль и оба типа навыков")
def test_saved_profile_is_visible_to_another_user(user_factory, published_profile):
    with allure.step("Проверить сохранённые имя и описание в каталоге другого участника"):
        viewer = user_factory("profile-viewer")
        profile_data = published_profile["data"]

        catalog = CatalogPage(viewer["page"])
        catalog.open()
        owner_card = catalog.card_by_name(profile_data["name"])

        expect(owner_card).to_have_count(1)
        expect(owner_card).to_contain_text(profile_data["bio"])

    with allure.step("Открыть карточку и проверить публичные данные и навыки"):
        owner_card.click()

        person = PersonPage(viewer["page"])
        expect(person.get_creator_name(profile_data["name"])).to_have_text(profile_data["name"])
        expect(person.profile_text(profile_data["bio"])).to_be_visible()
        expect(person.profile_text(profile_data["telegram"])).to_be_visible()

        for skill_type, skill_name in published_profile["skills"].items():
            expect(person.skill_tag(skill_name, skill_type)).to_be_visible()


@allure.feature("Профиль")
@allure.title("Пустое имя не заменяет сохранённое имя профиля")
def test_empty_name_cannot_replace_saved_name(
    page: Page, logged_in_page, profile_page, created_account
):
    with allure.step("Проверить исходное сохранённое имя"):
        profile_page.open()
        saved_name = created_account["user"]["name"]
        expect(profile_page.name_input).to_have_value(saved_name)

    with allure.step("Попытаться сохранить профиль без имени"):
        profile_page.name_input.clear()
        # HTML-валидация блокирует запрос: save(), ожидающий ответ, здесь не подходит.
        profile_page.save_button.click()

    with allure.step("Проверить блокировку обязательного поля"):
        expect(profile_page.name_input).to_be_empty()
        expect(profile_page.name_input).to_have_attribute("required", "")
        expect(profile_page.name_input.and_(page.locator(":invalid"))).to_have_count(1)
        expect(profile_page.name_input).to_be_focused()

    with allure.step("Перезагрузить профиль и проверить прежнее имя"):
        page.reload()
        expect(profile_page.name_input).to_have_value(saved_name)


@pytest.mark.parametrize(
    "field_name, initial_value, other_field_name, other_value",
    [
        ("telegram_input", "@qa_clear", "about_info_input", "Описание сохраняется"),
        ("about_info_input", "Описание для удаления", "telegram_input", "@qa_keep"),
    ],
    ids=["clear_telegram", "clear_bio"],
)
@allure.feature("Профиль")
@allure.title("Необязательное поле можно очистить, соседнее сохраняется ({field_name})")
def test_optional_profile_field_can_be_cleared_and_saved(
    page: Page,
    logged_in_page,
    profile_page,
    field_name,
    initial_value,
    other_field_name,
    other_value,
):
    with allure.step("Сохранить и проверить заполненные необязательные поля"):
        profile_page.open()
        field = getattr(profile_page, field_name)
        other_field = getattr(profile_page, other_field_name)
        field.fill(initial_value)
        other_field.fill(other_value)
        profile_page.save()
        page.reload()
        expect(field).to_have_value(initial_value)
        expect(other_field).to_have_value(other_value)

    with allure.step("Очистить выбранное поле и сохранить профиль"):
        field.clear()
        profile_page.save()

    with allure.step("Проверить пустое поле и неизменное соседнее после перезагрузки"):
        page.reload()

        expect(field).to_be_empty()
        expect(other_field).to_have_value(other_value)


@pytest.mark.parametrize("skill_type", ["can_help", "want_to_learn"])
@allure.feature("Навыки")
@allure.title("Повторное добавление навыка того же типа не создаёт дубль ({skill_type})")
def test_same_skill_cannot_be_added_twice_in_one_type(
    page: Page, logged_in_page, profile_page, skill_type
):
    with allure.step("Проверить отсутствие навыка и добавить его впервые"):
        skill_name = "Python"
        profile_page.open()
        skill = profile_page.saved_skill(skill_name, skill_type)
        expect(skill).to_have_count(0)

        profile_page.add_skill(skill_name, skill_type)
        expect(profile_page.skill_input).to_be_empty()
        expect(skill).to_have_count(1)

    with allure.step("Повторно добавить тот же навык и проверить единственную запись"):
        profile_page.add_skill(skill_name, skill_type)
        # Очистка формы означает, что результат повторной отправки уже применён в UI.
        expect(profile_page.skill_input).to_be_empty()
        expect(skill).to_have_count(1)

    with allure.step("Проверить отсутствие дубля после перезагрузки"):
        page.reload()
        expect(profile_page.skill_input).to_be_visible()
        expect(skill).to_have_count(1)


@allure.feature("Профиль")
@allure.title("Изменение опубликованного профиля видно другому участнику")
def test_updated_profile_is_visible_to_another_user(user_factory, published_profile):
    with allure.step("Посмотреть исходный публичный профиль другим участником"):
        viewer = user_factory("profile-reader")
        old_data = published_profile["data"]
        catalog = CatalogPage(viewer["page"])
        catalog.open()
        card = catalog.card_by_name(old_data["name"])
        expect(card).to_be_visible()
        expect(card).to_contain_text(old_data["bio"])
        person_id = card.get_attribute("data-person-id")
        assert person_id, "У опубликованного профиля отсутствует ID"
        card.click()

        person = PersonPage(viewer["page"])
        expect(person.get_creator_name(old_data["name"])).to_be_visible()
        expect(person.profile_text(old_data["bio"])).to_be_visible()
        expect(person.profile_text(old_data["telegram"])).to_be_visible()

    with allure.step("Изменить и сохранить профиль владельца"):
        updated = {
            "name": f"{old_data['name']} updated",
            "telegram": f"{old_data['telegram']}_new",
            "bio": f"Новое описание — {old_data['name']}",
        }
        owner_profile = ProfilePage(published_profile["person"]["page"])
        owner_profile.open()
        owner_profile.fill_text_data(updated["name"], updated["telegram"], updated["bio"])
        owner_profile.save()
        published_profile["person"]["page"].reload()
        expect(owner_profile.name_input).to_have_value(updated["name"])
        expect(owner_profile.telegram_input).to_have_value(updated["telegram"])
        expect(owner_profile.about_info_input).to_have_value(updated["bio"])

    with allure.step("Проверить новые данные и отсутствие старых в публичном профиле"):
        viewer["page"].reload()
        expect(person.get_creator_name(updated["name"])).to_be_visible()
        expect(person.profile_text(updated["bio"])).to_be_visible()
        expect(person.profile_text(updated["telegram"])).to_be_visible()
        expect(person.get_creator_name(old_data["name"])).to_have_count(0)
        expect(person.profile_text(old_data["bio"])).to_have_count(0)
        expect(person.profile_text(old_data["telegram"])).to_have_count(0)

    with allure.step("Проверить обновлённую карточку в каталоге"):
        catalog.open()
        updated_card = catalog.card_by_id(person_id)
        expect(updated_card).to_have_count(1)
        expect(updated_card).to_contain_text(updated["name"])
        expect(updated_card).to_contain_text(updated["bio"])
        expect(catalog.card_by_name(old_data["name"])).to_have_count(0)
        expect(updated_card).not_to_contain_text(old_data["bio"])


@pytest.mark.parametrize("skill_type", ["can_help", "want_to_learn"])
@allure.feature("Навыки")
@allure.title("Пустой навык не добавляется, существующий сохраняется ({skill_type})")
def test_empty_skill_is_not_added(page, logged_in_page, profile_page, skill_type):
    with allure.step("Добавить существующий навык для проверки сохранности списка"):
        profile_page.open()
        profile_page.add_skill("Python", skill_type)
        expect(profile_page.saved_skill("Python", skill_type)).to_be_visible()
        expect(profile_page.skill_tags).to_have_count(1)

    with allure.step("Попытаться добавить пустой навык"):
        profile_page.skill_input.clear()
        profile_page.type_skill.select_option(value=skill_type)
        # Пустое обязательное поле блокирует отправку: серверного ответа не ждём.
        profile_page.add_skill_button.click()

    with allure.step("Проверить обязательность поля и неизменность списка"):
        expect(profile_page.skill_input).to_be_empty()
        expect(profile_page.skill_input).to_have_attribute("required", "")
        expect(profile_page.skill_input.and_(page.locator(":invalid"))).to_have_count(1)
        expect(profile_page.skill_input).to_be_focused()
        expect(profile_page.skill_tags).to_have_count(1)

    with allure.step("Проверить сохранность списка после перезагрузки"):
        page.reload()
        expect(profile_page.skill_input).to_be_visible()
        expect(profile_page.skill_tags).to_have_count(1)
        expect(profile_page.saved_skill("Python", skill_type)).to_be_visible()
