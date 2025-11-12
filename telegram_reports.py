#%%
import requests
import os
import MagnumDB
import time
from dotenv import load_dotenv

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

try:
    load_dotenv('.env')
except:
    pass

db_promo_tabel = {
    'db_ip':os.environ['TABEL_IP'],
    'db_port':os.environ['TABEL_PORT'],
    'db_service':os.environ['TABEL_SERVICE'],
    'db_login':os.environ['TABEL_LOGIN'],
    'db_pass':os.environ['TABEL_PASS'] 
}

TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
TG_CHAT_ID = os.environ['TG_CHAT_ID']
TG_TOPIC_ID = os.environ['TG_TOPIC_ID']

distribution_port = int(os.environ['DISTRIBUTION_PORT'])
#%%
def send_distribution_status(token:str, chat_id:str, topic_id:int, db_params, promo_id, status):
    if status != -1:
        if promo_id != None:
            db = MagnumDB.DBConnection(**db_params)
            sql = """
                select distinct on (promo_name, creation_time)
                    promo_name 
                from promo_tabel.promo_actions
                where promo_id = %s
                order by promo_name, creation_time desc"""%(promo_id)
            table = db.select(sql)
            db.close()
        else:
            table = ''

        promo_name = table['promo_name'][0]

        if status == 0:
            text = '🚀 Запущено распределение "' + promo_name + '"'
        elif status == 1:
            text = '✅ Завершено распределение "' + promo_name + '"'
        elif status == 2:
            text = '❌ Сбой распределения "' + promo_name + '"'
        else:
            text = None

        if status != -1:
            data = {
                'chat_id': chat_id, 
                'message_thread_id': topic_id,
                'text': text
            }
            response = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', json=data)
            return response.json()

def get_service_status(port):
    requests.packages.urllib3.util.HAS_IPV6 = False
    url = f'http://10.70.10.2:{port}/status'
    response = requests.get(url).json()
    status = int(response['status'])
    promo_id = int(response['promo_id']) if 'promo_id' in response else None
    return promo_id, status

# Инициализация предыдущего статуса
is_restarted = 0
prev_status = None
prev_promo_id = None

logging.info('Status monitoring started.')
while True:
    try:
        # Получение текущего статуса сервиса
        promo_id, status = get_service_status(distribution_port)

        if prev_promo_id is not None and status == -1:
            promo_id = prev_promo_id

        # Если статус изменился, отправляем отчет в Telegram
        if status != prev_status and is_restarted == 1:
            logging.info('Status has changed. Sending report to Telegram.')
            if prev_status == 0 and status == -1:
                status = 2
            send_distribution_status(token = TG_BOT_TOKEN
                            , chat_id = TG_CHAT_ID
                            , topic_id = TG_TOPIC_ID
                            , db_params = db_promo_tabel
                            , promo_id = prev_promo_id if status == 2 else promo_id
                            , status = status)

        # Обновление предыдущего статуса
        prev_status = status
        prev_promo_id = promo_id
        is_restarted = 1

        # Ожидание 20 секунд перед следующей проверкой
        time.sleep(20)
    except Exception as e:
        logging.info(str(e))
        time.sleep(20)
 