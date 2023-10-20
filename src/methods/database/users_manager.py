import abc

import aiosqlite
from typing import Any


class UsersDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(
                    f'CREATE TABLE IF NOT EXISTS users(tg_id INTEGER PRIMARY KEY, balance INTEGER, is_banned INTEGER, status INTEGER, context TEXT,prompt_id INTEGER, context_status INTEGER, requests_count INTEGER)') as cursor:
                pass

    @classmethod
    async def get_all(cls):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT * FROM users') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result

    @classmethod
    async def get_all_banned(cls):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT * FROM users WHERE is_banned=1') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result

    @classmethod
    async def get_user(cls, tg_id: int):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT * FROM users WHERE tg_id = {tg_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]

    @classmethod
    async def create_user(cls, tg_id: int):
        async with aiosqlite.connect("src/databases/users.db") as db:
            await db.execute(f'INSERT INTO users("tg_id", "balance", "is_banned", "status", "context","prompt_id","context_status","requests_count") VALUES ({tg_id}, 0, 0, 0, "", 1, 1,0)')
            await db.commit()

    @classmethod
    async def get_value(cls, tg_id: int, key: Any):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT {key} FROM users WHERE tg_id = {tg_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]

    @classmethod
    async def set_value(cls, tg_id: int, key: Any, new_value: Any):
        async with aiosqlite.connect("src/databases/users.db") as db:
            if type(key) is int:
                await db.execute(f'UPDATE users SET {key}={new_value} WHERE tg_id={tg_id}')
            else:
                await db.execute(f'UPDATE users SET {key}=? WHERE tg_id={tg_id}',(new_value,))
            await db.commit()

    @classmethod        
    async def clear_all_context(cls):
        async with aiosqlite.connect("src/databases/users.db") as db:
            
            await db.execute(f'UPDATE users SET context=""')
            await db.commit()
    @classmethod        
    async def clear_context(cls,tg_id:int):
        async with aiosqlite.connect("src/databases/users.db") as db:
            
            await db.execute(f'UPDATE users SET context="" WHERE tg_id ={tg_id}')
            await db.commit()


    @classmethod        
    async def del_users(cls):
        async with aiosqlite.connect("src/databases/users.db") as db:
            
            await db.execute(f'DELETE from users')
            await db.commit()

    @classmethod
    async def add_points(cls, tg_id: int, points: int):
        await cls.set_value(tg_id, 'balance', (await cls.get_value(tg_id, 'balance')) + points)

    @classmethod
    async def is_banned(cls, tg_id: int):
        return await cls.get_value(tg_id, 'is_banned')

    @classmethod
    async def is_admin(cls, tg_id: int):
        return (await cls.get_value(tg_id, 'status')) == 1
    
    
# INSERT INTO users("tg_id", "balance", "is_banned", "status", "context") VALUES ({tg_id}, 0, 0, 0, "")'
# 'CREATE TABLE prompts(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT, body TEXT)')