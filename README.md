# Retma
## Настройки:

- Устанавливаем [Python](https://www.python.org/downloads/release/python-3115/).
>     Рекомендуется версия 3.11.5 
- Устанавливаем библиотеки в *Cmd*:
>     pip install openai aiosqlite aiogram
>     pip install loguru
>     pip install tiktoken
- Идем в *src/misc.py*:
  - Ставим токен (Получить токен можно здесь https://t.me/BotFather)
  - Здесь же в BotFather cтавим команды:
>     start - 🚀 Меню
>     personality -  🎭 Личности
>     account - 👤 Мой профиль
>     info - ℹ️ Инфо
  - Устанавливаем пароль от админки (*/admin*)
>     получить права:/set_admin{пароль}
>     назначить: /set_admin{пароль} user_id
  - Устанавливаем суперадмина.
>     Сейчас используется только для уведомления о превышении {количества запросов}.
- Идем в *src/content.py*:
  - Ставим стартовое сообщение ([Для красоты сюда](https://core.telegram.org/bots/api#html-style))
  - Ставим инфо текст.
  - Ставим фото в стартовое сообщение *(не обязательно)*. 
>         Как поставить? Запускаем бота, шлем ему картинку, получаем id, вставляем.
## Запускаем main.py
    
    
