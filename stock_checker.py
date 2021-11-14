#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# -*- coding: UTF-8 -*-
import requests
import sys
import gspread
import configparser 

from gspread.utils import a1_to_rowcol
from oauth2client.service_account import ServiceAccountCredentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#credentials = ServiceAccountCredentials.from_json_keyfile_name('/home/pi/services/StockChecker/GSpread-1e0d276e0409.json', scope)
credentials = ServiceAccountCredentials.from_json_keyfile_name('GSpread-1e0d276e0409.json', scope)


def check_stocks():
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open("test_dividend")
    worksheet = spreadsheet.get_worksheet(0)

    cell_id = a1_to_rowcol('m1')
    values_list = worksheet.col_values(cell_id[1])
    action_list = "";
    for i, value in enumerate(values_list):
        if i >= 28:
            break
        if value != "" and value != "wait" and value != "Utredning":
            notification_sent = worksheet.acell("N" + str(i+1)).value
            if notification_sent != "TRUE":
                buy_or_sell = worksheet.acell("L" + str(i+1)).value
                stock = worksheet.acell("A" + str(i+1)).value
                execution_statement = value
                action_list += buy_or_sell + " " + execution_statement + " stycken" + " " + stock + "!" + "\r\n"
                worksheet.update_acell("N" + str(i + 1), "TRUE")
    return action_list


message = check_stocks()

config = configparser.RawConfigParser()
config.read('telegram_credentials.config')

token = config.get('Telegram_token', 'token')
if message != "":
	data = {
	    'chat_id': '985282658',
	    'text': message 
	}
	token = token
	response = requests.post('https://api.telegram.org/bot' + token + '/sendMessage', data=data) 
else:
    print("No stock message to be sent.")


