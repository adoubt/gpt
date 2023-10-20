import abc

import aiosqlite
from typing import Any


class TokensDatabase:
    
    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/tokens.db") as db:
            async with db.execute(
                    f'CREATE TABLE IF NOT EXISTS tokens(apikey STRING PRIMARY KEY UNIQUE, balance INTEGER, UNIQUE ("apikey") ON CONFLICT IGNORE)') as cursor:
                pass
    
    @classmethod
    async def get_all(cls):
        async with aiosqlite.connect("src/databases/tokens.db") as db:
            async with db.execute(f'SELECT * FROM tokens') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result[0]
    @classmethod
    async def get_count(cls):
        async with aiosqlite.connect("src/databases/tokens.db") as db:
            async with db.execute(f'SELECT COUNT(*) FROM tokens') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result[0][0]
        
    @classmethod
    async def create_token(cls, key: str):
        async with aiosqlite.connect("src/databases/tokens.db") as db:
            await db.execute(f'INSERT INTO tokens ("apikey", "balance") VALUES (?,?)',(key,0))
            await db.commit()
    
    @classmethod
    async def delete_token(cls,key):
        async with aiosqlite.connect("src/databases/tokens.db") as db:
            await db.execute(f'DELETE FROM tokens WHERE apikey = "{key}"')
            await db.commit()

    
    @classmethod
    async def get_rand_key(cls: int):
        async with aiosqlite.connect("src/databases/tokens.db") as db:
            async with db.execute('SELECT apikey FROM tokens ORDER BY RANDOM() LIMIT 1') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
    @classmethod
    async def delete_tokens(cls):
        async with aiosqlite.connect("src/databases/tokens.db") as db:
            await db.execute(f'DELETE FROM tokens')
            await db.commit()
    # @classmethod
    # async def get_all(cls):
    #     async with aiosqlite.connect("src/databases/tokens.db") as db:
    #         async with db.execute(f'SELECT * FROM tokens') as cursor:
    #             result = await cursor.fetchall()
    #             if not result:
    #                 return []
    #             return result
    