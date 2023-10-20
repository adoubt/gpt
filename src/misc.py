from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


token="5947463331:AAFjoFVFNTzeghEzY8mB9m_RznEnwbov7ms"
super_admin = "436839651"
password = '1234' # /set_admin{password}



bot_id = token.split(":",1)[0]
bot = Bot(token)
dp = Dispatcher(storage=MemoryStorage())