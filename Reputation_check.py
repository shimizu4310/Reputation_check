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

#作成した関数を読み込む
import MyBase
import MyReputation

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

# 変数定義
INPUT_FILE = 'URL_test3.txt'													# チェックするURLが格納された一覧
OUTPUT_FILE = './result/Reputation_result'										# 最終的な結果を出力するファイル。拡張子はcsvとなるが、ここでは指定しない。
OUTPUT_TMP_FILE = './result/tmp_Reputation_result'								# 途中結果を出力するファイル。拡張子はcsvとなるが、ここでは指定しない。	※完了時刻や実行時間が出力されない。
SLEEP_PER_SITE = 1																# 1サイトチェックあたりの待機秒数。

HEADER1 = ['', '', 'WebPulse', '', '', 'URL void', '', '', '','','','','','IP void', '', '', '','','','']
HEADER2 = ['No.', 'check site', 'category', 'category_english', 'notes', 'Reputation', 'Country', 'Analysis Date', 'Register Date', 'IP address', 'ASN','url', 'status_code', 'Check IP','IP Reputation', 'IP Country', 'Analysis Date', 'IP ISP', 'ASP Owner', 'url','status_code']
Result_HEADER = [HEADER1,HEADER2]

################
#### Main
def main():
	print(r'===== Reputation Check =================')

	#### 時刻取得
	dt_start = datetime.datetime.now()
	start_time=dt_start.strftime('%Y/%m/%d %H:%M:%S')
	file_time=dt_start.strftime('_%Y%m%d_%H%M%S')

	#### ファイル存在確認
	print(r'Input File Check:'+INPUT_FILE)
	MyBase.file_check(INPUT_FILE)

	#### ファイル名編集
	Output_File = OUTPUT_FILE + file_time +'.csv'
	Output_Tmp_File = OUTPUT_TMP_FILE + file_time +'.csv'

	#### 中間ファイルを開き、開始時刻やヘッダを出力しクローズする。
	MyBase.result_tmp_file_csv_open(Output_Tmp_File, Result_HEADER, dt_start)
	print(r'Temporary File Open:'+Output_Tmp_File)

	#### インプットファイルの中身を出力
	print('\r\nInput File Open:'+INPUT_FILE)
	INPUT_LIST=MyBase.file_open(INPUT_FILE)
	for l in INPUT_LIST:
		print(l)
		print('\r\nNumber of check site:' + str(len(INPUT_LIST)) )
		print('========================================')
	#### end for

	#### 変数初期化
	result=[['NULL'] * len(HEADER2) for i in range(len(INPUT_LIST)) ]
	cnt=0

	#### レピュテーションチェック開始宣言
	print('\r\n\r\n===== Reputation Check =================')
	print(r'Number of check site:' + str(len(INPUT_LIST)) )
	print(r'Reputation Check Start Time:' + start_time )
	print(r'Output Result Temporary File Name:' + Output_Tmp_File )
	print(r'Process Status: Start reputation check start')
	print(r'Reputation sites: WebPulse, URL void, IP void')
	print('========================================\r\n\r\n')

	#### 1サイトずつ読み込み処理を繰り返す。
	for site in INPUT_LIST:

		# 変数初期化
		category='null'
		category_eng='null'
		notes='null'
		url_reputation='null'
		url_country='null'
		url_analysis_date='null'
		url_register_date='null'
		url_ip_address='null'
		url_asn='null'
		url_url='null'
		url_status_code=0
		check_ip='null'
		ip_reputation='null'
		ip_country='null'
		ip_analysis_date='null'
		ip_isp='null'
		ip_asp_owner='null'
		ip_url='null'
		ip_status_code=0

		# Webpulse check
		category, category_eng, notes = MyReputation.get_value_for_Webpulse(site)
		print('WebPulse: '+ site +':'+ category +':'+ notes +': Done!')

		if MyBase.check_boolen_ip(site):
			# IP void Check
			check_ip=site
			ip_reputation, ip_country, ip_analysis_date, ip_isp, ip_asp_owner, ip_status_code, ip_url=MyReputation.check_IPvoid(check_ip)
			print('IPvoid:' + check_ip + ',' + ip_reputation + ',' + ip_country + ',' + str(ip_status_code) +': Done!')
		else:
			# URL void check
			url_reputation, url_country, url_analysis_date, url_register_date, url_ip_address, url_asn, url_status_code, url_url=MyReputation.check_URLvoid(site)
			print('URLvoid:' + site + ',' + url_reputation + ',' + url_country + ',' + str(url_status_code) +': Done!')
			if MyBase.check_boolen_ip(url_ip_address):
				# IP void Check
				check_ip=url_ip_address
				ip_reputation, ip_country, ip_analysis_date, ip_isp, ip_asp_owner, ip_status_code, ip_url=MyReputation.check_IPvoid(check_ip)
				print('IPvoid:' + check_ip + ',' + ip_reputation + ',' + ip_country + ',' + str(ip_status_code) +': Done!')

		#結果格納
		result[cnt][0]=str(cnt+1)
		result[cnt][1]=site.replace('.' , '[.]')	# ディファングを入れて出力
		result[cnt][2]=category
		result[cnt][3]=category_eng
		result[cnt][4]=notes
		result[cnt][5]=url_reputation
		result[cnt][6]=url_country
		result[cnt][7]=url_analysis_date
		result[cnt][8]=url_register_date
		result[cnt][9]=url_ip_address.replace('.' , '[.]')	# ディファングを入れて出力
		result[cnt][10]=url_asn
		result[cnt][11]=url_url.replace('http' , 'hxxp')	# ディファングを入れて出力
		result[cnt][12]=url_status_code
		result[cnt][13]=check_ip.replace('.' , '[.]')	# ディファングを入れて出力
		result[cnt][14]=ip_reputation
		result[cnt][15]=ip_country
		result[cnt][16]=ip_analysis_date
		result[cnt][17]=ip_isp
		result[cnt][18]=ip_asp_owner
		result[cnt][19]=ip_url.replace('http' , 'hxxp')	# ディファングを入れて出力
		result[cnt][20]=ip_status_code

		#### 中間ファイルを開き、中間データを書き込む
		MyBase.result_tmp_file_csv_add(Output_Tmp_File, result[cnt])

		#### 状況出力
		print('\r\n===== Reputation Check Status =========')
		print('check site summary:\t' + site )
		print(' WebPulse category:\t' + category_eng )
		print(' URL void reputation:\t' + url_reputation )
		print(' IP void reputation:\t' + ip_reputation )
		print('\r\n')
		print('Process Status: Running')
		print('Number of check site:\t\t' + str(len(INPUT_LIST)) )
		print('Number of completed site:\t' + str(cnt+1) )
		print('Number of remaining site:\t' + str(len(INPUT_LIST)-(cnt+1)) )
		print('=======================================\r\n')

		#### Sleep per site
		time.sleep(SLEEP_PER_SITE)

		####インクリメント
		cnt +=1
	#### end for

	#### 時刻取得
	dt_end = datetime.datetime.now()
	end_time=dt_end.strftime('%Y/%m/%d %H:%M:%S')
	dt_process = dt_end - dt_start
	end_time=dt_end.strftime('%Y/%m/%d %H:%M:%S')

	#### 結果ファイル出力
	print(r'Try output reputation result:'+ Output_File)
	MyBase.result_file_csv_open(Output_File, Result_HEADER, dt_start, result)

	#### プログラム終了
	print('\r\n\r\n===== Reputation Check =================')
	print(r'Reputation sites: WebPulse, URL void, IP void')
	print(r'Number of check site:' + str(len(INPUT_LIST)) )
	print(r'Reputation Check Start Time:' + start_time )
	print(r'Reputation Check End Time:' + end_time )
	print(r'Reputation Check Processing Time:' + MyBase.get_process_time(dt_start, dt_end) )
	print(r'Output Result File Name:' + Output_File )
	print(r'Process Status: Finished!')
	print(r'========================================')

################
#### Main()を実行
if __name__ == '__main__':
	main()
	sys.exit(0)
