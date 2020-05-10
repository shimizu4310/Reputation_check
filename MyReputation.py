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

################		WebPulseで取得した値を返す。
################		Reputation
def driver_get_value_for_Webpulse(in_driver, in_category_class_name, in_rating_date_class_name):

	if len(in_driver.find_elements_by_class_name("search-result")) > 0 :	# 未評価サイトの場合
#<p class="search-result"><span>この URL はまだ評価されていません</span><!----><br><span>
		MyBase.driver_Check_class(in_driver, "search-result")
		if '評価されていません' in in_driver.find_element_by_class_name("search-result").text:
			category='未評価 (none)'
			category_eng_result='none'
			check_date='no data'
		else:
			print('ERROR: sentence of category none may be changed. Please check.')
			in_driver.quit()
			sys.exit(1)
	else:																# カテゴリがある場合
#<span class="clickable-category">ビジネス/経済 (Business/Economy)</span
#<span class="rating-date">最終評価日: 7 日 <
		MyBase.driver_Check_class(in_driver, in_category_class_name)
		MyBase.driver_Check_class(in_driver, in_rating_date_class_name)
		CategoryResults=in_driver.find_elements_by_class_name(in_category_class_name)
		category=''
		for i in range(len(CategoryResults)):
			category += CategoryResults[i].text
			category += ','
		category = category[:-1]										# remove last comma

		category_eng_result=''											# カテゴリで日本語を除いた文字列を作成
		for cate in category.split(','):
			m = re.search(r'\((.*)\)', cate)
			category_eng_result += m.group(1)
			category_eng_result += ','
		category_eng_result=category_eng_result[:-1]					# remove last comma

		SearchResult=in_driver.find_element_by_class_name(in_rating_date_class_name)	# 更新日付を取得
		check_date=SearchResult.text
		check_date = check_date[:-1]									# remove last ?

	return category, category_eng_result, check_date

################		WebPulse用のmain関数。returnとして、category, category_eng, notes※check_dateを返す。
################		Reputation

def get_value_for_Webpulse(in_check_site):
	Chrome_Driver=r'D:\外付けHDD_同期\22.Python\code\chromedriver_win32\chromedriver'		# エスケープ処理を除くため、rを入れている。
	Webpulse=r'https://sitereview.bluecoat.com/#/'											# WebPulse URL
	Webpulse_result=r'https://sitereview.bluecoat.com/#/lookup-result/'						# 遷移後のWebPulse URLの一部。URLの遷移が完了したか判定するために行う。
	TimeOutInt = 15																			# WebPulseのタイムアウトの判定値を入れる。入力値の秒数待機する。
	ClickTimeOutInt = 2																		# WebPulseでSubmitしたときに1クリックごとに何秒待機するか決める。
	ClickTryCnt = 5																			# WebPulseでSubmitしたときに最大何クリックするか決める。これは必ず指定する。
	Headless_mode = 1																		# ヘッドレス（ブラウザを起動しない）を選択する。0以外の場合、ヘッドレスモード。0の場合はブラウザを起動する。デバッグ時は0を入れる。
	sleep_per_request = 1																	# 一回のリクエスト後に何秒待機するか指定。0にするとWebPulseの場合、10リクエストした場合にプログラムかどうかの判定が入り止まってしまうことがある。

	print('WebPulse Check start. check site: '+in_check_site)

	# Driver起動
	driver=MyBase.open_driver_Chrome(Chrome_Driver, Headless_mode)

	# URLアクセス
	driver.get(Webpulse)

	# 全要素が取得できるまで待機
	MyBase.driver_Wait_Content(driver, TimeOutInt)

	# 画面の最大化 （submitボタンや入力フォームが画面に表示されないときに使う。画面領域外の箇所になるとエラーとなる。
	# driver.maximize_window()

	#入力値にチェックするURLを入れる。
	MyBase.driver_Check_id(driver, "txtUrl")
	SearchBar=driver.find_element_by_id("txtUrl").send_keys(in_check_site)

	#クリックを複数回実行する。
	MyBase.driver_click_try(driver, "btnLookup", ClickTimeOutInt, ClickTryCnt, Webpulse_result)

	#全要素が取得できるまで待機
	MyBase.driver_Wait_Content(driver, TimeOutInt)

	#カテゴリを取得
	category, category_eng, notes = driver_get_value_for_Webpulse(driver, "clickable-category", "rating-date")

	#Driverを終了する。
	print('Driver Close.' )
	driver.quit()

	#一時的に待機する。
	print('WebPulse Check is finished. check site: '+in_check_site)
	time.sleep(sleep_per_request)

	return category, category_eng, notes

################		URLvoidの値を返す。入力で与えられたoutに返す。
################		Reputation
def check_URLvoid(in_check_site):
	url_site="https://www.urlvoid.com/"
	payload = {'site': in_check_site, 'go': ''}
	rep='NULL'
	country='NULL'
	analysis_date='NULL'
	register_domain='NULL'
	ip_address='NULL'
	ASN='NULL'
	status_code=0
	check_url='NULL'
	body_content=[]

	print('URLvoid Check start. check site: '+in_check_site)

# データ取得
	body_content, status_code, check_url = MyBase.post_request_URL(url_site, payload)

# データ成形。HTMLのbody部で特定の箇所を抽出
	for n in body_content:

# レピュテーション
		if re.search(r'Blacklist Status', n):
			m = re.search(r'[0-9]+.[0-9]+', n)
			rep = m.group()

# 国名
		if re.search(r'Server Location', n):
			m = re.search(r'\((.+?)\<|Unknown', n)
			if m.group() == 'Unknown':
				country = 'Unknown'
			else:
				num = m.group()
				country = num[:-1]

# 分析日時
		if re.search(r'Last Analysis', n):
			m = re.search(r'<\/td><td>(.*) &nbsp', n)
			analysis_date = m.group(1)

# ドメイン登録日
		if re.search(r'Domain Registration', n):
			m = re.search(r'<\/td><td>(.*)<\/td><\/tr>|Unknown', n)
			if m.group() == 'Unknown':
				register_domain = 'Unknown'
			else:
				register_domain = m.group(1)

# IPアドレス
		if re.search(r'IP Address', n):
			m = re.search(r'<strong>(.*)<\/strong>|Unknown', n)
			if m.group() == 'Unknown':
				ip_address = 'Unknown'
			else:
				ip_address = m.group(1)

# ASN
		if re.search(r'ASN', n):
			m = re.search(r'<\/a>\ (.*)<\/td><\/tr>|Unknown', n)
			if m.group() == 'Unknown':
				ASN = 'Unknown'
			else:
				ASN = m.group(1)

	out_rep=rep
	out_country=country
	out_analysis=analysis_date
	out_register=register_domain
	out_ip=ip_address
	out_ASN=ASN
	out_status_code=status_code
	out_url=check_url

	print('URLvoid Check is finished. check site: '+in_check_site)

	return out_rep, out_country, out_analysis, out_register, out_ip, out_ASN, out_status_code, out_url


################		URLvoidの値を返す。
################		Reputation

def check_IPvoid(in_check_ip):
	url_site="https://www.ipvoid.com/ip-blacklist-check/"
	payload = {'ip': in_check_ip}
	rep='NULL'
	country='NULL'
	analyst_date='NULL'
	isp='NULL'
	asp_owner='NULL'

	status_code=0
	check_url='NULL'
	body_content=[]

# データ取得
	body_content, status_code, check_url = MyBase.post_request_URL(url_site, payload)

# データ成形。HTMLのbody部で特定の箇所を抽出
	for n in body_content:

# レピュテーション
		if re.search(r'Blacklist Status', n):
			m = re.search(r'[0-9]+.[0-9]+', n)
			rep = m.group()

# 国名
		if re.search(r'Country Code', n):
			m = re.search(r'\((.+?)\<|Unknown', n)
			if m.group() == 'Unknown':
				country = 'Unknown'
			else:
				num = m.group()
				country = num[:-1]

# Analyst Date
		if re.search(r'Analysis Date', n):
			m = re.search(r'<\/td><td>(.*)<\/td><\/tr>', n)
			analyst_date=m.group(1)

# ISP
		if re.search(r'ISP', n):
			m = re.search(r'<\/td><td>(.*)<\/td><\/tr>', n)
			isp=m.group(1)

# ASN Owner
		if re.search(r'ASN Owner', n):
			m = re.search(r'<\/td><td>(.*)<\/td><\/tr>', n)
			asp_owner=m.group(1)

	out_rep=rep
	out_country=country
	out_analyst_date=analyst_date
	out_isp=isp
	out_asp_owner=asp_owner
	out_status_code=status_code
	out_url=check_url
	return out_rep, out_country, out_analyst_date, out_isp, out_asp_owner, out_status_code, out_url
