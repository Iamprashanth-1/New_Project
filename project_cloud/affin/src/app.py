from bs4 import BeautifulSoup
import requests, re, itertools, csv,json
import itertools
import boto3
import logging,sys
import pymongo ,sqlite3
from pymongo import MongoClient
from pymongo import database
from pymongo.errors import ConnectionFailure
from datetime import datetime, timedelta
logging.basicConfig(stream=sys.stdout,  level=logging.INFO)

yesterday = datetime.now() - timedelta(1)
yesterday_date = datetime.strftime(yesterday, '%d-%b-%y')

password ='2AyZYEKDOLnozrg6'
database_user ='fahadev'
client = MongoClient(f"mongodb+srv://faha_nonprod:{password}@fahadev.tj25u.mongodb.net/{database_user}?retryWrites=true&w=majority")

conn = sqlite3.connect('example.db')
def sqlite_insert(val):
    cursor = conn.cursor()

    sql ='''CREATE TABLE if not exists data(
            'Scheme Code' VARCHAR(100),
            'Scheme Name' VARCHAR(100),
            'ISIN Div Payout/ISIN Growth' VARCHAR(100),
            'ISIN Div Reinvestment' VARCHAR(100),
            'Net Asset Value' VARCHAR(100),
            'Repurchase Price' VARCHAR(100),
            'Sale Price' VARCHAR(100),
            'Date' VARCHAR(100),
            'Scheme Classification' VARCHAR(100),
            'Scheme Type' VARCHAR(100),
            'Scheme Category' VARCHAR(100),
            'Fund Family' VARCHAR(100)
            )'''
    cursor.execute(sql)
    cursor.executemany('INSERT INTO data VALUES (?,? ,?, ? ,? ,? ,? ,? ,? ,? ,?  ,?)', val)
    # for row in cursor.execute('select count(*) from data ;'):
    #     print(row)
    conn.commit()
    #close the connection
    cursor.close()
    

def feth_older_data():
    collection_list = client.business.list_collection_names()
    if 'temp' in collection_list:
        url =f'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt={yesterday_date}'
        lambda_handler(url)
    else:
        current_date  = datetime.now() 
        # Fetching older data from year 2010
        for years in range(2010,current_date.year):
            older_date = datetime.strftime(yesterday, '%d-%b-')+str(years)
            older_date_next = datetime.strftime(yesterday, '%d-%b-')+str(years+1)
            url =f'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt={older_date}&todt={older_date_next}'
            lambda_handler(url)
        

def resp(url,drop_value):
    try:
        response        = requests.get(url).text
        soup            = BeautifulSoup(response, 'lxml')
        options         = soup.select(f'select#{drop_value} > option')
        fund_id_dict_mf   = {}

        for option in options:
            if option['value'].strip():
                fund_id_dict_mf[ option.string ]  = option['value']
        return fund_id_dict_mf
    except:
        raise Exception(f'Failed to Fetch Data from {url}')

def lambda_handler(url):
    print(url)
    logging.info('Fetching data from https://www.amfiindia.com/nav-history-download')
    #fund_id_dict_mf_name= resp('https://www.amfiindia.com/nav-history-download', 'NavDownMFName')
    #fund_id_dict_mf_type = resp('https://www.amfiindia.com/nav-history-download', 'NavDownType')
    
    logging.info(f'Fetching data From AFFIINDIA on date {yesterday_date} from  http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt={yesterday_date}')
    try:
        response    = requests.get(url).text
    except Exception as e:
        raise Exception('unable to fetch data from AFFIINDIA')
    raw_data    = [line for line in response.split('\n') if line.strip()]
    #print(raw_data)
    Colums    = [val.strip() for val in raw_data[0].split(';')]+['Scheme Classification','Scheme Type','Scheme Category','Fund Family']

    final_data      = []
    final_data_sqlite = []
    check_next      = False
    mf_scheme_type  = ''
    mf_family       = ''


    for line in raw_data[1:]:
        if line.find(';') == -1:
            
            if check_next:
                mf_scheme_type  = mf_family.strip()
                check_next      = False
            else:
                check_next      = True

            mf_family   = line.strip()
            
        else:
            check_next  = False

            row = [element.strip() for element in line.split(';') ]
            #print(row)
            row.extend( [
                mf_scheme_type,
                re.search( r'(^.*)\(',  mf_scheme_type).group(1),
                re.search( r'\((.*)\)', mf_scheme_type).group(1),
                mf_family,
                #fund_id_dict_mf_name[mf_family],
                
            ] )
            
            final_data.append( dict( zip( Colums, row ) ) )
            final_data_sqlite.append( tuple(row))
    insert_mongo(final_data)
    # use this to insert for sqlite sqlite_insert(final_data_sqlite)
    return 'Insertion Succesful'
    
def insert_mongo(values):
    try:
        client.business.temp.insert_many(values)
        logging.info('Insertion Successfully')
    except Exception as e:
        logging.info(f'Failed to insert data with exception {e}')
        raise Exception('Failed to insert')
        


#lambda_handler()
feth_older_data()
# cursor = conn.cursor()
# # cursor.execute('drop table data;')
# for row in cursor.execute('select count(*) from data  ;'):
#     print(row)
