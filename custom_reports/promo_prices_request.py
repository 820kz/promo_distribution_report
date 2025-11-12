#%%imports
import MagnumDB
import os
import pandas as pd
import io
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
    'db_ip':os.environ['TABEL_IP'],
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
# лимиты по ценам
places_rules = {
                'CC':{'Т':2,'П':2,'СТ':78,'КК':24,'СП':2, 'TXO':-1, 'TB':3},
                'HYPER':{'Т':2,'П':2,'СТ':78,'КК':24,'СП':2, 'TXO':-1, 'TB':3},
                'ATAK':{'Т':2,'П':2,'СТ':78,'КК':24,'СП':2, 'TXO':-1, 'TB':3},
                'SUPER':{'Т':2,'П':2,'СТ':78,'КК':24,'СП':2, 'TXO':-1, 'TB':3},
                'EXPRESS':{'Т':4,'П':4,'СТ':78,'КК':24,'СП':4, 'TXO':-1, 'TB':3},
                'DAILY':{'Т':2,'П':4,'СТ':78,'КК':24,'СП':4, 'TXO':-1, 'TB':3}
                }

def get_promo_prices_data(promo_id, user_name, limit):

    if limit != None:
        lim_row = f'LIMIT {limit}'
    else:
        lim_row = ''

    # факт цен из табеля
    select_promos_query  = open("custom_reports/promo_prices_query_tabel.sql", encoding='utf-8', mode="r").read()
    db = MagnumDB.DBConnection(**db_promo_tabel)
    data_tabel = db.select(select_promos_query%(promo_id, lim_row))
    db.close()

    # Группы доступные пользователю
    select_tabel_groups_query  = open("custom_reports/promo_prices_query_tabel_groups.sql", encoding='utf-8', mode="r").read()
    db = MagnumDB.DBConnection(**db_promo_tabel)
    tabel_groups = db.select(select_tabel_groups_query%(user_name))
    db.close()

    # Регионы доступные пользователю
    select_tabel_regions_query  = open("custom_reports/promo_prices_query_tabel_regions.sql", encoding='utf-8', mode="r").read()
    db = MagnumDB.DBConnection(**db_promo_tabel)
    tabel_regions = db.select(select_tabel_regions_query%(user_name))
    db.close()

    # Форматы доступные пользователю
    select_tabel_formats_query  = open("custom_reports/promo_prices_query_tabel_formats.sql", encoding='utf-8', mode="r").read()
    db = MagnumDB.DBConnection(**db_promo_tabel)
    tabel_formats = db.select(select_tabel_formats_query%(user_name))
    db.close()

    # план цен из двх
    scenario_name = data_tabel['scenario_name'][0]
    select_promos_dwh_query  = open("custom_reports/promo_prices_query_dwh.sql", encoding='utf-8', mode="r").read()
    db = MagnumDB.DBConnection(**db_dwh)
    data_dwh = db.select(select_promos_dwh_query%(scenario_name))
    db.close()

    # добавить словарь с лимитами цен в отдельную колонку
    data_dwh['promo_prices'] = None

    for index, row in data_dwh.iterrows():
        store_format = row['store_format']
        place_type = row['place_type']

        if store_format in places_rules and place_type in places_rules[store_format]:
            data_dwh.at[index, 'promo_prices'] = places_rules[store_format][place_type]

    # обновить лимиты на значения из двх где не пусто
    data_dwh['promo_limits'] = where(data_dwh['prices_limit'].notna(), data_dwh['prices_limit'], data_dwh['promo_prices'])

    # фильтры данных по пользователю
    data_dwh = data_dwh.loc[(data_dwh['store_format'].isin(tabel_formats['format_code']))&
                            data_dwh['city'].isin(tabel_regions['region_name'])&
                            data_dwh['place_group'].isin(tabel_groups['group_code'])][['store_id', 'place_id', 'place_type', 'promo_limits']].drop_duplicates().reset_index(drop=True)

    # план + факт
    main = pd.merge(data_tabel, data_dwh, 
                        left_on=['shop_code', 'Промо-место'], 
                        right_on=['store_id', 'place_id'],
                        how='outer',
                        indicator='match')

    bad_place_id = ['НЕ УЧАСТВУЕТ', 'КАССА', 'НЕУЧАСТВУЕТ', 'ОЗ', 'УЦЕНКА', 'ДИСПЛЕЙ', 'СЕЗОН', 'E-COM', '#N/A', '0']

    # исключить мусор из данных
    main = main[(~main['Тип ДМП'].isin(bad_place_id))&(main['Тип ДМП'].notna())&(main['place_id'].notna())&(main['match']=='both')].reset_index(drop=True)

    # итоговый вид таблицы
    main = main[['Торговый зал', 'Формат', 'place_type', 'Промо-место', 'Факт цен', 'promo_limits']].drop_duplicates().reset_index(drop=True)
    main = main.rename(columns={'place_type':'Тип ДМП', 'promo_limits':'Лимит цен'})

    # разница лимита и факта
    main['Разница'] = main['Факт цен'] - main['Лимит цен']

    # отдать бинарник файла
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    main.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.close()

    output.seek(0)

    return output