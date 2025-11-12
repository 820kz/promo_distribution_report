#%%
import requests
import logging
import os
import MagnumDB
from dotenv import load_dotenv
import time
import sys

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

db = MagnumDB.DBConnection(**db_promo_tabel)
# получить актуальный promo_id
sql = """SELECT 
            min(promo_id) 
        FROM promo_tabel.promo_actions 
        WHERE 1 = 1 
            AND is_arc = 0 
            AND date_start > CURRENT_DATE + INTERVAL '7 days'
            AND date_start < CURRENT_DATE + INTERVAL '21 days' 
        """
PROMO_ID = db.select(sql)['min'][0]
db.close()

USERNAME = 'KUDASHKINA'
DEPLOY_SRVR_IP = os.environ['DEPLOY_SRVR_IP']
SERVICE_PORT = os.environ['SERVICE_PORT']
ROW_LIMIT = 100
endpoints = ['promo_tabel_report', 'mc_report', 'dmr_report', 'oukd_report', 'od_report', 'od_wo_prices_report', 'promo_places_report', 'promo_prices_report', 'promo_tabel_pivots_report', 'promo_catalogs_report', 'promo_places_import_report']

def test_endpoint(endpoint):
    """
    Шаблон для получения отчета
    """
    start_time = time.time()
    url = f"http://{DEPLOY_SRVR_IP}:{SERVICE_PORT}/{endpoint}?promo_id={PROMO_ID}&user_name={USERNAME}&limit={ROW_LIMIT}"
    response = requests.get(url)
    elapsed_time = time.time() - start_time
    if response.status_code == 200:
        logging.info(f"Endpoint {endpoint} - Succeed in {elapsed_time:.4f} - {response.status_code}.")
        return 0
    else:
        logging.warning(f"Endpoint {endpoint} - Failed in {elapsed_time:.4f} - {response.text}.") 
        return 1

# Пройтись по всем отчетам и вывести сведения в консоль
error_status = 0
for endpoint in endpoints:
    error_status += test_endpoint(endpoint)

if error_status > 0:
    logging.info("Something went wrong.")
    sys.exit(1)
else:
    logging.info("All passed.")
# %%
