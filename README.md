# Retma
Настройки:
    Устанавливаем Python рекомендую 3.11.5 (Рекомендую https://www.python.org/downloads/release/python-3115/)
    Устанавливаем библиотеки в Cmd:
        pip install openai aiosqlite aiogram
        pip install loguru
        pip insall tiktoken
    Идем в src/misc.py:
        Ставим токен (Получить токен можно здесь https://t.me/BotFather)
        Ставим пароль от админки (/admin), получить права:/set_admin{пароль}, назначить: /set_admin{пароль} user_id
        Установить суперадмина. Сейчас почти не используется.
    Идем в src/content.py:
        Ставим стартовое сообщение (Для красоты сюда https://core.telegram.org/bots/api#html-style)
        Ставим инфо текст.
        Ставим фото в стартовое сообщнение (не обязательно). 
            Как поставить? Запускаем бота, шлем ему картинку, получаем id, вставляем.
    Ставим меню в ботфазере:
        start - 🚀 Меню
        personality -  🎭 Личности
        account - 👤 Мой профиль
        context - 📝 Контекст
        info - ℹ️ Инфо
    
