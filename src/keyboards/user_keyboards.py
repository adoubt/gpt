from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from src.methods.database.config_manager import ConfigManager

def get_file_upload_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Загрузить файл")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb)


def get_admin_panel_kb() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="[🔨] Бан", callback_data="ban"),
         InlineKeyboardButton(text="[🔓] Разбан", callback_data="unban")],
        # [InlineKeyboardButton(text="[✏️] Сменить apikey", callback_data="setkey"),
        # [InlineKeyboardButton(text="[🎭] Сменить prompt", callback_data="setprompt")],
        [InlineKeyboardButton(text="[🎭] Личности", callback_data="getprompts_first_0_0")],
        [InlineKeyboardButton(text="[✉️] Рассылка", callback_data="queue"),
         InlineKeyboardButton(text="[💻] Статистика", callback_data="stats")],
         [InlineKeyboardButton(text="[🔑] ApiKeys", callback_data="apikeys"),
         InlineKeyboardButton(text="[⚙️] Настройки",callback_data="settings")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_settings_kb() -> InlineKeyboardMarkup:
    kb = [
        
        [InlineKeyboardButton(text="Канал", callback_data="channel")],
        [InlineKeyboardButton(text="Длина запроса", callback_data="request_len"),
         InlineKeyboardButton(text="Длина ответа", callback_data="max_tokens")],
        [InlineKeyboardButton(text="Шаг очистки", callback_data="limit_clear_msg")],
        [InlineKeyboardButton(text="Размер контекста",callback_data="limit_msg")],
        [InlineKeyboardButton(text="Температура",callback_data="temperature")],
        [InlineKeyboardButton(text="❌Удалить юзеров",callback_data="del_users")],
        [InlineKeyboardButton(text="🔙 Назад",callback_data="admin")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_subscription_kb(link) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🗝 Подписаться', url=link)],
        [InlineKeyboardButton(text='🔎 Проверить подписку', callback_data="check_subscribe")]
    ])

    return ikb

def get_apikeys_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить", callback_data="addkey"),
        InlineKeyboardButton(text="❌Удалить", callback_data="del_apikeys")],
        [InlineKeyboardButton(text='🔙Назад', callback_data="admin")]
    ])
    return ikb
def get_del_apikeys_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Да, удалить', callback_data="del_apikeys_yes")],
        [InlineKeyboardButton(text='🔙Отмена', callback_data="apikeys")]
    ])
    return ikb


def get_del_users_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Да, удалить', callback_data="del_users_yes"),
        InlineKeyboardButton(text='🔙Отмена', callback_data="settings")]
    ])
    return ikb

def get_del_prompts_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Да, удалить', callback_data="del_prompts_yes"),
        InlineKeyboardButton(text='🔙Отмена', callback_data="admin")]
    ])
    return ikb


def cancel_prompts_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='❌ Отмена', callback_data="cancel_state_prompts")]
    ])

    return ikb

def cancel_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='❌ Отмена', callback_data="cancel_state")]
    ])

    return ikb

def back_admin_panel_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔙 Назад', callback_data="admin")]
    ])
    return ikb

def add_more_tokens() ->InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='[✏️] Добавить еще',callback_data="addkey")],
        [InlineKeyboardButton(text='🔙Назад',callback_data="admin")]
    ])
    return ikb

async def get_sub_kb() -> InlineKeyboardMarkup:
    sub = await ConfigManager.get_value('sub')
    
    if sub == 1:
        sub_1= "✔️"
        sub_0 =""
    elif sub == 0:
        sub_1= ""
        sub_0 ="✔️"
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Да{sub_1}', callback_data="sub_1"),
         InlineKeyboardButton(text=f'Нет{sub_0}', callback_data="sub_0")],
        [InlineKeyboardButton(text='🔙Назад', callback_data="channel")]
    ])
    return ikb
def get_channel_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сменить ID', callback_data="set_channel"),
         InlineKeyboardButton(text='Сменить link', callback_data="set_link")],
        [InlineKeyboardButton(text="Проверка подписки", callback_data="sub")],
        [InlineKeyboardButton(text='🔙Назад', callback_data="settings")]
    ])
    return ikb

def get_request_len_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сменить значение', callback_data="set_request_len")],
        [InlineKeyboardButton(text='🔙 Назад', callback_data="settings")]
    ])
    return ikb

def get_max_tokens_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сменить значение', callback_data="set_max_tokens")],
        [InlineKeyboardButton(text='🔙 Назад', callback_data="settings")]
    ])
    return ikb

def get_limit_clear_msg_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сменить значение', callback_data="set_limit_clear_msg")],
        [InlineKeyboardButton(text='🔙 Назад', callback_data="settings")]
    ])
    return ikb

def get_limit_msg_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сменить значение', callback_data="set_limit_msg")],
        [InlineKeyboardButton(text='❌Очистить контект', callback_data="clear_all_context")],
        [InlineKeyboardButton(text='🔙 Назад', callback_data="settings")]
    ])
    return ikb

def get_temperature_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сменить значение', callback_data="set_temperature")],
        [InlineKeyboardButton(text='🔙 Назад', callback_data="settings")]
    ])
    return ikb

def get_prompt_kb(prompt_id)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Удалить', callback_data=f"del_prompt_{prompt_id}")],
        [InlineKeyboardButton(text='🔙 Назад', callback_data="getprompts_first_0_0")]
    ])
    return ikb
def get_del_prompt_kb(prompt_id)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Да, удалить', callback_data=f"del_prompt_yes_{prompt_id}"),
        InlineKeyboardButton(text='🔙Отмена', callback_data=f"prompt_{prompt_id}_0")]
    ])
    return ikb

def get_prompts_kb(prompts,current_page:int, total_pages:int,view_mode:int)-> InlineKeyboardMarkup:
    
    buttons = []
    for prompt in prompts:
        buttons = buttons+[InlineKeyboardButton(text=prompt[1], callback_data=f"prompt_{prompt[0]}_{view_mode}")]
    pagination = []
    # if current_page != 1:
    # pagination.append(InlineKeyboardButton(text='⏪', callback_data=f"getprompts_first_{current_page}"))
    # if current_page > 1:
    pagination.append(InlineKeyboardButton(text='◀️', callback_data=f"getprompts_prev_{current_page}_{view_mode}"))
    pagination.append(InlineKeyboardButton(text = f"{current_page}/{total_pages}", callback_data="current_page"))
    # if current_page < total_pages:
    pagination.append(InlineKeyboardButton(text='▶️', callback_data=f"getprompts_next_{current_page}_{view_mode}"))
    # if current_page!= total_pages:
    # pagination.append(InlineKeyboardButton(text='⏩', callback_data=f"getprompts_last_{current_page}"))

    # buttons.append(pagination)
    footer = []
    
    footer.append(InlineKeyboardButton(text='Добавить', callback_data="add_prompt"))
    footer.append(InlineKeyboardButton(text='Удалить все', callback_data="del_prompts"))
    back = []
    back.append(InlineKeyboardButton(text='Назад', callback_data="admin"))
    # buttons.append(footer)
    if view_mode == 0:
        rows= [[btn] for btn in buttons] + [pagination] + [footer] + [back]
    elif view_mode == 1:
        rows= [[btn] for btn in buttons] + [pagination] 
    ikb = InlineKeyboardMarkup(inline_keyboard=rows)
    return ikb

def get_context_kb(context_status)-> InlineKeyboardMarkup:
    btn = "Включить"
    if context_status==1:
        btn = "Выключить"
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Очистить контекст', callback_data=f"del_context")],
        [InlineKeyboardButton(text=f'{btn} контекст', callback_data=f"context_status_{context_status}")],
        [InlineKeyboardButton(text='🔙Назад', callback_data="start")]
    ])
    return ikb
    
def get_menu() -> ReplyKeyboardMarkup:
    rkb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('🎭Личности','🎭Личности')],
        [KeyboardButton('👤Мой аккаунт','👤Мой аккаунт')]
    ])
    return rkb

