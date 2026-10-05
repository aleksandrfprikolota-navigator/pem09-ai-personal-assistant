# PEm09. Ответ на задание. Личный помощник

Бот: [@AI_MyPersonalAssistant_bot](https://t.me/AI_MyPersonalAssistant_bot).

Репозиторий: [pem09-ai-personal-assistant](https://github.com/aleksandrfprikolota-navigator/pem09-ai-personal-assistant).

Подключение к официальному API OpenAI: `https://api.openai.com/v1`.

## Этап 1. Роль ассистента

Ассистент помогает сотруднику или коллеге быстро ответить про компанию «1С-Премиум» и её услуги премиальной поддержки решений 1С. Пользователь спрашивает, чем занимается компания, куда отправить коммерческое предложение, что входит в конкретную услугу и о чём написаны статьи на сайте. Типичные вопросы: адрес `corp@1c-prem.ru`, состав корпоративной поддержки типовых решений, внедрение «1С:Шины», зачем бизнесу свой центр компетенции 1С. Факты берутся из файлов в `data/documents`: страница «О нас», восемь карточек услуг и тринадцать статей, плюс загруженный документ-приглашение. Если нужного факта в базе нет, бот прямо говорит об этом и не придумывает реквизиты. Помимо поиска по базе бот ведёт обычный диалог, принимает голос и фотографии и по явной просьбе рисует изображение.

## Этап 2. База знаний

Файлы лежат в `Project_AI_MPA/data/documents/`. В начале каждого текстового файла указан URL страницы-источника.

Страница компании:

- `company.txt` — о компании, принципы, стоимость, контакты и реквизиты. Источник: https://www.1c-prem.ru/about/

Услуги, источник каталога https://www.1c-prem.ru/services/:

- `service_target_architecture.txt` — целевая архитектура и сопровождение проектов
- `service_audit_monitoring.txt` — аудит, мониторинг и сопровождение систем
- `service_performance.txt` — оптимизация производительности
- `service_custom_development.txt` — управление клиентскими разработками
- `service_update_migration.txt` — обновление и миграция систем
- `service_data_management.txt` — управление данными
- `service_typical_solutions_support.txt` — корпоративная поддержка типовых решений
- `service_1c_bus.txt` — архитектура обмена данными, «1С:Шина»

Статьи, источник раздела https://www.1c-prem.ru/articles/:

- `article_besshovnaya-integratsiya-1s.txt`
- `article_effektivnye-instrumenty-v-razrabotke-1s.txt`
- `article_informatsionnaya-bezopasnost-bd-pri-integratsii-1s-predpriyatie-s-subd-postgrespro.txt`
- `article_izolirovannaya-krepost-dlya-apache-i-1s-na-linux.txt`
- `article_kak-reshit-problemy-s-nsi-i-povysit-effektivnost-raboty-predpriyatiya.txt`
- `article_kakogo-razmera-dolzhen-byt-avtotest.txt`
- `article_monitoring-1s-kak-obespechit-bespereboynuyu-rabotu-vashego-biznesa.txt`
- `article_nastroyka-otkazoustoychivogo-klastera-na-postgresql.txt`
- `article_premialnaya-podderzhka-1s-kak-preimushchestvo-zakazchika.txt`
- `article_vaybkoding-v-1s-ot-eksperimenta-k-upravlyaemoy-praktike.txt`
- `article_vybiraem-arkhitekturu-integratsii.txt`
- `article_vybor-resheniya-po-otkazoustoychivosti-na-postgresql.txt`
- `article_zachem-biznesu-svoy-tsentr-kompetentsii-1s-vzglyad-iznutri.txt`

Дополнительно в ту же папку загружен `Приглашение_1C_Premium_06_августа.pdf`. Его можно заменить или дополнить: бот принимает в чат файлы txt, md и pdf и кладёт их в `data/documents`.

Индексация. При старте бот сравнивает подпись файлов (имя, размер, время изменения). Если состав не менялся и индекс уже есть, повторной нарезки нет. Команда `/index` собирает индекс заново. Фрагмент — 1000 символов, перекрытие — 200, в ответ попадают 3 ближайших фрагмента. Векторное хранилище ChromaDB лежит в `data/chroma_db` и в git не входит. Команда `/stats` показывает число фрагментов. После индексации текущей папки в индексе 429 фрагментов.

Режим по умолчанию задаётся в `.env` как `BOT_MODE=rag`, поэтому вопрос по компании идёт в базу знаний сразу после `/start`.

## Этап 3. Проверка модальностей

Проверка выполняется в Telegram в чате с ботом. Ключи лежат только в `Project_AI_MPA/.env` и в репозиторий не попадают.

1. RAG. Режим `/mode rag` (он же режим по умолчанию). Вопрос: «Расскажи о центрах компетенции 1С». Ответ опирается на `article_zachem-biznesu-svoy-tsentr-kompetentsii-1s-vzglyad-iznutri.txt` и называет этот файл. Контрольный короткий вопрос: «Куда писать за персональным предложением?» — в ответе адрес `corp@1c-prem.ru` и источник `company.txt`.
2. Текст. `/mode text`, обычный вопрос без поиска по файлам. Ответ даёт GPT-4o с историей диалога. `/reset` очищает историю пользователя.
3. Голос. Голосовое сообщение уходит в Whisper (`whisper-1`), текст проходит тот же маршрут, что и обычное сообщение, ответ озвучивается TTS (`tts-1`). Для конвертации OGG в WAV нужен FFmpeg. Голос по умолчанию — `alloy`, смена командой `/voice nova`.
4. Фото. Снимок в любом режиме разбирает GPT-4o Vision. Режим `/mode vision` включает подсказку для разбора изображений.
5. Генерация изображения. Фраза «нарисуй…» или команда `/image описание` вызывает модель `gpt-image-2` в любом режиме, включая vision. Размер по умолчанию 1024×1024, качество `auto`. Параметр `style` в запрос не передаётся: он относится к другой модели и API его отклоняет. Ответ приходит как PNG. Файл остаётся на диске в `Project_AI_MPA/data/generated_images/` с именем `generated_ГГГГММДД_ЧЧММСС.png`. Папка добавлена в `.gitignore`.

Команда `/stats` после запуска показывает размер индекса. Если Telegram не принимает разметку ответа, бот отправляет тот же текст без Markdown.

## Этап 4. Архитектура

```text
Пользователь в Telegram
        |
        v
handlers: команды, текст, голос, фото, документ
        |
        v
services/router.py
   |-- явная просьба нарисовать --> gpt-image-2 --> PNG в чат и в data/generated_images
   |-- режим rag --> поиск 3 фрагментов в ChromaDB --> GPT-4o
   |-- обычный текст --> GPT-4o и история диалога
   |-- голос --> Whisper --> тот же маршрут --> TTS
   |-- фото --> GPT-4o Vision
        |
        v
Ответ в Telegram
```

`handlers` принимает сообщения Telegram. `services` ходит в OpenAI и выбирает маршрут. `rag` читает `data/documents`, режет тексты и ищет ближайшие фрагменты в ChromaDB. `utils` хранит историю диалога в памяти процесса, пишет лог и конвертирует аудио. При старте `main.py` проверяет токен командой `getMe`, затем индексирует документы, если подпись файлов изменилась.

Модели: диалог и разбор фото — `gpt-4o`, распознавание — `whisper-1`, озвучка — `tts-1`, картинки — `gpt-image-2`. Эмбеддинги для RAG — модель эмбеддингов OpenAI.

## Запуск

```bash
cd Project_AI_MPA
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py
```

В `.env` заполняются `TELEGRAM_BOT_TOKEN` и `OPENAI_API_KEY`. Значения из файла имеют приоритет над одноимёнными переменными Windows. На Windows после создания `.env` можно запустить `run.bat`.
