import openai
import tiktoken

from src.methods.database.config_manager import ConfigManager,PromptsManager
from src.methods.database.tokens_manager import TokensDatabase
from src.methods.database.users_manager import UsersDatabase
from loguru import logger

#set encoding for tiktoken
encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

async def make_request(request: str,user_id,bad_trys,context_status,requests_count):
    
    
    
    prompt_id = await UsersDatabase.get_value(key='prompt_id',tg_id=user_id)
    if prompt_id == 0:
        prompt=''
    else:
        prompt = await PromptsManager.get_value(key ='body',prompt_id=prompt_id)
    if prompt == -1:
        prompt ==''
        await UsersDatabase.set_value(tg_id=user_id,key='prompt_id',new_value=0)
    messages = [{"role": "system", "content": 'prompt'}]

    request_len = await ConfigManager.get_value('request_len')
    if len(request) > request_len:
        return f"Слишком длинный запрос. Максимум {request_len}"
    
    count = await TokensDatabase.get_count()
    if count==0:
        logger.info(f"[Admin] Токены закончились")
        return('Нужны новые токены...')
    
    openai.api_key = await TokensDatabase.get_rand_key()

    max_tokens = await ConfigManager.get_value('max_tokens')
    
    # limit_msg = await ConfigManager.get_value('limit_msg')
    limit_clear_msg = await ConfigManager.get_value('limit_clear_msg')
    temperature = await ConfigManager.get_value('temperature')
    

    messages[0] = {"role": "system", "content": str(prompt)}
    messages_2 = messages[::]
    if context_status == 1:
        context = await UsersDatabase.get_value(user_id,'context')
        if context !='' or context !=' ':
            
            print(len(encoding.encode(context+request)))
            print("---")

            rows = context.split('\n')
            
            while len(encoding.encode(context+request+prompt)) >max_tokens:
                rows = rows[limit_clear_msg:]
                context = '\n'.join(rows)
            # if len(rows) >= limit_msg:
            #     rows = rows[limit_clear_msg+len(rows)-limit_msg:]
            #     context = '\n'.join(rows)
            print(len(encoding.encode(context+request)))
            for row in rows[:-1]:
                if row[:4]=='user':
                    messages_2.append({"role": "user","content": row[5:]})
                elif row[:5]==' user':
                    messages_2.append({"role": "user","content": row[6:]})
                elif row[:9]=='assistant':
                    messages_2.append({"role": "assistant","content": row[10:]})
                else:
                    continue
        
    
    messages_2.append({"role": "user","content": request})


    try:
        completion =  await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages_2,
            temperature=temperature,
            # max_tokens=1900,
            top_p=0.9,
            frequency_penalty=0,
            presence_penalty=0
        )
        response = completion.choices[0].message.content
        
        if context_status == 1:
            
            context+=(f'user:{request}\n')
            new_context = response.replace("\n"," ")
            context+=(f'assistant:{new_context}\n')
            await UsersDatabase.set_value(user_id,'context',context)
        await UsersDatabase.set_value(tg_id=user_id,key='requests_count',new_value=requests_count+1)
        return response
    
    except Exception as e:
        print(e)
        if e.http_status:
            if e.http_status == 502:
                #Cloudframe душит
                pass

            elif e.http_status== 401:
                #Incorrect APIkey
                await TokensDatabase.delete_token(openai.api_key)
                logger.info(f"[Admin] Токен удален: {openai.api_key} Осталось: {count}") 
                pass
            if e.http_status == None:
                logger.info(f"[Admin] Неизвестная ошибка, мб Openai ругается: {openai.api_key} Осталось: {count}") 
                return 'Повторите позже 🤒'
        elif e.error:
            if e.error== 'context_length_exceeded':
                return "Слишком длинный запрос"
            
        bad_trys+=1
        if bad_trys <=2: 
            return await make_request(request,user_id,bad_trys,context_status,requests_count)
        else:
            logger.info(f"[Admin] Не удается получить ответ от OpenAI")
            return '🤒 Повторите позже!'
            
        
        
      
        
        
