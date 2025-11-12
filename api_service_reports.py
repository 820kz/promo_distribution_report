#%%imports
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from custom_reports.promo_tabel_request import get_promo_tabel_data
from custom_reports.promo_places_request import get_promo_places_data
from custom_reports.promo_prices_request import get_promo_prices_data
from custom_reports.promo_tabel_pivots_request import get_promo_tabel_pivots_data
from custom_reports.promo_tabel_catalogs_request import get_promo_catalogs_data
from custom_reports.mc_request import get_mc_data
from custom_reports.dmr_request import get_dmr_data
from custom_reports.oukd_request import get_oukd_data
from custom_reports.od_request import get_od_data
from custom_reports.od_wo_prices_request import get_od_wo_prices_data
from custom_reports.promo_places_import_report import get_promo_places_import_data
import time
import uuid
import MagnumDB
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from typing import Optional

import logging
logging.basicConfig(
    level=logging.DEBUG,
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

def execute_logs(conn, sql):
    db = MagnumDB.DBConnection(**conn)
    db.execute(sql)
    db.close()

execute_logs(db_promo_tabel, '''CREATE TABLE IF NOT EXISTS promo_tabel.report_logs (
                                id TEXT PRIMARY KEY,
                                username TEXT,
                                report_type TEXT,
                                promo_id INTEGER,
                                file_size_mb REAL,
                                date_start TIMESTAMP,
                                date_end TIMESTAMP,
                                status TEXT
                                )''')

app = FastAPI()
executor = ThreadPoolExecutor()

async def get_data_async(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)

def create_report_endpoint(report_type: str, data_func, file_format):
    @app.get(f"/{report_type}_report")
    async def report_xlsx(promo_id: str, user_name: str, limit: Optional[int] = None):
        id = uuid.uuid4() # идентификатор
        if limit == None: # результаты теста в логи не выводить
            logging.info(f'ID: {id} | USER: {user_name} | PROMO ID: {promo_id} | TYPE: {report_type} report | Loading...')
        start_time = time.time()
        try:
            dmp_results = await get_data_async(data_func, promo_id, user_name, limit)
            elapsed_time = time.time() - start_time # окончание выгрузки
            file_size_mb = dmp_results.getbuffer().nbytes / (1024 * 1024) # размер файла
            response = StreamingResponse(
                dmp_results,
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                #headers={'Content-Disposition': f'attachment; filename={report_type}_report_{user_name}.{file_format}'})
                headers={'Content-Disposition': f'attachment; filename={promo_id.replace(",", "_")}_{report_type}_report_{user_name}.{file_format}'})
            # успешная выгрузка
            if limit == None: # результаты теста в базу не кидать
                execute_logs(db_promo_tabel,"INSERT INTO promo_tabel.report_logs (id, username, report_type, promo_id, file_size_mb, date_start, date_end, status) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %\
                    (str(id)
                    , user_name.upper()
                    , report_type.upper()
                    , promo_id
                    , float(file_size_mb)
                    , (datetime.fromtimestamp(start_time) + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
                    , (datetime.fromtimestamp(time.time()) + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
                    , "Success"))
                logging.info(f'ID: {id} | USER: {user_name} | PROMO ID: {promo_id} | TYPE: {report_type} report | Done in {elapsed_time:.4f} sec.')
            return response
        except Exception as e:
            # неуспешная выгрузка
            if limit == None: # результаты теста в базу не кидать
                execute_logs(db_promo_tabel,"INSERT INTO promo_tabel.report_logs (id, username, report_type, promo_id, file_size_mb, date_start, date_end, status) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %\
                    (str(id)
                    , user_name.upper()
                    , report_type.upper()
                    , promo_id
                    , float(0)
                    , (datetime.fromtimestamp(start_time) + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
                    , (datetime.fromtimestamp(time.time()) + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
                    , "Failed"))
                logging.error(f'ID: {id} | USER: {user_name} | PROMO ID: {promo_id} | TYPE: {report_type} report | Error: {str(e)}')
            return JSONResponse(status_code=500, content=f"An error occurred: {str(e)}")

# основной отчет
# http://10.70.10.2:10511/promo_tabel_report?promo_id=113&user_name=KAN
create_report_endpoint('promo_tabel', get_promo_tabel_data, 'xlsx')

# отчет по МС
# http://10.70.10.2:10511/mc_report?promo_id=113&user_name=KAN
create_report_endpoint('mc', get_mc_data, 'xlsx')

# отчет по ДМР
# http://10.70.10.2:10511/dmr_report?promo_id=113&user_name=KAN
create_report_endpoint('dmr', get_dmr_data, 'xlsx')

# отчет по ОУКД
# http://10.70.10.2:10511/oukd_report?promo_id=113&user_name=KAN
create_report_endpoint('oukd', get_oukd_data, 'zip')

# отчет по ОД
# http://10.70.10.2:10511/od_report?promo_id=113&user_name=KAN
create_report_endpoint('od', get_od_data, 'zip')

# отчет по ОД без цен
# http://10.70.10.2:10511/od_report?promo_id=113&user_name=KAN
create_report_endpoint('od_wo_prices', get_od_wo_prices_data, 'zip')

# отчет по промо-местам
# http://10.70.10.2:10511/promo_places_report?promo_id=113&user_name=KAN
create_report_endpoint('promo_places', get_promo_places_data, 'xlsx')

# отчет по промо-ценам
# http://10.70.10.2:10511/promo_prices_report?promo_id=113&user_name=KAN
create_report_endpoint('promo_prices', get_promo_prices_data, 'xlsx')

# отчет по сводным табеля
# http://10.70.10.2:10511/promo_tabel_pivots_report?promo_id=115&user_name=KUDASHKINA
create_report_endpoint('promo_tabel_pivots', get_promo_tabel_pivots_data, 'xlsx')

# основной отчет
# http://10.70.10.2:10511/promo_catalogs_report?promo_id=285&user_name=KAN
create_report_endpoint('promo_catalogs', get_promo_catalogs_data, 'xlsx')

# отчет по типорту промо-местам
# http://10.70.10.2:10511/promo_catalogs_report?promo_id=285&user_name=KAN
create_report_endpoint('promo_places_import', get_promo_places_import_data, 'xlsx')

# #%%
# if __name__ == "__main__":
#     import nest_asyncio
#     import uvicorn
#     nest_asyncio.apply()
#     uvicorn.run(app, host="0.0.0.0", port=10500)
