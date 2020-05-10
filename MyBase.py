import sys
import os
import locale
import urllib.request
import urllib.error
import requests
import re
import csv
import pprint
import datetime
import selenium
import time

# URL voidやIP void用。requestライブラリを使用
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Selenium用
from selenium import webdriver
from time import sleep

#Enter keyを押すために必要？
from selenium.webdriver.common.keys import Keys

#全要素が取得できるまで待機するようにimport
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

#エラー処理用のFrom
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

#ヘッドレスモード（ブラウザを見えなくするモード）で必要。
from selenium.webdriver.chrome.options import Options

################		ファイルの存在確認
################		base

def file_check(in_file):

	if os.path.exists(in_file):
		print(in_file + ' exists.')
	else:
		print('ERROR!! File ' +in_file+ r' does not exist.')
		exit(1)

################		ファイルを開いて読み込み
################		base
def file_open(In_Path):
	try:
		f = open(In_Path)
	except OSError as e:
		print(e)
		sys.exit(1)
	else:
		# l = f.readlines() #改行を含む場合
		list = [s.strip() for s in f.readlines()]
		f.close()
		return list

################		中間ファイルを開いて、開始時刻とヘッダを入力する。
################		base
def result_tmp_file_csv_open(in_tmp_file, in_header, in_dt_start_time):
	try:
		f = open(in_tmp_file, mode='w', newline="")
	except OSError as e:
		print(e)
		sys.exit(1)
	else:
		writer = csv.writer(f, lineterminator='\n')
		writer.writerow(['Script Start:', in_dt_start_time.strftime('%Y/%m/%d %H:%M:%S')])
		writer.writerows(in_header)
		f.close()

################		中間ファイルを開いて、中間結果を出力する。
################		base
def result_tmp_file_csv_add(in_tmp_file, in_result):
	try:
		f = open(in_tmp_file, mode='a', newline="")
	except OSError as e:
		print(e)
		sys.exit(1)
	else:
		writer = csv.writer(f, lineterminator='\n')
		writer.writerow(in_result)
		f.close()

################		最終的な結果を開いて結果を出力する。
################		base
def result_file_csv_open(in_tmp_file, in_header, in_dt_start_time, in_result):
	try:
		f = open(in_tmp_file, mode='w', newline="")
	except OSError as e:
		print(e)
		sys.exit(1)
	else:
		# 時刻取得
		start_time=in_dt_start_time.strftime('%Y/%m/%d %H:%M:%S')
		dt_end = datetime.datetime.now()
		end_time=dt_end.strftime('%Y/%m/%d %H:%M:%S')

		writer = csv.writer(f, lineterminator='\n')
		writer.writerow(['Script Start:', start_time])
		writer.writerow(['Script End:', end_time])
		writer.writerow(['Processing time:', get_process_time(in_dt_start_time, dt_end)])
		writer.writerows(in_header)
		writer.writerows(in_result)
		f.close()

################		実行時間を出力する。返しはstringで返す。
################		base
def get_process_time(in_dt_start, in_dt_end):
	# 丸め誤差が起こるので下記は使用しない。
	'''
	dt_process = in_dt_end - in_dt_start
	total_sec = dt_process.total_seconds()

	hour = total_sec//3600			# 時間を返す
	min = (total_sec%3600)//60		# 分を返す
	sec = ((total_sec%3600)%60)		# 秒を返す

	return str(int(hour))+':'+str(int(min)).zfill(2)+':'+str(int(sec)).zfill(2)
	'''
	start_time=in_dt_start.strftime('%Y/%m/%d %H:%M:%S')
	end_time=in_dt_end.strftime('%Y/%m/%d %H:%M:%S')
	dt_process=datetime.datetime.strptime(end_time,'%Y/%m/%d %H:%M:%S')-datetime.datetime.strptime(start_time,'%Y/%m/%d %H:%M:%S')

	total_sec = dt_process.total_seconds()
	hour = total_sec//3600			# 時間を返す
	min = (total_sec%3600)//60		# 分を返す
	sec = ((total_sec%3600)%60)		# 秒を返す

	return str(int(hour))+':'+str(int(min)).zfill(2)+':'+str(int(sec)).zfill(2)

################		入力値がIPかデータか返却する
################		base
def check_boolen_ip(in_data):

	if	re.search(r'^(([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$', in_data):	# IPアドレスのフォーマットとして完全一致するか確認
		return True
	else:
		return False

################		ドライバーを起動する。ヘッドレスかどうかの判定も含む
################		base
def open_driver_Chrome(in_driver_path, in_mode):
	print(r'Driver:'+ in_driver_path +' : Try Start.')
	options = Options()
	if in_mode == 0:
# 		options.add_argument('--headless')			#wo headless
		print(r'Browser: Headless mode : off')
	else:
		options.add_argument('--headless')			#w/ headless
		print(r'Browser: Headless mode : on')

	driver = webdriver.Chrome(in_driver_path,options=options)
	print(r'Driver:'+ in_driver_path +' : Started.')

	return driver

################		全要素が取得できるまで待機する関数。あくまでタイムアウトのチェックのみで、ステータスコードは取得できない。
################		base
def driver_Wait_Content(in_driver, in_TimeOutInt):
	try:
		WebDriverWait(in_driver, in_TimeOutInt).until(EC.presence_of_all_elements_located)
	except TimeoutException as te:
		print("Time Out:driver_Wait_Content")
		print(te)


################		IDを検索する関数。IDが無い場合は、エラーを出力。
################		base
def driver_Check_id(in_driver, in_id):
	try:
		in_driver.find_element_by_id(in_id)
	except NoSuchElementException:
		print(r'ERROR:Cannot connect to Site or Site does not have ID:' +in_id)
		in_driver.quit()
		sys.exit(1)
	else:
		print(r'Site has ID:' +in_id)


################		IDを検索する関数。IDが無い場合は、エラーを出力。
################		base
def driver_Check_class(in_driver, in_class):
	try:
		in_driver.find_element_by_class_name(in_class)
	except NoSuchElementException:
		print(r'ERROR:Cannot connect to Site or Site does not have class name:' +in_class)
		in_driver.quit()
		sys.exit(1)
	else:
		print(r'Site has class name:' +in_class)


################		クリックを行う。なおなぜか一回では反映されないことがあるため複数回行う。URLが変更されたことをもって次へ遷移したと判断する。与えられた回数を超えた場合はエラー出力し終了する。無限回にするとリクエストが無限に飛ぶ可能性があるので必ず回数は限定する。
################		base
def driver_click_try(in_driver, in_id, in_ClickTimeOutInt, in_try_cnt, in_next_url):
	i=0
	while i< in_try_cnt:
#		print('Submit Button Try. Check URL is '+ Check_url)
#		in_driver.find_element_by_id("txtUrl").send_keys(Keys.ENTER)		#これでもいける。Enter Keyを入力する。
		in_driver.find_element_by_id(in_id).click()							#これでもいける。ボタンをクリックする。
#		print('Click sleep :'+ str(in_ClickTimeOutInt))
		time.sleep(in_ClickTimeOutInt)
#		print('Current URL: '+ driver.current_url)
		if in_next_url in in_driver.current_url:
			print(r'Click Finished. Break.')
			break
	else:
		print(r'ERROR:Click may be not working. Click Count is Exceed. Click Count:' +str(in_try_cnt))
		in_driver.quit()
		sys.exit(1)

################		urllib.request,urllib.errorを使ったURL。現在使っていない。
################		base

def get_URL(url):
	req = Request(url)
	content2 = []
	try:
		res = urlopen(req)
	except HTTPError as e:
		print('The server couldn\'t fulfill the request.')
		print('URL:', url)
		print('Error code: ', e.code)
	except URLError as e:
		print('We failed to reach a server.')
		print('URL:', url)
		print('Reason: ', e.reason)

	else:
		body=res.read()
		content = body.decode()
		content2 = content.splitlines()
		res.close()

	return content2

################		requestsを使ったPOST通信
################		base

def post_request_URL(in_url, in_payload):
	req = requests.post(in_url, data=in_payload)
	content=req.text
	content2=content.splitlines()

	out_content=content2
	out_status_code=req.status_code
	out_url=req.url

	return out_content, out_status_code, out_url
