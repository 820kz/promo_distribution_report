#%%imports
import MagnumDB
import os
import pandas as pd
import io
import time

#%%read params

from dotenv import load_dotenv

try:
    load_dotenv('.env')
except:
    pass

#declare db connections
db_promo_tabel = {
    'db_ip':os.environ['TABEL_IP'],
    'db_port':os.environ['TABEL_PORT'],
    'db_service':os.environ['TABEL_SERVICE'],
    'db_login':os.environ['TABEL_LOGIN'],
    'db_pass':os.environ['TABEL_PASS'] 
}

def get_mc_data(promo_id, user_name, limit):

    if limit != None:
        lim_row = f'LIMIT {limit}'
    else:
        lim_row = ''

    start_time = time.time()
    select_promos_query  = open("custom_reports/mc_query.sql", encoding='utf-8', mode="r").read()
    db = MagnumDB.DBConnection(**db_promo_tabel)
    data = db.select(select_promos_query%(promo_id,
                                          user_name,
                                          user_name,
                                          user_name,
                                          lim_row
                                          )
                                          )
    db.close()
    # rename cols
    data = data.rename(columns={'date_start':'Дата начала'
                    , 'date_end':'Дата окончания'
                    , 'source_product_id': 'Код товара в Спрут'
                    , 'shop_code': 'Код магазина'
                    , 'promo_bonus': 'Акционный бонус от поставщика, %'
                    , 'dmp_id': 'ДМП'
                    , 'purchaise_price_wvat': 'Закупочная цена с НДС, тенге'
                    , 'promo_discount': 'Скидка для покупателя, %'
                    , 'promo_price_wvat': 'Акционная цена с НДС, тенге'
                    , 'barcode': 'Штрих-код'
                    , 'rn': 'РН'
                    , 'brand': 'Торговая марка'
                    , 'supllier_name': 'Поставщик'
                    , 'shop_name': 'Наименование магазина'
                    , 'pzpt': 'ПЗПТ'
                })
    # удалить мусорные символы
    data['ДМП'] = data['ДМП'].apply(lambda x: x.strip())
    data = data.loc[data['ДМП'].str.upper() != 'НЕ УЧАСТВУЕТ'].reset_index(drop=True)

    # to binary flow
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    data.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.close()
    output.seek(0)

    elapsed_time = time.time() - start_time
    
    return output
#%%
