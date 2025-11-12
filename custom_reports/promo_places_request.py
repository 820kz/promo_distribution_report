#%%imports
import MagnumDB
import os
import pandas as pd
import io
import time
import re
from numpy import where

pd.set_option("display.max_columns", None)
pd.options.display.float_format = '{:,}'.format

#%%read params
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        #logging.FileHandler("outputs/debug.log"),
        logging.StreamHandler()
    ]
)

from dotenv import load_dotenv

try:
    load_dotenv('.env')
except:
    pass

#declare db connections
db_promo_tabel = {
    'db_ip': os.environ['TABEL_IP'],
    'db_port':os.environ['TABEL_PORT'],
    'db_service':os.environ['TABEL_SERVICE'],
    'db_login':os.environ['TABEL_LOGIN'],
    'db_pass':os.environ['TABEL_PASS'] 
}

db_dwh = {
    'db_ip':os.environ['DWH_IP'],
    'db_port':os.environ['DWH_PORT'],
    'db_service':os.environ['DWH_SERVICE'],
    'db_login':os.environ['DWH_LOGIN'],
    'db_pass':os.environ['DWH_PASS'] 
}

#%%
# promo_id = 113

# user_name = 'KAN'

def get_promo_places_data(promo_id, user_name, limit):

    if limit != None:
        lim_row = f'LIMIT {limit}'
    else:
        lim_row = ''
    
    # Все промо-места из текущего promo_id
    select_tabel_query  = open("custom_reports/promo_places_query_tabel_main.sql", encoding='utf-8', mode="r").read()
    db = MagnumDB.DBConnection(**db_promo_tabel)
    tabel_data = db.select(select_tabel_query%(promo_id, lim_row))
    db.close()

    # Группы доступные пользователю
    select_tabel_groups_query  = open("custom_reports/promo_places_query_tabel_groups.sql", encoding='utf-8', mode="r").read()
    db = MagnumDB.DBConnection(**db_promo_tabel)
    tabel_groups = db.select(select_tabel_groups_query%(user_name))
    db.close()

    # Регионы доступные пользователю
    select_tabel_regions_query  = open("custom_reports/promo_places_query_tabel_regions.sql", encoding='utf-8', mode="r").read()
    db = MagnumDB.DBConnection(**db_promo_tabel)
    tabel_regions = db.select(select_tabel_regions_query%(user_name))
    db.close()

    # Форматы доступные пользователю
    select_tabel_formats_query  = open("custom_reports/promo_places_query_tabel_formats.sql", encoding='utf-8', mode="r").read()
    db = MagnumDB.DBConnection(**db_promo_tabel)
    tabel_formats = db.select(select_tabel_formats_query%(user_name))
    db.close()

    # Промо-места из ДВХ
    select_dwh_query  = open("custom_reports/promo_places_query_dwh.sql", encoding='utf-8', mode="r").read()
    db = MagnumDB.DBConnection(**db_dwh)
    dwh_data = db.select(select_dwh_query%(tabel_data['dmp_binding_name'].unique()[0], lim_row))
    db.close()

    # Объединение данных из ДВХ
    rez = pd.merge(tabel_data, dwh_data, left_on=['shop_code', 'dmp_id'], right_on=['store_id', 'place_id'], how='outer', indicator='match')#.query('match=="right_only"')

    # Фильтр на доступы текущего пользователя
    rez = rez.loc[(rez['store_format'].isin(tabel_formats['format_code']))&
                            rez['city'].isin(tabel_regions['region_name'])&
                            rez['place_group'].isin(tabel_groups['group_code'])].query('match=="right_only"')[['short_name','place_group','place_id']].drop_duplicates().reset_index(drop=True)

    rez = rez.rename(columns={'short_name':'Торговый зал',
                            'place_group':'Группа',
                            'place_id':'Промо-место'})
    
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    rez.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.close()

    output.seek(0)

    return output

# rez
# # %%
# rez.to_excel('113_kan_promo_places.xlsx', index=False)
# # %%
