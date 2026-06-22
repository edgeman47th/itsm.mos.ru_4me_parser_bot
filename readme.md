# 4me parser
## Описание работы алгоритма
Система делает запрос на эндпоинт https://api.itsm.mos.ru/requests/assigned_to_my_team
c параметром __status=assigned__ 
Заголовки ``` 'Authorization': f'Bearer {BEARER_TOKEN}'```, ```'X-4me-Account': ACCOUNT_ID```
В ответе запроса массив с новыми запросами. 
пример ответа
```
[
{'id': 6464570, 'sourceID': 'CAMhxC567ZigxM5-qgDd=xJVZq74js3A84hPAxWPxGZwN1ftV+A@mail.gmail.com', 'subject': 'Проверочная тема', 'category': 'rfi', 'impact': None, 'status': 'assigned', 'next_target_at': '2025-02-26T15:36:13+03:00', 'completed_at': None, 'team': {'id': 4531, 'name': 'ПУДС. СТП', 'nodeID': 'aXRzbS5tb3MucnUvVGVhbS80NTMx'}, 'member': None, 'grouped_into': None, 'service_instance': {'id': 17698, 'name': 'ПУДС ПП. Поддержка пользователей', 'localized_name': 'ПУДС ПП. Поддержка пользователей', 'nodeID': 'aXRzbS5tb3MucnUvU2VydmljZUluc3RhbmNlLzE3Njk4'}, 'created_at': '2025-02-26T14:36:13+03:00', 'updated_at': '2025-02-26T14:36:13+03:00', 'tags': [], 'account': {'id': 'ext-sc-tr-mdg-mk', 'name': 'EXT. ДИТ. ТехРешения - Внешние подрядчики'}, 'nodeID': 'aXRzbS5tb3MucnUvUmVxLzY0NjQ1NzA'}
]
```
Данный запрос делается обрабатывается с помощью асинхронной python библиотеки **AsyncIOScheduler** и позволяет отпралять подписавшимся(отправившим /subscribe телеграмм боту) пользователям получать уведомление в отформатированном сообщении.
## Деплоймент

1. ``` git clone https://github.com/zamuragin03/4me-parser.git```
2. ```cd 4me-parser```
3. ```vim config.ini```
3.1. Вставляем данные такого формата без ковычек
```
[Telegram]

bot_token = _
[AUTH]

BEARER_TOKEN = _

ACCOUNT_ID = _
```
3. ``` docker-compose up --build -d ``` || ``` docker compose up --build -d```(версия докера 2+)






