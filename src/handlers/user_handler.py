# import sqlite3
# import uuid
import asyncio
from aiogram import types
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from loguru import logger

from src.keyboards import user_keyboards

from src.methods.database.users_manager import UsersDatabase
from src.methods.database.tokens_manager import TokensDatabase
from src.methods.database.config_manager import ConfigManager, PromptsManager

from src.methods import openai_manager

router =  Router()
from src.misc import bot,bot_id, super_admin,password
from src.content import start_photo,start_msg,info_msg,bot_version
# from src.misc import  dp


def pursue_subscription(function):
    async def _pursue_subscription(*args, **kwargs):
        msg = args[0]
        if msg is None:
            return

        if (await is_user_subscribed(msg.from_user.id)) or (
                type(msg) is CallbackQuery and (await is_user_subscribed(msg.message.from_user.id))):
            return await function(*args, **kwargs)
        link = await ConfigManager.get_value('link') 
        msg_text = f'Для использования бота необходимо подписаться на канал.\n<a href="{link}">Подписаться (кликабельно)</a>'
       
        kb = user_keyboards.get_subscription_kb(link)

        await msg.answer(text=msg_text, parse_mode ="HTML",reply_markup=kb)
        return

    return _pursue_subscription


@router.callback_query(lambda clb: clb.data == "check_subscribe")
async def check_subscribe(clb: types.CallbackQuery, **kwargs) -> None:
    if await is_user_subscribed(clb.from_user.id):
        await clb.answer("🚨 Подписка обнаружена")
        await clb.message.answer(
            text="Спасибо за подписку, теперь вы можете пользоваться ботом!",
            parse_mode="HTML")
        return
    else:
        await clb.answer("🚨 Подписка не обнаружена")



async def is_user_subscribed(tg_id: int, **kwargs):
    sub = await ConfigManager.get_value('sub')
    channel = await ConfigManager.get_value('channel')
    if sub ==0:
        return True
    if sub ==1:
        check_member = await bot.get_chat_member(channel, tg_id)
        if check_member.status in ["member", "creator", "administrator"]:
            return True
        else:
            return False

def new_user_handler(function):
    async def _new_user_handler(*args, **kwargs):
        message: Message = args[0]
        user_id = message.from_user.id
        await UsersDatabase.create_table()
        if (await UsersDatabase.get_user(user_id)) == -1:
            await UsersDatabase.create_user(user_id)
            
            logger.success(f"Новый пользователь (ID: {user_id}")
            if user_id == int(bot_id):

                await UsersDatabase.set_value(user_id,'status',1)
                #назначение бота админом для кнопок в админке(костыль, вроде пофикшен)
                logger.info(f'[Admin] {user_id} получил права админа')
            # else:
                # await message.answer(
                # "👋 Привет, вижу ты новенький. Будем знакомы, чтобы получить список моих команд напиши <code>/help</code>",
                # parse_mode="HTML")


        return await function(*args, **kwargs)

    return _new_user_handler


def user_banned_handler(function):
    async def _user_banned_handler(*args, **kwargs):
        message: Message = args[0]
        user_id = message.from_user.id
        await UsersDatabase.create_table()
        if (await UsersDatabase.get_user(user_id)) == -1:
            await UsersDatabase.create_user(user_id)

            logger.success(f"Новый пользователь (ID: {user_id}")

        if (await UsersDatabase.is_banned(user_id)):
            await message.answer("🚨 Вы заблокированы в боте")
            return lambda x: x

        return await function(*args, **kwargs)

    return _user_banned_handler


@router.message(Command("ban"))
@new_user_handler
@user_banned_handler
async def ban_command_handler(message: types.Message, is_clb=False, **kwargs):
    args = message.text.split()
    if is_clb:
        args.insert(0, 'ban')
    user_id = message.from_user.id
    if len(args) == 2:
        ban_user_id = args[1]

        if (await UsersDatabase.get_value(user_id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return

        if not ban_user_id.isdigit():
            await message.answer(
                "Второй аргумент команды <code>/ban</code> должен являться ID пользователя.\nПример: <code>/ban 12345678</code>",
                parse_mode="HTML")
            return

        if not 0 < len(ban_user_id) < 24:
            await message.answer(
                "Длина ID пользователя должна быть от 1 до 23.\nПример: <code>/ban 12345678</code>", parse_mode="HTML")
            return

        ban_user_id = int(ban_user_id)

        if (await UsersDatabase.get_user(ban_user_id)) == -1:
            await message.answer(
                "Пользователя с данным ID не существует.", parse_mode="HTML")
            return

        await UsersDatabase.set_value(ban_user_id, 'is_banned', 1)
        await message.answer(
            f"Пользователь с ID ({ban_user_id}) был забанен.", parse_mode="HTML")
        logger.info(f"[Admin] Пользователь с ID ({ban_user_id}) был забанен админом c ID ({user_id}).")
    else:
        await message.answer(
            "Второй аргумент команды <code>/ban</code> должен являться ID пользователя.\nПример: <code>/ban 12345678</code>",
            parse_mode="HTML")


class BanState(StatesGroup):
    ban_ask = State()


@router.callback_query(lambda clb: clb.data == "ban")
@user_banned_handler
async def ban_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(BanState.ban_ask)
    await clb.message.answer("Введите ID пользователя", reply_markup=user_keyboards.cancel_kb())


@router.message(BanState.ban_ask)
@user_banned_handler

async def ban_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    await state.clear()
    await ban_command_handler(message, is_clb=True)


@router.message(Command("unban"))
@new_user_handler
@user_banned_handler

async def unban_command_handler(message: types.Message, is_clb=False, **kwargs):
    args = message.text.split()
    if is_clb:
        args.insert(0, '/unban')
    user_id = message.from_user.id
    if len(args) == 2:
        ban_user_id = args[1]

        if (await UsersDatabase.get_value(user_id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return

        if not ban_user_id.isdigit():
            await message.answer(
                "Второй аргумент команды <code>/unban</code> должен являться ID пользователя.\nПример: <code>/unban 12345678</code>",
                parse_mode="HTML")
            return

        if not 0 < len(ban_user_id) < 24:
            await message.answer(
                "Длина ID пользователя должна быть от 1 до 23.\nПример: <code>/unban 12345678</code>",
                parse_mode="HTML")
            return

        ban_user_id = int(ban_user_id)

        if (await UsersDatabase.get_user(ban_user_id)) == -1:
            await message.answer(
                "Пользователя с данным ID не существует.", parse_mode="HTML")
            return

        await UsersDatabase.set_value(ban_user_id, 'is_banned', 0)
        await message.answer(
            f"Пользователь с ID ({ban_user_id}) был разбанен.", parse_mode="HTML")
        logger.info(f"[Admin] Пользователь с ID ({ban_user_id}) был разбанен админом c ID ({user_id}).")
    else:
        await message.answer(
            "Второй аргумент команды <code>/unban</code> должен являться ID пользователя.\nПример: <code>/unban 12345678</code>",
            parse_mode="HTML")


class UnBanState(StatesGroup):
    unban_ask = State()


@router.callback_query(lambda clb: clb.data == "unban")
@user_banned_handler

async def unban_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(UnBanState.unban_ask)
    await clb.message.answer("Введите ID пользователя", reply_markup=user_keyboards.cancel_kb())


@router.message(UnBanState.unban_ask)
@user_banned_handler

async def unban_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    await state.clear()
    await unban_command_handler(message, is_clb=True)


@router.message(Command("addkey"))
@new_user_handler
async def addkey_command_handler(message: types.Message, is_clb=False, **kwargs):

    # if is_clb:
    #     args.insert(0, '/addkey')
    user_id = message.from_user.id
    apikeys = message.text

    if (await UsersDatabase.get_value(user_id, 'status')) != 1:
        await message.answer(
            "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
            parse_mode="HTML")
        return

    # if not 0 < len(ban_user_id) < 24:
    #     await message.answer(
    #         "Длина ID пользователя должна быть от 1 до 23.\nПример: <b>/unban 12345678</b>", parse_mode="HTML")
    #     return
    apikeys = apikeys.split('\n')
    await TokensDatabase.create_table()
    for count,key in enumerate(apikeys):
        await TokensDatabase.create_token(key)
    
    await message.answer(
        f"🚨 Добавлены токены OpenAI:\n<b>Кол-во:{count+1}</b>.", parse_mode="HTML",reply_markup=user_keyboards.add_more_tokens())
    logger.info(f"[Admin] Добавлены токены OpenAI:<b>Кол-во:{count+1}</b>")


class AddKeyState(StatesGroup):
    addkey_ask = State()

@router.callback_query(lambda clb: clb.data == "addkey")
async def addkey_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(AddKeyState.addkey_ask)
    msg1 = await clb.message.answer("Введите apikeys ", reply_markup=user_keyboards.cancel_kb())
    await state.set_data(msg1)

@router.message(AddKeyState.addkey_ask)
async def addkey_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    
    # msg1 = state.get_data()
    msg1 = await state.get_data()
    await state.clear()
    await bot.delete_message(chat_id=msg1.chat.id,message_id=msg1.message_id)
   
    await addkey_command_handler(message, is_clb=True)




@router.message(Command("setprompt"))
@new_user_handler
async def setprompt_command_handler(message: types.Message, is_clb=False, **kwargs):
    args = message.text.split()
    if is_clb:
        args.insert(0, '/setprompt')
    user_id = message.from_user.id
    if len(args) >= 2:
        key = ' '.join(args[1:])

        if (await UsersDatabase.get_value(user_id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return

        await ConfigManager.set_value('prompt', key)
        await message.answer(
            f"🚨 Было изменено значение <b>промта : {key}</b>.", parse_mode="HTML")
        #logger.info(f"[Admin] Изменено значение prompt на {key}.")
    else:
        await message.answer(
            "Второй аргумент команды <code>/setprompt</code> должен prompt для OpenAI.\nПример: <code>/setprompt [prompt]</code>",
            parse_mode="HTML")


class SetPromptSate(StatesGroup):
    setprompts_ask = State()


@router.callback_query(lambda clb: clb.data == "setprompt")
async def setprompt_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(SetPromptSate.setprompts_ask)
    await clb.message.answer("Введите prompt", reply_markup=user_keyboards.cancel_kb())


@router.callback_query(lambda x: x.data == 'cancel_state')
async def cancel_handler(clb: types.CallbackQuery, state: FSMContext, **kwargs):
    current_state = await state.get_state()

    if current_state is None:
        return

    
    msg1 = await state.get_data()
    await bot.delete_message(chat_id=msg1.chat.id,message_id=msg1.message_id)
    await state.clear()
    await clb.answer('Ввод отменен')

@router.callback_query(lambda x: x.data == 'cancel_state_prompts')
async def cancel_state_prompts_handler(clb: types.CallbackQuery, state: FSMContext, **kwargs):
    current_state = await state.get_state()
    await clb.message.delete()
    if current_state is None:
        return
    
    await state.clear()
    await clb.answer('Ввод отменен')

@router.message(SetPromptSate.setprompts_ask)
async def setprompt_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    await state.clear()
    await setprompt_command_handler(message, is_clb=True)


@router.message(Command("admin"))
@new_user_handler
@user_banned_handler

async def admin_panel_handler(message: types.Message, is_clb = False, **kwargs):
    args = message.text.split()
    if is_clb:
        args = ['/admin']
    user_id = message.from_user.id
    if (await UsersDatabase.get_value(user_id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return
    if len(args) == 1:

        await message.answer(
            f"Добро пожаловать в админ-панель!{bot_version}", reply_markup=user_keyboards.get_admin_panel_kb(), parse_mode="HTML")
    else:
        await message.answer(
            "Команда <code>/admin</code> не содержит аргументов.\nПример: <code>/admin</code>",
            parse_mode="HTML")
        
@router.callback_query(lambda clb: clb.data == "admin")
async def queue_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await clb.message.edit_text(
            f"Добро пожаловать в админ-панель!{bot_version}", reply_markup=user_keyboards.get_admin_panel_kb(), parse_mode="HTML")


@router.message(Command(f"set_admin{password}"))
@new_user_handler
@user_banned_handler
async def set_admin_handler(message: types.Message, is_clb = False, **kwargs):
    args = message.text.split()
    if is_clb:
        args.insert(0, f'/set_admin{password}')
    
    if len (args) == 1:
        user_id = message.from_user.id
        await UsersDatabase.set_value(user_id,'status',1)
        await message.answer(f'Юзер {user_id} получил права админа')
        logger.info(f'[Admin] {user_id} получил права админа')

    elif len(args) == 2:

        user_id=args[1]
        await UsersDatabase.set_value(user_id,'status',1)
        await message.answer(f'Юзер {user_id} получил права админа')
        logger.info(f'[Admin] {user_id} получил права админа')
    else:
        await message.answer(f'?')
        

@router.message(Command("queue"))
@new_user_handler
@user_banned_handler

async def send_all(message: Message, is_clb=False, **kwargs):
    if not is_clb:
        if (await UsersDatabase.get_value(message.from_user.id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return
    await message.delete()
    if message.text:

        args = message.text.split()
        if is_clb:
            args.insert(0, '/queue')
            q_text = ' '.join(args[1:])
    else:
        q_text = message.caption
        photo_id = message.photo[-1].file_id
    
    
    message2 =await message.answer_sticker(sticker='CAACAgIAAxkBAAIqxmUt8GcHobTJpCaHcuhvkpUFkss9AAJIAgACVp29Chz1cvjcKRTQMAQ')
    users = await UsersDatabase.get_all()
   
    message3 = await message.answer(f'Осталось отправить: <code>{len(users)}</code>',parse_mode="HTML")
    await asyncio.sleep(2)
    for i,user in enumerate(users):
        
        try:
            if message.text:
                await bot.send_message(user[0], q_text,parse_mode="HTML")
            else:
                await bot.send_photo(chat_id=user[0],photo=photo_id,caption=q_text,parse_mode="HTML")
            i+=1
            await message3.edit_text(f'Осталось отправить: <code>{len(users)-i}</code>',parse_mode="HTML")
        
        except Exception as _ex:
            pass
        
    else:
        await message2.delete()
        await message3.edit_text(f'Рассылка окончена😎\nОтправлено сообщений:<code>{i}</code>',parse_mode="HTML")
        


class QueueState(StatesGroup):
    queue_ask = State()

@router.callback_query(lambda clb: clb.data == "queue")
@user_banned_handler
async def queue_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(QueueState.queue_ask)
    
    msg1 = await clb.message.answer("Введите текст для рассылки(включая теги<>) вместе с картинкой", reply_markup=user_keyboards.cancel_kb())
    await state.set_data(msg1)

@router.message(QueueState.queue_ask)
@user_banned_handler
async def queue_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    msg1 = await state.get_data()
    await bot.delete_message(chat_id=msg1.chat.id,message_id=msg1.message_id)
    await state.clear()
    await send_all(message, is_clb=True)


@router.message(Command("stats"))
@new_user_handler
async def stats_handler(message: Message, is_clb=False, **kwargs):
    if not is_clb:
        if (await UsersDatabase.get_value(message.from_user.id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return

    all_users = len(await UsersDatabase.get_all())
    all_banned_users = len(await UsersDatabase.get_all_banned())
    
    await message.edit_text(f"<b>Статистика</b>\n\nВсего пользователей: {all_users}\nЗабанено: {all_banned_users}",
                         parse_mode='HTML',reply_markup=user_keyboards.back_admin_panel_kb())


@router.callback_query(lambda clb: clb.data == "stats")
@user_banned_handler
async def state_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await stats_handler(clb.message, is_clb=True)



@router.message(Command("settings"))
@new_user_handler
@user_banned_handler
async def settings_handler(message: Message, is_clb=False, **kwargs):
    if not is_clb:
        if (await UsersDatabase.get_value(message.from_user.id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return

    
    await message.edit_text(f"<b>Настройки</b>",
                         parse_mode='HTML',reply_markup=user_keyboards.get_settings_kb())


@router.callback_query(lambda clb: clb.data == "settings")
@user_banned_handler
async def settings_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await settings_handler(clb.message, is_clb=True)


@router.message(Command("sub"))
@new_user_handler
@user_banned_handler
async def sub_handler(message: Message, is_clb=False, **kwargs):
    if not is_clb:
        if (await UsersDatabase.get_value(message.from_user.id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return


    await message.edit_text(f"<b>Проверять наличие подписки?</b>",
                         parse_mode='HTML',reply_markup=await user_keyboards.get_sub_kb())


@router.callback_query(lambda clb: clb.data == "sub")
@user_banned_handler
async def sub_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await sub_handler(clb.message, is_clb=True)

@router.callback_query(lambda clb: clb.data == "sub_1")
@user_banned_handler
async def sub_1_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await ConfigManager.set_value('sub',1)
    await clb.message.edit_text(f'Проверка включена\nУбедитесь что вставлена ссылка и id канала/чата, иначе бот будет работать некорректно.',reply_markup=await user_keyboards.get_sub_kb())

@router.callback_query(lambda clb: clb.data == "sub_0")
@user_banned_handler
async def sub_0_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await ConfigManager.set_value('sub',0)
    await clb.message.edit_text(f'Проверка выключена!',reply_markup=await user_keyboards.get_sub_kb())

@router.message(Command("channel"))
@new_user_handler
@user_banned_handler
async def channel_handler(message: Message, is_clb=False, **kwargs):
    if not is_clb:
        if (await UsersDatabase.get_value(message.from_user.id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return

    
    await message.edit_text(f"ID Канала:{await ConfigManager.get_value('channel')}\nСсылка:{await ConfigManager.get_value('link')}",
                         parse_mode='HTML',reply_markup=user_keyboards.get_channel_kb())

@router.callback_query(lambda clb: clb.data == "channel")
@user_banned_handler
async def channel_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await channel_handler(clb.message, is_clb=True)

class SetChannelState(StatesGroup):
    set_channel = State()

@router.callback_query(lambda clb: clb.data == "set_channel")
@user_banned_handler
async def set_channel_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(SetChannelState.set_channel)
    await clb.message.edit_text("Введите Id Канала.\nПример:-1001500435983", reply_markup=user_keyboards.get_channel_kb())

@router.message(SetChannelState.set_channel)
@user_banned_handler
async def queue_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    await state.clear()
     
    channel = message.text
    if '-' in channel:
        channel = -1 *int(channel[1:])
        await ConfigManager.set_value('channel',channel)
        await message.answer('ID установлен ',reply_markup=user_keyboards.get_channel_kb())
    else:
        await message.answer('Некорректный ID ',reply_markup=user_keyboards.get_channel_kb())

class SetLink(StatesGroup):
    set_link = State()

@router.callback_query(lambda clb: clb.data == "set_link")
@user_banned_handler
async def set_link_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(SetLink.set_link)
    await clb.message.edit_text("Введите ссылку на канал.\nПример: t.me/durov", reply_markup=user_keyboards.get_channel_kb())

@router.message(SetLink.set_link)
@user_banned_handler
async def queue_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    await state.clear()
    await ConfigManager.set_value('link',message.text)
    await message.answer('Link установлен ',reply_markup=user_keyboards.get_channel_kb())
    

@router.message(Command("request_len"))
@new_user_handler
@user_banned_handler
async def request_len_handler(message: Message, is_clb=False, **kwargs):
    if not is_clb:
        if (await UsersDatabase.get_value(message.from_user.id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return

    
    await message.edit_text(f"Максимальная длина запроса:\n{await ConfigManager.get_value('request_len')} символов",
                         parse_mode='HTML',reply_markup=user_keyboards.get_request_len_kb())

@router.callback_query(lambda clb: clb.data == "request_len")
@user_banned_handler
async def request_len_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await request_len_handler(clb.message, is_clb=True)  


class request_lenState(StatesGroup):
    request_len = State()

@router.callback_query(lambda clb: clb.data == "set_request_len")
@user_banned_handler
async def set_request_len_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(request_lenState.request_len)
    await clb.message.edit_text("Введите длину строки.\nРекомендуемое значение: 100-500", reply_markup=user_keyboards.get_request_len_kb())

@router.message(request_lenState.request_len)
@user_banned_handler
async def queue_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    await state.clear()

    try:
        request_len = int(message.text)
        if 1<=request_len<=4090:
            await ConfigManager.set_value('request_len',request_len)
            await message.answer('Длина строки установлена ',reply_markup=user_keyboards.get_request_len_kb())
        else:
            await message.answer('Значение должно быть от 1 до 4090. .',reply_markup=user_keyboards.get_request_len_kb())

    except:
        await message.answer('Вводите только числа.',reply_markup=user_keyboards.get_request_len_kb())

##

@router.message(Command("max_tokens"))
@new_user_handler
async def max_tokens_handler(message: Message, is_clb=False, **kwargs):
    if not is_clb:
        if (await UsersDatabase.get_value(message.from_user.id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return

    
    await message.edit_text(f"Длина ответа зависит от лимита токенов, сейчас стоит:\n{await ConfigManager.get_value('max_tokens')}",
                         parse_mode='HTML',reply_markup=user_keyboards.get_max_tokens_kb())

@router.callback_query(lambda clb: clb.data == "max_tokens")
@user_banned_handler
async def max_tokens_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await max_tokens_handler(clb.message, is_clb=True)  


class max_tokensState(StatesGroup):
    max_tokens = State()

@router.callback_query(lambda clb: clb.data == "set_max_tokens")
@user_banned_handler
async def set_max_tokens_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(max_tokensState.max_tokens)
    await clb.message.edit_text("Введите кол-во от 1000 до 3000.\nЧем больше - тем больше контекст, но меньше длина ответа.", reply_markup=user_keyboards.get_request_len_kb())

@router.message(max_tokensState.max_tokens)
@user_banned_handler
async def queue_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    await state.clear()

    try:
        max_tokens = int(message.text)
        if 100<= max_tokens <= 3000:

            await ConfigManager.set_value('max_tokens',max_tokens)
            await message.answer('Значение установлено!',reply_markup=user_keyboards.get_max_tokens_kb())
        else:
            await message.answer('Значение должно быть от 1000 до 3000.',reply_markup=user_keyboards.get_max_tokens_kb())

    except:
        await message.answer('Вводите только числа.',reply_markup=user_keyboards.get_max_tokens_kb())

##

@router.message(Command("limit_clear_msg"))
@new_user_handler
@user_banned_handler
async def limit_clear_msg_handler(message: Message, is_clb=False, **kwargs):
    if not is_clb:
        if (await UsersDatabase.get_value(message.from_user.id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return

    
    await message.edit_text(f"Кол-во старых сообщений, которые удаляются из начала буфера контекста. Сейчас стоит:\n{await ConfigManager.get_value('limit_clear_msg')}",
                         parse_mode='HTML',reply_markup=user_keyboards.get_limit_clear_msg_kb())

@router.callback_query(lambda clb: clb.data == "limit_clear_msg")
@user_banned_handler

async def limit_clear_msg_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await limit_clear_msg_handler(clb.message, is_clb=True)  


class limit_clear_msgState(StatesGroup):
    limit_clear_msg = State()

@router.callback_query(lambda clb: clb.data == "set_limit_clear_msg")
@user_banned_handler

async def set_limit_clear_msg_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(limit_clear_msgState.limit_clear_msg)
    await clb.message.edit_text("Введите кол-во.\nРекомендуемое значение: 1-5", reply_markup=user_keyboards.get_limit_clear_msg_kb())

@router.message(limit_clear_msgState.limit_clear_msg)
@user_banned_handler

async def queue_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    await state.clear()

    try:
        limit_clear_msg = int(message.text)
        if 1<=limit_clear_msg <= 10:
            await ConfigManager.set_value('limit_clear_msg',limit_clear_msg)
            await message.answer('Значение установлено!',reply_markup=user_keyboards.get_limit_clear_msg_kb())
        else:
            await message.answer('Значение должно быть от 1 до 10.',reply_markup=user_keyboards.get_limit_clear_msg_kb())

    except:
        await message.answer('Вводите только числа.',reply_markup=user_keyboards.get_limit_clear_msg_kb())

##

@router.message(Command("limit_msg"))
@new_user_handler
@user_banned_handler

async def limit_msg_handler(message: Message, is_clb=False, **kwargs):
    if not is_clb:
        if (await UsersDatabase.get_value(message.from_user.id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return

    
    await message.edit_text(f"Кол-во сообщений, хранимых в буфере контекста. Сейчас стоит:\n{await ConfigManager.get_value('limit_msg')}",
                         parse_mode='HTML',reply_markup=user_keyboards.get_limit_msg_kb())

@router.callback_query(lambda clb: clb.data == "limit_msg")
@user_banned_handler

async def limit_msg_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await limit_msg_handler(clb.message, is_clb=True)  


class limit_msgState(StatesGroup):
    limit_msg = State()

@router.callback_query(lambda clb: clb.data == "set_limit_msg")
@user_banned_handler

async def set_limit_msg_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(limit_msgState.limit_msg)
    await clb.message.edit_text(f"🚧Команда ни на что не влияет, буфер изменяется динамично({bot_version}). Кнопку уберу потом, может пригодится.\n\n\n .Введите кол-во хранимых сообщений.\nРекомендуемое значение: 10-20.\n Размер контекста влияет на скорость бота, при увеличении контекта, рекомендуется сокращать длины строк", reply_markup=user_keyboards.get_limit_msg_kb())

@router.message(limit_msgState.limit_msg)
@user_banned_handler

async def queue_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    await state.clear()

    try:
        limit_msg = int(message.text)
        if 1<=limit_msg<=25:
            await ConfigManager.set_value('limit_msg',limit_msg)
            await message.answer('Значение установлено!',reply_markup=user_keyboards.get_limit_msg_kb())
        else:
            await message.answer('Число должно быть от 1 до 25.',reply_markup=user_keyboards.get_limit_msg_kb())

    except:
        await message.answer('Вводите только числа.',reply_markup=user_keyboards.get_limit_msg_kb())


##

@router.callback_query(lambda clb: clb.data == "clear_all_context")
@user_banned_handler

async def clear_all_context_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await UsersDatabase.clear_all_context()
    await clb.message.edit_text("Контекст очищен🗑", reply_markup=user_keyboards.get_limit_msg_kb())

##
@router.callback_query(lambda clb: clb.data == "del_users")
@user_banned_handler

async def del_users_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await clb.message.edit_text("<b>Вы точно хотите очистить базу юзеров</b>❓❗️",parse_mode="HTML", reply_markup=user_keyboards.get_del_users_kb())

@router.callback_query(lambda clb: clb.data == "del_users_yes")
@user_banned_handler

async def del_users_yes_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await UsersDatabase.del_users()
    await clb.message.edit_text("База пользователей очищена🗑\nHere We Go Again.../start")

##

@router.message(Command("temperature"))
@new_user_handler
@user_banned_handler

async def temperature_handler(message: Message, is_clb=False, **kwargs):
    if not is_clb:
        if (await UsersDatabase.get_value(message.from_user.id, 'status')) != 1:
            await message.answer(
                "Для того, чтобы выполнить эту команду нужно иметь статус администратора.",
                parse_mode="HTML")
            return

    
    await message.edit_text(f"Параметр запроса влияющий на точность ответа. Сейчас стоит:\n{await ConfigManager.get_value('temperature')}",
                         parse_mode='HTML',reply_markup=user_keyboards.get_temperature_kb())

@router.callback_query(lambda clb: clb.data == "temperature")
@user_banned_handler

async def temperature_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await temperature_handler(clb.message, is_clb=True)  


class temperatureState(StatesGroup):
    temperature = State()

@router.callback_query(lambda clb: clb.data == "set_temperature")
@user_banned_handler

async def set_temperature_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(temperatureState.temperature)
    await clb.message.edit_text("Введите значение.\nДолжено быть задано в промежутке от 0 до 1. Где - 0 точная логика, 1 - кретивность\nРекомендуемое: 0.5", reply_markup=user_keyboards.get_temperature_kb())

@router.message(temperatureState.temperature)
@user_banned_handler

async def queue_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    await state.clear()

    try:
        temperature = float(message.text)
        if 0<=temperature<=1:
            await ConfigManager.set_value('temperature',temperature)
            await message.answer('Значение установлено!',reply_markup=user_keyboards.get_temperature_kb())
        else:
            await message.answer('Значение должно быть в промежутке от 0 до 1.',reply_markup=user_keyboards.get_temperature_kb())
    except:
        await message.answer('Вводите только числа.',reply_markup=user_keyboards.get_temperature_kb())



@router.message(Command("start"))
@new_user_handler
@user_banned_handler
async def start_handler(message: Message, is_clb=False, **kwargs):

    text = start_msg
    
    if is_clb:
        await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
    else:
        await message.delete()
    if start_photo =="":
        await message.answer(text = text, parse_mode="HTML")
    else:
        await message.answer_photo(photo =start_photo,caption=text,parse_mode="HTML" )


@router.callback_query(lambda clb: clb.data == 'start')
@new_user_handler
@user_banned_handler
async def start_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await start_handler(clb.message, is_clb=True)

#
@router.callback_query(lambda clb: clb.data == 'apikeys')
@new_user_handler
@user_banned_handler
async def apikeys_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    count = await TokensDatabase.get_count()
    text = f'Используется: <code>{count}</code>'
    await clb.message.edit_text(text=text,parse_mode="HTML",reply_markup=user_keyboards.get_apikeys_kb())

@router.callback_query(lambda clb: clb.data == 'del_apikeys')
@new_user_handler
@user_banned_handler
async def del_apikeys_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    text = ' <b>Вы точно хотите удалить ключи</b>❓❗️'
    await clb.message.edit_text(text=text,parse_mode="HTML",reply_markup=user_keyboards.get_del_apikeys_kb())

@router.callback_query(lambda clb: clb.data == 'del_apikeys_yes')
@new_user_handler
@user_banned_handler

async def del_apikeys_yes_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await TokensDatabase.delete_tokens()
    count = await TokensDatabase.get_count()
    text = f'<b>Ключи удалены</b>🗑\nИспользуется: <code>{count}</code>'
    await clb.message.edit_text(text=text,parse_mode="HTML",reply_markup=user_keyboards.get_apikeys_kb())


#

@router.callback_query(lambda clb: clb.data == 'current_page')
async def current_page_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await clb.answer()


@router.callback_query(lambda clb: clb.data.startswith('prompt_'))
@new_user_handler
@user_banned_handler
async def get_prompt_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_')
    prompt_id = int(data[1])
    name = await PromptsManager.get_value(prompt_id=prompt_id,key='name')
    view_mode = int(data[2])
    user_id = clb.from_user.id
    if view_mode ==0:
        body = await PromptsManager.get_value(prompt_id=prompt_id,key='body')
        await clb.message.edit_text(text=f'<b>Id:</b>{prompt_id}\n<b>Name:</b>{name}\n<b>Promt:</b>\n{body}',reply_markup=user_keyboards.get_prompt_kb(prompt_id),parse_mode="HTML")
    elif view_mode ==1:
        await UsersDatabase.set_value(key ='prompt_id',tg_id=user_id, new_value=prompt_id)
        await UsersDatabase.clear_context(tg_id=user_id)
        await clb.message.edit_text(f'<b>GPT теперь</b> {name}',parse_mode="HTML")
#


@router.message(Command("personality"))
@new_user_handler
@user_banned_handler
@pursue_subscription
async def personality_handler(message: Message, is_clb=False, **kwargs):
    count = 5

    current_page = 1
    view_mode = 1
    total_items = await PromptsManager.get_count_prompts()
    total_pages = (total_items + count - 1) // count

    prompts = await PromptsManager.get_prompts(count,current_page)
    
    text = '<b>🎭Личности:</b>'
    ikb = user_keyboards.get_prompts_kb(prompts,current_page,total_pages,view_mode)
 
    if is_clb:
        pass
    else:
        await message.delete()
        await message.answer(text=text,parse_mode="HTML",reply_markup=ikb)

@router.callback_query(lambda clb: clb.data.startswith('getprompts_'))
@new_user_handler
@user_banned_handler
async def get_prompts_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    count = 5
    
    data = clb.data.split('_')
    action = data[1]
    current_page = int(data[2])
    view_mode = int(data[3])
    total_items = await PromptsManager.get_count_prompts()
    total_pages = (total_items + count - 1) // count

    # Обработка событий кнопок пагинации
    if action == 'next':
        if current_page == total_pages:
            await clb.answer()
            return
        current_page += 1
    elif action == 'prev':
        if current_page == 1:
            await clb.answer()
            return
        current_page -= 1
    elif action == 'first':
        if current_page == 1:
            await clb.answer()
            return
        current_page = 1
    elif action == 'last':
        if current_page == total_pages:
            await clb.answer()
            return
        current_page = total_pages
    # Получите записи для новой страницы из базы данных
    prompts = await PromptsManager.get_prompts(count,current_page)
    
    text = '<b>🎭Личности:</b>'
    ikb = user_keyboards.get_prompts_kb(prompts,current_page,total_pages,view_mode)
 
    await clb.message.edit_text(text=text,parse_mode="HTML",reply_markup=ikb)

#
class AddPtromtState(StatesGroup):
    input_name = State()
    input_body = State()

@router.callback_query(lambda clb: clb.data == "add_prompt")
@new_user_handler

async def add_prompt_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state(AddPtromtState.input_name)
    await clb.message.answer("Введите название промпта",reply_markup=user_keyboards.cancel_prompts_kb())



@router.message(AddPtromtState.input_name)
@new_user_handler

async def queue_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    
    await state.set_state(AddPtromtState.input_body)
    await state.update_data(name = message.text)
   
    await message.answer(text='Введите текст промпта',reply_markup=user_keyboards.cancel_prompts_kb())
   
@router.message(AddPtromtState.input_body)
@new_user_handler
async def queue_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    
    data = await state.get_data()
    name = data['name']
    if len(name) > 20:
        await message.answer(text=f'Слишком длинное название, лимит 20',reply_markup=user_keyboards.get_admin_panel_kb())
        await state.clear()
        return

    body = message.text
    await state.clear()
    await PromptsManager.create_prompt(name,body)
    await message.answer(text=f'Промпт {name} добавлен!', reply_markup=user_keyboards.get_admin_panel_kb())
    
##

@router.callback_query(lambda clb: clb.data == "del_prompts_yes")

async def del_prompts_yes_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await PromptsManager.del_prompts()
    await clb.message.edit_text("Промпты удалены🗑\n",reply_markup=user_keyboards.get_admin_panel_kb())

@router.callback_query(lambda clb: clb.data == "del_prompts")

async def del_prompts_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    await clb.message.edit_text("<b>Вы точно хотите удалить все промпты</b>❓❗️",parse_mode="HTML", reply_markup=user_keyboards.get_del_prompts_kb())

@router.callback_query(lambda clb: clb.data.startswith("del_prompt_yes"))

async def del_prompt_yes_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    data = clb.data.split('_')
    prompt_id = int(data[3])
    await PromptsManager.del_prompt(prompt_id)
    
    await clb.message.edit_text("Промпт удален🗑\n",reply_markup=user_keyboards.get_admin_panel_kb())


@router.callback_query(lambda clb: clb.data.startswith("del_prompt"))

async def del_prompt_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    data = clb.data.split('_')
    prompt_id = int(data[2])
    await clb.message.edit_text("<b>Удалить промпт</b>❓❗️",parse_mode="HTML", reply_markup=user_keyboards.get_del_prompt_kb(prompt_id))
    
@router.message(Command("context"))
@new_user_handler
@user_banned_handler
@pursue_subscription
async def context_handler(message: Message, is_clb=False, **kwargs):
    # msg = await message.answer(text="💬")
    request ='Суммируй все о чем мы говорили в одно предложение'
    user_id = message.from_user.id
    # response = await openai_manager.make_request(request,user_id,0,0)
    context_status = await UsersDatabase.get_value(key='context_status',tg_id=user_id)
    if context_status ==1:
        text ='<b>Контекст включен</b> ✅'
    else:
        text ='<b>Контекст выключен</b> ❌'
    
    await message.delete()
    await message.answer(text=f'{text}:\n\n<b>Забудем о чем говорили?</b>',parse_mode='HTML',reply_markup=user_keyboards.get_context_kb(context_status))
    
@router.callback_query(lambda clb: clb.data =="del_context")
@user_banned_handler
async def del_context_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    message2 = await clb.message.answer_sticker(sticker='CAACAgIAAxkBAAIq6mUvdka3_LHjW9nY4oHsZBSAKPlBAAJnFgACSQfZSYmwXND1I7cOMAQ')
    await asyncio.sleep(3)
    user_id = clb.from_user.id
    await UsersDatabase.clear_context(tg_id=user_id)
    await message2.delete()
    await clb.message.edit_text(text = '<b>Ничего</b> не помню, <b>все</b> забыл 😶‍🌫️..',parse_mode="HTML")



@router.callback_query(lambda clb: clb.data.startswith("context_status"))
@user_banned_handler
async def context_status_callback_handler(clb: CallbackQuery, state: FSMContext, **kwargs):
    user_id = clb.from_user.id
    data = clb.data.split('_')
    context_status = int(data[2])
    text = ''
    if context_status == 0:
        context_status = 1
        text = "Контекст включен ✅"
    elif context_status==1:
        context_status= 0
        text = "Контекст выключен ❌"
    
    await UsersDatabase.set_value(key="context_status",tg_id=user_id,new_value=context_status)
    
    await clb.message.edit_text(text = text,reply_markup=user_keyboards.get_context_kb(context_status))
#
@router.message(Command("info"))
@new_user_handler
@user_banned_handler
async def info_handler(message: Message, is_clb=False, **kwargs):
    await message.delete()
    await message.answer(info_msg)
#
@router.message(Command("account"))
@new_user_handler
@user_banned_handler
@pursue_subscription
async def account_handler(message: Message, is_clb=False, **kwargs):
    user_id = message.from_user.id
    context_status = await UsersDatabase.get_value(key='context_status',tg_id=user_id)
    if context_status ==1:
        context_status =='Включен'
    else:
        context_status =='Выключен'
    prompt_id = await UsersDatabase.get_value(key='prompt_id', tg_id=user_id)
    name = await PromptsManager.get_value(key ='name', prompt_id=prompt_id)
    
    await message.delete()
    await message.answer(f"""<b>Твой ID:</b> <code>{user_id}</code>
<b>Выбранная личность</b>:
{name}
<b></b>""",parse_mode="HTML")

@router.message(F.text[0] != '/')
@new_user_handler
@user_banned_handler
@pursue_subscription
async def openai_handler(msg: Message, is_clb=False, **kwargs):
    user_id = msg.from_user.id
    
    request = msg.text
    msg2 = await msg.answer(text="💬")
    bad_trys = 0
    context_status = await UsersDatabase.get_value(key='context_status',tg_id=user_id)
    requests_count = await UsersDatabase.get_value(key='requests_count',tg_id=user_id)
    if requests_count == 50:
        await bot.send_message(chat_id=super_admin,text=f'user {user_id} сделал 50 запросов 👀')
    response = await openai_manager.make_request(request,user_id,bad_trys,context_status,requests_count)
    if len(response)> 4000:
            responses = [response[i:i +4000] for i in range(0,len(response),4000)]
            for i,response in enumerate(responses):
                if i ==0:
                    await msg2.edit_text(response)
                else:
                    text = 'Продолжение:\n\n'+response
                    await msg.answer(text=text)
                await asyncio.sleep(1)
    else:
        await msg2.edit_text(response)

@router.message()
async def photo_handler(msg: Message, is_clb=False, **kwargs):
    user_id = msg.from_user.id
    await msg.answer(text=msg.photo[-1].file_id)
