import abc
import json
from typing import Any
# from aiofiles import open as aio_open
import aiosqlite


class ConfigManager:

    @classmethod
    async def get_value(cls, key: Any):
        async with aiosqlite.connect("src/databases/config.db") as db:
            async with db.execute(f'SELECT {key} FROM config LIMIT 1') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
    
    @classmethod
    async def set_value(cls, key: Any, new_value: Any):
        async with aiosqlite.connect("src/databases/config.db") as db:
            if type(key) is str:
                await db.execute(f'UPDATE config SET {key}=?',(new_value,))
            else:
                await db.execute(f'UPDATE config SET {key}={new_value} ')
            await db.commit()

class PromptsManager:
    
    @classmethod
    async def get_value(cls, prompt_id: int, key: str):
        async with aiosqlite.connect("src/databases/config.db") as db:
            async with db.execute(f'SELECT {key} FROM prompts WHERE id = {prompt_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]

    @classmethod
    async def set_value(cls, prompt_id: int, key: Any, new_value: Any):
        async with aiosqlite.connect("src/databases/config.db") as db:
            if type(key) is int:
                await db.execute(f'UPDATE prompts SET {key}={new_value} WHERE id={prompt_id}')
            else:
                await db.execute(f'UPDATE prompts SET {key}=? WHERE id={prompt_id}',(new_value,))
            await db.commit()
            
    @classmethod    
    async def get_prompts(cls,count: int,page: int) -> list:
         async with aiosqlite.connect("src/databases/config.db") as db:
            async with db.execute(f'SELECT * FROM prompts ORDER BY id LIMIT {count} OFFSET {count*(page-1)}') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result 
    @classmethod    
    async def get_count_prompts(cls)->int:
         async with aiosqlite.connect("src/databases/config.db") as db:
            async with db.execute(f'SELECT COUNT(*) FROM prompts') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
            
    @classmethod
    async def get_prompt(cls, prompt_id :int) -> str:
        async with aiosqlite.connect("src/databases/config.db") as db:
            async with db.execute(f'SELECT body FROM prompts WHERE id = {prompt_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0] 
    @classmethod
    async def create_prompt(cls, name: str,body : str):
        async with aiosqlite.connect("src/databases/config.db") as db:
            await db.execute(f'INSERT INTO prompts ("name", "body") VALUES (?,?)',(name,body))
            await db.commit()
    @classmethod
    async def del_prompts(cls):
        async with aiosqlite.connect("src/databases/config.db") as db:
            await db.execute(f'DELETE FROM prompts WHERE id != 1')
            await db.commit()
    @classmethod
    async def del_prompt(cls,prompt_id):
        if prompt_id == 1:
            return 
        
        async with aiosqlite.connect("src/databases/config.db") as db:
            await db.execute(f'DELETE FROM prompts WHERE id = {prompt_id}')
            await db.commit()





#CREATE TABLE config (prompt TEXT,sub INTEGER,channel INTEGER,link TEXT,max_tokens INTEGER,request_len INTEGER,limit_msg INTEGER,limit_clear_msg INTEGER,temperature REAL)
# INSERT INTO config("prompt","sub","channel","link","max_tokens","request_len","limit_clear_msg", "limit_msg","temperature") VALUES (" ",0,-1001755740642,"https://t.me/mycumsock",100,255,3,9,0.4)

# class ConfigManager:

#     @classmethod
#     async def get(self) -> dict:
#         async with aio_open("src/databases/config.json", mode='r') as config_file:
#             content = await config_file.read()
#             config_json = json.loads(content)
#         return config_json

#     @classmethod
#     async def get_value(self, key: str) -> Any:
#         config = await self.get()
#         return config.get(key, None)

#     @classmethod
#     async def set_value(self, key: str, value: Any) -> None:
#         async with aio_open("src/databases/config.json", mode='r') as config_file:
#             async for line in config_file:
#                 config_json = json.loads(line)

#         config_json[key] = value

#         async with aio_open("src/databases/config.json", mode='w') as config_file:
#             await config_file.write(json.dumps(config_json))
