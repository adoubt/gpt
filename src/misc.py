from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


token="594746333:AAFjoFVFNTzeghEzY8mB9m_RznEnwbov7m"
super_admin = "43683965"# not required but you can set your id
password = '1234' # /set_admin{password}



bot_id = token.split(":",1)[0] # temp-fix: bot still have some buds with admin rules in callback func.. 
bot = Bot(token)
dp = Dispatcher(storage=MemoryStorage())