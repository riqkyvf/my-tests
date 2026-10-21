# Матрица покрытия PomidorQA

[← README](README.md)

Дата сверки: **21.10.2026**. Источник: [requirements.md](requirements.md).

**78 тестовых случаев** для Chromium с учётом параметризации:
77 UI и одна проверка API-сессии. В наборе 53 тестовые функции.

## Статусы

| Статус | Значение |
| --- | --- |
| Автоматизировано | Поведение покрыто тестами. |
| Частично автоматизировано | Покрыта часть требования. |
| Не автоматизировано | Проверка не реализована. |
| Заблокировано | Нет доступа к необходимым данным, API, подготовке данных или управлению временем сервера. |
| Вне scope MVP | Функция исключена из MVP требованиями. |

`R` — требования, `O` — функции вне MVP, `A` — дополнительные проверки.
Ссылки `Txx` ведут к перечню тестов.

## Требования и проверки

### Роли, регистрация и вход — §§3–4

| ID | Требование / проверка | Статус | Тесты | Примечание |
| --- | --- | --- | --- | --- |
| R3.1 | Гость без аккаунта просматривает каталог и публичный профиль со свободными слотами | Автоматизировано | [T16](#t16) | Каталог и свободные слоты доступны без авторизации. |
| R3.2 | Гость без аккаунта не может забронировать слот | Автоматизировано | [T16](#t16) | После подтверждения проверяются требование войти и сохранение free у слота. |
| R4.1 | Успешная регистрация по имени, email и паролю автоматически авторизует участника | Автоматизировано | [T28](#t28) | Два случая: пароль ровно 8 и ровно 9 символов; проверяются каталог и авторизованная шапка. |
| R4.2 | Имя при регистрации обязательно | Автоматизировано | [T29](#t29) | Параметр missing_name; нативная HTML-валидация и отсутствие входа. |
| R4.3 | Email при регистрации обязателен | Автоматизировано | [T29](#t29) | Параметр missing_email; нативная HTML-валидация и отсутствие входа. |
| R4.4 | Пароль при регистрации обязателен: 0 символов отклоняется | Автоматизировано | [T29](#t29) | Параметр missing_password. |
| R4.5 | Пароль не короче 8 символов: 7 отклоняется, 8 и 9 принимаются | Автоматизировано | [T30](#t30), [T28](#t28) | Пароли длиной 7, 8 и 9 символов; проверка через UI. |
| R4.6 | После UI-регистрации профиль получает имя из формы и Europe/Moscow | Автоматизировано | [T28](#t28) | Имя из формы и Europe/Moscow в созданном профиле. |
| R4.7 | Вход с верными email и паролем успешен | Автоматизировано | [T13](#t13) | Вход через форму; проверяются авторизация и имя в профиле. |
| R4.8 | Неверный email и неверный пароль дают одинаковую общую ошибку | Автоматизировано | [T12](#t12), [T14](#t14) | Оба теста ожидают «Неверный email или пароль». |

### Профиль — §5

| ID | Требование / проверка | Статус | Тесты | Примечание |
| --- | --- | --- | --- | --- |
| R5.1 | Имя участника можно изменить и сохранить | Автоматизировано | [T19](#t19), [T20](#t20) | Параметр name_input и совместное сохранение полей; значения проверяются после reload. |
| R5.2 | Пустое имя не заменяет сохранённое обязательное имя | Автоматизировано | [T25](#t25) | Проверяются HTML-валидация и прежнее имя после reload. |
| R5.3 | Telegram — сохраняемый необязательный свободный текст | Автоматизировано | [T19](#t19), [T26](#t26) | Заполненное значение сохраняется; очистка сохраняется пустой, соседнее поле не меняется. |
| R5.4 | Описание — сохраняемый необязательный свободный текст | Автоматизировано | [T19](#t19), [T26](#t26) | Аналогично Telegram; отдельный параметр clear_bio. |
| R5.5 | Часовой пояс по умолчанию Moscow, изменение сохраняется после reload | Автоматизировано | [T18](#t18), [T28](#t28) | Сохранение Europe/Moscow → Asia/Irkutsk и исходное значение после UI-регистрации. |
| R5.6 | Время слотов отображается в часовом поясе владельца, независимо от браузера зрителя | Автоматизировано | [T33](#t33), [T53](#t53) | Moscow → Irkutsk: пересчёт существующего слота и создание в выбранном поясе. Пояса зрителей — Kaliningrad и Vladivostok; проверен перенос даты. |
| R5.7 | Сохранённые данные профиля видны другому участнику | Автоматизировано | [T24](#t24) | Имя и описание в каталоге; имя, описание, Telegram и оба типа навыков на публичной странице. |
| R5.8 | После изменения уже опубликованного профиля другой участник видит обновлённые данные | Автоматизировано | [T40](#t40) | Изменённые имя, Telegram и описание видны после обновления публичного профиля; имя и описание обновляются в каталоге. |

### Навыки — §6

| ID | Требование / проверка | Статус | Тесты | Примечание |
| --- | --- | --- | --- | --- |
| R6.1 | Навыки can_help и want_to_learn добавляются и сохраняются в своих разделах | Автоматизировано | [T22](#t22), [T24](#t24) | После reload проверяются наличие и отсутствие в противоположном разделе. |
| R6.2 | Свободный текст навыка поддерживает кавычки | Автоматизировано | [T21](#t21), [T02](#t02) | Отдельные имена с одинарными/двойными кавычками; основной booking использует имя с обоими видами. |
| R6.3 | Одинаковый навык одного типа нельзя добавить повторно | Автоматизировано | [T27](#t27) | Оба типа; остаётся ровно одна запись сразу и после reload. |
| R6.4 | Одинаковое название в разных типах не смешивает записи | Автоматизировано | [T23](#t23) | Навык создаётся в обоих типах; удаление выбранного типа сохраняет второй. |
| R6.5 | Навык каждого типа можно удалить, удаление сохраняется | Автоматизировано | [T23](#t23) | Оба типа, проверка после reload. |
| R6.6 | Добавление/удаление навыка отражается у другого участника и в поиске | Автоматизировано | [T41](#t41) | Добавление и удаление обоих типов видны в публичном профиле; поиск реагирует только на can_help. Остальные навыки сохраняются. |

### Слоты — §7

| ID | Требование / проверка | Статус | Тесты | Примечание |
| --- | --- | --- | --- | --- |
| R7.1 | Свободный будущий слот создаётся с заданными датой и временем и сохраняется | Автоматизировано | [T31](#t31), [T53](#t53) | Дата, время и free после reload, включая создание в немосковском поясе профиля. |
| R7.2 | Прошедшую календарную дату нельзя отправить через форму | Автоматизировано | [T34](#t34) | Проверяются min=сегодня, invalid при вчерашней дате и отсутствие записи после reload. Это UI-валидация. |
| R7.3 | При сегодняшней дате прошедшее время не создаёт слот | Автоматизировано | [T36](#t36) | Сегодня, 00:00 по Москве; реальный ответ формы и отсутствие записи после reload. В первую минуту суток тест пропускается. |
| R7.4 | Длительность слота фиксирована и составляет 25 минут | Заблокировано | — | Доступный интерфейс не выдаёт фактический end_time созданного слота, а подпись «25 минут» не доказывает серверную длительность. |
| R7.5 | Слоты переходят между free и booked при бронировании/отмене | Автоматизировано | [T02](#t02), [T04](#t04) | Проверяются статусы конкретного data-slot-id. |
| R7.6 | Владелец удаляет свой свободный слот | Автоматизировано | [T32](#t32) | Удаление конкретного ID, проверка после reload. |
| R7.7 | Забронированный слот нельзя удалить через интерфейс | Автоматизировано | [T35](#t35) | Кнопка удаления отсутствует; booked и встреча сохраняются после reload. |
| R7.8 | Чужой слот нельзя удалить | Заблокировано | — | Нет API удаления слотов для проверки серверных прав. |
| R7.9 | Удаление одного из нескольких слотов сохраняет остальные | Автоматизировано | [T39](#t39) | Удаляется средний из трёх слотов; ID, дата, время и free остальных сохраняются после reload. |

### Каталог — §8

| ID | Требование / проверка | Статус | Тесты | Примечание |
| --- | --- | --- | --- | --- |
| R8.1 | Участник со свободным будущим слотом виден в каталоге | Автоматизировано | [T07](#t07), [T08](#t08) | Карточка подготовленного участника видна другому посетителю. |
| R8.2 | Участник без слотов скрыт | Автоматизировано | [T09](#t09) | Контрольный участник с доступностью остаётся видимым. |
| R8.3 | После удаления последнего свободного слота участник скрыт | Автоматизировано | [T10](#t10) | Карточка сначала видна; после удаления слота и нового открытия каталога отсутствует. |
| R8.4 | Участник только с booked-слотами скрыт | Автоматизировано | [T11](#t11) | Проверяется реальный booked-слот и отсутствие карточки по person-id. |
| R8.5 | Участник с booked- и свободным будущим слотом остаётся видимым | Автоматизировано | [T37](#t37) | Карточка остаётся видимой при наличии booked- и free-слотов. |
| R8.6 | Участник только с прошедшими слотами скрыт | Заблокировано | — | Нет API/БД для подготовки прошедших слотов и управления временем сервера. |
| R8.7 | Участник не видит себя в собственном каталоге | Автоматизировано | [T08](#t08) | Другой посетитель видит карточку; сам владелец не видит, контрольная карточка остаётся. |
| R8.8 | UI-поиск находит по can_help и не находит только по want_to_learn | Автоматизировано | [T07](#t07) | Одинаковый искомый навык у двух участников в разных типах; проверяются URL и отфильтрованные карточки. |
| R8.9 | Для навыка без совпадений выдача пуста | Автоматизировано | [T42](#t42) | Поиск по отсутствующему навыку: нет карточек, показана пустая выдача, запрос сохранён в поле. |

### Публичная страница — §9

| ID | Требование / проверка | Статус | Тесты | Примечание |
| --- | --- | --- | --- | --- |
| R9.1 | На странице видны имя, описание и навыки в правильных разделах | Автоматизировано | [T24](#t24) | Имя, описание и оба типа навыков в публичном профиле. |
| R9.2 | Свободные будущие слоты доступны для просмотра | Автоматизировано | [T16](#t16), [T02](#t02) | Дата и время своего подготовленного слота; в подтверждении сверяется slot-id. |
| R9.3 | Забронированные слоты скрыты, свободные остаются видимыми | Автоматизировано | [T17](#t17) | Слоты в один день и в разные дни; день только с booked скрыт, день со свободным временем остаётся. |
| R9.4 | Прошедшие слоты скрыты | Заблокировано | — | Нужны прошедшие записи или управление временем сервера. |
| R9.5 | При нескольких днях и временах выбирается именно нужный свободный слот | Автоматизировано | [T38](#t38) | Выбор среди трёх слотов на два дня; сверяются slot-id, дата, время и booking-id. Остальные слоты остаются free. |

### Бронирование — §10

| ID | Требование / проверка | Статус | Тесты | Примечание |
| --- | --- | --- | --- | --- |
| R10.1 | Зарегистрированный участник бронирует чужой свободный будущий слот | Автоматизировано | [T02](#t02) | Успех, дата/время, одинаковый booking-id у обеих сторон и booked у исходного слота. |
| R10.2 | Нельзя забронировать собственный слот | Автоматизировано | [T03](#t03) | Публичный профиль открыт по прямой ссылке в контексте владельца; ошибка, free и отсутствие встречи. |
| R10.3 | Нельзя повторно забронировать уже занятый слот | Автоматизировано | [T06](#t06) | Оба открывают окно заранее; проигравший получает ошибку занятости, дополнительная встреча не появляется. |
| R10.4 | Нельзя забронировать прошедший слот | Заблокировано | — | Невозможно подготовить реальный прошедший слот имеющимися инструментами. |
| R10.5 | Создаваемая бронь имеет внутренний статус confirmed | Частично автоматизировано | [T02](#t02), [T06](#t06) | Подтверждение и ближайшая встреча проверяются через UI; внутреннее поле confirmed непосредственно не читается. |
| R10.6 | Гонка двух UI-бронирований создаёт ровно одну встречу | Автоматизировано | [T06](#t06) | Запросы удерживаются до отправки обоими участниками, затем идут на реальный сервер; победитель заранее не фиксирован. |
| R10.7 | Проигравший видит понятную ошибку и предложение выбрать другой слот | Автоматизировано | [T06](#t06) | Проверяется точный текст ошибки и отсутствие успеха/ближайшей встречи у проигравшего. |

### Отмена — §11

| ID | Требование / проверка | Статус | Тесты | Примечание |
| --- | --- | --- | --- | --- |
| R11.1 | Отмену может выполнить каждый из двух участников | Автоматизировано | [T04](#t04), [T05](#t05) | Параметры host и guest; обе стороны проверяются после действия. |
| R11.2 | Менее чем за два часа отмена запрещена, включая час до встречи | Автоматизировано | [T05](#t05) | 60 и 115 минут до начала, для обеих сторон: сообщение об ограничении, отсутствие HTTP 5xx, сохранение брони и booked. |
| R11.3 | Более чем за два часа отмена разрешена | Автоматизировано | [T05](#t05), [T04](#t04) | 125 минут и далёкая будущая встреча; отменённая запись и free проверяются. |
| R11.4 | Ровно за 2:00:00 отмена разрешена, сразу после границы запрещена | Заблокировано | — | Для проверки точного равенства требуется управление временем сервера. |
| R11.5 | После отмены встреча отображается отменённой у обоих, слот снова free | Автоматизировано | [T04](#t04), [T05](#t05) | UI-статус «отменено» проверяется; внутреннее поле cancelled не читается напрямую. |
| R11.6 | Освободившийся слот можно забронировать третьему участнику | Автоматизировано | [T04](#t04) | Проверяются новый booking-id, обе стороны новой встречи и повторный booked того же slot-id. |

### Мои встречи — §12

| ID | Требование / проверка | Статус | Тесты | Примечание |
| --- | --- | --- | --- | --- |
| R12.1 | Ведущий и гость видят свою подтверждённую будущую встречу в ближайших | Автоматизировано | [T02](#t02), [T06](#t06), [T52](#t52) | Участник, дата, время и booking-id у обеих сторон; также две встречи одного пользователя в разных ролях. |
| R12.2 | Отменённая встреча находится в прошедших и отменённых, а не ближайших | Автоматизировано | [T04](#t04), [T05](#t05) | Проверяются оба участника после нового открытия страницы. |
| R12.3 | Начавшаяся подтверждённая встреча переходит в прошедшие | Заблокировано | — | Нет подготовки начавшихся встреч или управления серверным временем. |
| R12.4 | Список показывает только встречи текущего участника | Автоматизировано | [T06](#t06), [T51](#t51), [T52](#t52) | Свои и чужие ID в ближайших и отменённых встречах; отдельный сценарий для участника в обеих ролях. |
| R12.5 | Отмена доступна только из ближайших, для отменённой записи действия нет | Автоматизировано | [T04](#t04) | После отмены кнопка отсутствует у обеих сторон. Начавшиеся встречи — R12.3. |

### Тестовые данные и окружение — §14

| ID | Требование / проверка | Статус | Тесты | Примечание |
| --- | --- | --- | --- | --- |
| R14.1 | Для регистрации не нужны подтверждение email и приглашение | Автоматизировано | [T28](#t28) | Новый уникальный email регистрируется, сразу появляется сессия и доступен профиль. |
| R14.2 | Список доступных часовых поясов совпадает со всеми 10 значениями требований | Автоматизировано | [T50](#t50) | Все десять значений из §14 доступны для выбора, без дублей. |

### За границами MVP — §2

| ID | Требование / проверка | Статус | Тесты | Примечание |
| --- | --- | --- | --- | --- |
| O2.1 | Создание и хранение сервисом ссылки на видеозвонок | Вне scope MVP | — | — |
| O2.2 | Push/email-уведомления о бронировании и отмене | Вне scope MVP | — | — |
| O2.3 | Рейтинги и отзывы после звонка | Вне scope MVP | — | — |
| O2.4 | Модерация профилей и жалобы | Вне scope MVP | — | — |
| O2.5 | Оплата | Вне scope MVP | — | — |

### Дополнительные проверки, не отдельные пункты требований

| ID | Требование / проверка | Статус | Тесты | Примечание |
| --- | --- | --- | --- | --- |
| A.1 | Выход из аккаунта сохраняет гостевое состояние после reload | Автоматизировано | [T15](#t15) | Гостевая шапка сохраняется после перезагрузки. |
| A.2 | Тестовый API создания аккаунта выдаёт pomidorqa_session | Автоматизировано | [T01](#t01) | Проверка сессионной cookie после API-создания аккаунта. |
| A.3 | Очистка поискового запроса возвращает исходную выдачу | Автоматизировано | [T43](#t43) | После очистки поля и нажатия «Найти» снова видны оба подготовленных участника. |
| A.4 | Повторная регистрация на занятый email и неверный формат email | Автоматизировано | [T44](#t44), [T45](#t45) | Занятый email: ошибка сервера. Неверный формат: HTML-валидация для отсутствующих @, локальной части и домена; вход не выполнен. |
| A.5 | Гость не открывает защищённые страницы напрямую | Автоматизировано | [T46](#t46) | Профиль, слоты и встречи перенаправляют на форму входа. |
| A.6 | После выхода защищённые страницы требуют нового входа | Автоматизировано | [T47](#t47) | После выхода профиль, слоты и встречи требуют входа. Отзыв токена на сервере не проверяется. |
| A.7 | Отказ от подтверждения не создаёт бронирование | Автоматизировано | [T48](#t48) | После закрытия диалога и reload слот остаётся free, у обеих сторон нет встреч. |
| A.8 | Пустой навык не добавляется | Автоматизировано | [T49](#t49) | Оба типа: HTML-валидация пустого поля; список навыков не меняется после reload. |

## Критерии приёмки — §13

Регистрация, профиль, поиск и бронирование проверяются в соответствующих разделах набора.

| Негативный критерий §13 | Строка матрицы | Проверка |
| --- | --- | --- |
| Нельзя забронировать собственный слот | R10.2 | [T03](#t03) |
| Нельзя забронировать занятый слот | R10.3 | [T06](#t06) |
| Нельзя создать слот в прошлом | R7.2, R7.3 | [T34](#t34), [T36](#t36) |
| Нельзя отменить за час до звонка | R11.2 | [T05](#t05) — за час до начала, обе стороны |
| Гонка не создаёт две подтверждённые брони | R10.6 | [T06](#t06) |

## Перечень тестов

<a id="t01"></a>

- **T01** — [test_created_account_has_session_cookie](tests/test_account_api.py#L6)
  - `tests/test_account_api.py::test_created_account_has_session_cookie`

<a id="t02"></a>

- **T02** — [test_guest_books_host_slot_and_both_see_meeting](tests/test_booking.py#L20)
  - `tests/test_booking.py::test_guest_books_host_slot_and_both_see_meeting`

<a id="t03"></a>

- **T03** — [test_owner_cannot_book_own_slot](tests/test_booking.py#L117)
  - `tests/test_booking.py::test_owner_cannot_book_own_slot`

<a id="t04"></a>

- **T04** — [test_cancelled_meeting_frees_slot_for_another_user](tests/test_booking_cancellation.py#L16)
  - `tests/test_booking_cancellation.py::test_cancelled_meeting_frees_slot_for_another_user`

<a id="t05"></a>

- **T05** — [test_cancellation_respects_two_hour_deadline](tests/test_booking_cancellation.py#L91)
  - `tests/test_booking_cancellation.py::test_cancellation_respects_two_hour_deadline`

<a id="t06"></a>

- **T06** — [test_two_users_compete_for_one_slot_and_only_one_booking_is_created](tests/test_booking_race.py#L14)
  - `tests/test_booking_race.py::test_two_users_compete_for_one_slot_and_only_one_booking_is_created`

<a id="t07"></a>

- **T07** — [test_catalog_search_finds_people_by_can_help_skill](tests/test_catalog_page.py#L17)
  - `tests/test_catalog_page.py::test_catalog_search_finds_people_by_can_help_skill`

<a id="t08"></a>

- **T08** — [test_catalog_excludes_current_user](tests/test_catalog_page.py#L40)
  - `tests/test_catalog_page.py::test_catalog_excludes_current_user`

<a id="t09"></a>

- **T09** — [test_catalog_excludes_user_without_slots](tests/test_catalog_page.py#L56)
  - `tests/test_catalog_page.py::test_catalog_excludes_user_without_slots`

<a id="t10"></a>

- **T10** — [test_catalog_excludes_user_after_last_free_slot_is_removed](tests/test_catalog_page.py#L71)
  - `tests/test_catalog_page.py::test_catalog_excludes_user_after_last_free_slot_is_removed`

<a id="t11"></a>

- **T11** — [test_catalog_excludes_user_with_only_booked_slots](tests/test_catalog_page.py#L96)
  - `tests/test_catalog_page.py::test_catalog_excludes_user_with_only_booked_slots`

<a id="t12"></a>

- **T12** — [test_login_with_invalid_credentials](tests/test_login_page.py#L12)
  - `tests/test_login_page.py::test_login_with_invalid_credentials`

<a id="t13"></a>

- **T13** — [test_login_with_valid_credentials](tests/test_login_page.py#L29)
  - `tests/test_login_page.py::test_login_with_valid_credentials`

<a id="t14"></a>

- **T14** — [test_login_with_invalid_password](tests/test_login_page.py#L51)
  - `tests/test_login_page.py::test_login_with_invalid_password`

<a id="t15"></a>

- **T15** — [test_logout](tests/test_login_page.py#L71)
  - `tests/test_login_page.py::test_logout`

<a id="t16"></a>

- **T16** — [test_anonymous_guest_sees_public_slot_but_must_log_in_to_book](tests/test_person_page.py#L14)
  - `tests/test_person_page.py::test_anonymous_guest_sees_public_slot_but_must_log_in_to_book`

<a id="t17"></a>

- **T17** — [test_public_profile_hides_booked_slot_but_shows_free_slot](tests/test_person_page.py#L59)
  - `tests/test_person_page.py::test_public_profile_hides_booked_slot_but_shows_free_slot`

<a id="t18"></a>

- **T18** — [test_timezone_persists_after_reload](tests/test_profile_page.py#L38)
  - `tests/test_profile_page.py::test_timezone_persists_after_reload`

<a id="t19"></a>

- **T19** — [test_text_field_persists_after_reload](tests/test_profile_page.py#L67)
  - `tests/test_profile_page.py::test_text_field_persists_after_reload`

<a id="t20"></a>

- **T20** — [test_profile_fields_persist_together](tests/test_profile_page.py#L88)
  - `tests/test_profile_page.py::test_profile_fields_persist_together`

<a id="t21"></a>

- **T21** — [test_can_help_skill_persists_after_reload](tests/test_profile_page.py#L117)
  - `tests/test_profile_page.py::test_can_help_skill_persists_after_reload`

<a id="t22"></a>

- **T22** — [test_can_help_and_want_to_learn_skill_persists_after_reload](tests/test_profile_page.py#L131)
  - `tests/test_profile_page.py::test_can_help_and_want_to_learn_skill_persists_after_reload`

<a id="t23"></a>

- **T23** — [test_removed_skill_stays_absent_after_reload](tests/test_profile_page.py#L166)
  - `tests/test_profile_page.py::test_removed_skill_stays_absent_after_reload`

<a id="t24"></a>

- **T24** — [test_saved_profile_is_visible_to_another_user](tests/test_profile_page.py#L196)
  - `tests/test_profile_page.py::test_saved_profile_is_visible_to_another_user`

<a id="t25"></a>

- **T25** — [test_empty_name_cannot_replace_saved_name](tests/test_profile_page.py#L221)
  - `tests/test_profile_page.py::test_empty_name_cannot_replace_saved_name`

<a id="t26"></a>

- **T26** — [test_optional_profile_field_can_be_cleared_and_saved](tests/test_profile_page.py#L255)
  - `tests/test_profile_page.py::test_optional_profile_field_can_be_cleared_and_saved`

<a id="t27"></a>

- **T27** — [test_same_skill_cannot_be_added_twice_in_one_type](tests/test_profile_page.py#L289)
  - `tests/test_profile_page.py::test_same_skill_cannot_be_added_twice_in_one_type`

<a id="t28"></a>

- **T28** — [test_registration_logs_user_in_and_creates_profile](tests/test_register_page.py#L17)
  - `tests/test_register_page.py::test_registration_logs_user_in_and_creates_profile`

<a id="t29"></a>

- **T29** — [test_registration_requires_each_field](tests/test_register_page.py#L46)
  - `tests/test_register_page.py::test_registration_requires_each_field`

<a id="t30"></a>

- **T30** — [test_registration_rejects_seven_character_password](tests/test_register_page.py#L69)
  - `tests/test_register_page.py::test_registration_rejects_seven_character_password`

<a id="t31"></a>

- **T31** — [test_user_can_create_slot](tests/test_slot_page.py#L17)
  - `tests/test_slot_page.py::test_user_can_create_slot`

<a id="t32"></a>

- **T32** — [test_removed_free_slot_stays_absent_after_reload](tests/test_slot_page.py#L43)
  - `tests/test_slot_page.py::test_removed_free_slot_stays_absent_after_reload`

<a id="t33"></a>

- **T33** — [test_slot_display_uses_owner_timezone_independently_of_browser](tests/test_slot_page.py#L73)
  - `tests/test_slot_page.py::test_slot_display_uses_owner_timezone_independently_of_browser`

<a id="t34"></a>

- **T34** — [test_slot_calendar_rejects_past_dates](tests/test_slot_page.py#L181)
  - `tests/test_slot_page.py::test_slot_calendar_rejects_past_dates`

<a id="t35"></a>

- **T35** — [test_booked_slot_has_no_delete_action_and_stays_booked](tests/test_slot_page.py#L206)
  - `tests/test_slot_page.py::test_booked_slot_has_no_delete_action_and_stays_booked`

<a id="t36"></a>

- **T36** — [test_slot_cannot_be_created_for_past_time_today](tests/test_slot_page.py#L233)
  - `tests/test_slot_page.py::test_slot_cannot_be_created_for_past_time_today`

<a id="t37"></a>

- **T37** — [test_catalog_keeps_user_with_both_free_and_booked_slots](tests/test_catalog_page.py#L113)
  - `tests/test_catalog_page.py::test_catalog_keeps_user_with_both_free_and_booked_slots`

<a id="t38"></a>

- **T38** — [test_booking_selected_slot_keeps_other_slots_free](tests/test_booking.py#L155)
  - `tests/test_booking.py::test_booking_selected_slot_keeps_other_slots_free`

<a id="t39"></a>

- **T39** — [test_removing_one_slot_keeps_other_free_slots](tests/test_slot_page.py#L260)
  - `tests/test_slot_page.py::test_removing_one_slot_keeps_other_free_slots`

<a id="t40"></a>

- **T40** — [test_updated_profile_is_visible_to_another_user](tests/test_profile_page.py#L316)
  - `tests/test_profile_page.py::test_updated_profile_is_visible_to_another_user`

<a id="t41"></a>

- **T41** — [test_skill_updates_are_visible_in_public_profile_and_search](tests/test_catalog_page.py#L136)
  - `tests/test_catalog_page.py::test_skill_updates_are_visible_in_public_profile_and_search`

<a id="t42"></a>

- **T42** — [test_catalog_search_without_matches_shows_empty_results](tests/test_catalog_page.py#L212)
  - `tests/test_catalog_page.py::test_catalog_search_without_matches_shows_empty_results`

<a id="t43"></a>

- **T43** — [test_clearing_skill_search_restores_unfiltered_catalog](tests/test_catalog_page.py#L230)
  - `tests/test_catalog_page.py::test_clearing_skill_search_restores_unfiltered_catalog`

<a id="t44"></a>

- **T44** — [test_registration_rejects_existing_email](tests/test_register_page.py#L92)
  - `tests/test_register_page.py::test_registration_rejects_existing_email`

<a id="t45"></a>

- **T45** — [test_registration_rejects_invalid_email_format](tests/test_register_page.py#L119)
  - `tests/test_register_page.py::test_registration_rejects_invalid_email_format`

<a id="t46"></a>

- **T46** — [test_anonymous_guest_cannot_open_protected_page](tests/test_auth_session.py#L9)
  - `tests/test_auth_session.py::test_anonymous_guest_cannot_open_protected_page`

<a id="t47"></a>

- **T47** — [test_protected_page_requires_login_after_logout](tests/test_auth_session.py#L24)
  - `tests/test_auth_session.py::test_protected_page_requires_login_after_logout`

<a id="t48"></a>

- **T48** — [test_dismissing_booking_confirmation_keeps_slot_free](tests/test_booking.py#L214)
  - `tests/test_booking.py::test_dismissing_booking_confirmation_keeps_slot_free`

<a id="t49"></a>

- **T49** — [test_empty_skill_is_not_added](tests/test_profile_page.py#L370)
  - `tests/test_profile_page.py::test_empty_skill_is_not_added`

<a id="t50"></a>

- **T50** — [test_profile_has_all_required_timezones](tests/test_profile_page.py#L12)
  - `tests/test_profile_page.py::test_profile_has_all_required_timezones`

<a id="t51"></a>

- **T51** — [test_meetings_lists_show_only_current_participants_bookings](tests/test_meetings_page.py#L12)
  - `tests/test_meetings_page.py::test_meetings_lists_show_only_current_participants_bookings`

<a id="t52"></a>

- **T52** — [test_participant_sees_meetings_in_both_roles](tests/test_meetings_page.py#L41)
  - `tests/test_meetings_page.py::test_participant_sees_meetings_in_both_roles`

<a id="t53"></a>

- **T53** — [test_new_slot_uses_preselected_profile_timezone](tests/test_slot_page.py#L120)
  - `tests/test_slot_page.py::test_new_slot_uses_preselected_profile_timezone`

## Обновление матрицы

- При изменении требований или тестов обновляйте статусы, примечания и ссылки.
- Количество случаев сверяйте через `pytest --collect-only -q`.
