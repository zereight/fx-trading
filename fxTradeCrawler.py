import numpy as np
import pandas as pd
import time
import bs4
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 전역 변수들
import private_info # 개인정보있는 파일
my_ID = private_info.my_ID
my_PW = private_info.my_PW

prev_my_Money = 0
my_Money = 0
start_invest_money = 1000 # KRW
martin_process = [start_invest_money]
current_invest_money = start_invest_money
current_martin = 0
invested_res = 0

def waiting(_type, name):
    try:
        if _type == "class":
            element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, name)))
        elif _type == "id":
            element = wait.until(EC.element_to_be_clickable((By.ID, name)))
        else:
            print("type error", _type, " cannot resolve")
    except Exception as e:
        driver.refresh()
        time.sleep(1)
        print(e, "\n Cannot find that element")

def convert_date1(t):
    t = str(t).split(" ")
    return str(datetime.datetime( datetime.date.today().year, datetime.date.today().month, int(t[0][:-1]), int(t[1][:-1]),  int(t[2][:-1]), 0))

def convert_date2(t):
    t = str(t).split(" ")
    t = t[1].split(":")
    return str(datetime.datetime( datetime.date.today().year, datetime.date.today().month, datetime.date.today().day, int(t[0]), int(t[1]),  int(t[2])))

def date_add_1minute(a):
    a = datetime.datetime.strptime(a, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(minutes=1)
    return convert_date2(a)

def find_price_result(t):
    driver.refresh()
    waiting("id", "resultList")
    table = driver.find_elements_by_css_selector("#resultList > tr > td:nth-child(1)") # #resultList > tr:nth-child(1)

    for i,tr in enumerate(table):
        if( str(t) in str(convert_date1(tr.get_attribute("innerText"))) ):
            return driver.find_element_by_css_selector(F"#resultList > tr:nth-child({i+1}) > td:nth-child(2)").get_attribute("innerText"), \
                     driver.find_element_by_css_selector(F"#resultList > tr:nth-child({i+1}) > td:nth-child(3) > span").get_attribute("innerText")


    # 해당 시간에 대한 결과값을 못찾았으면
    return 0,0


while(1):
    time.sleep(1)
    try:
        # 웹 드라이버를 켠다
        driver = webdriver.Chrome("./chromedriver")
        driver.implicitly_wait(1)

        # 사이트 접속
        driver.get("https://fxcity.co.kr/#")

        # 로딩 대기
        wait = WebDriverWait(driver, 2)

        # 토글 버튼 기다리고
        waiting("class", "btn toggle")

        # 배너 클릭
        driver.find_element_by_css_selector("body > container > header > div > nav > div.navtoggle > a").click()

        time.sleep(1)

        # 로그인 버튼 클릭
        driver.find_element_by_css_selector("body > container > header > div > nav > div.innerset > div > div > a.btn.login").click()

        time.sleep(1)

        # 카카오 로그인 버튼 클릭
        driver.find_element_by_css_selector("body > container > div > form > div.snsbtnset > div.social.kakao > a").click()

        time.sleep(1)

        # 창전환
        driver.switch_to_window(driver.window_handles[1])

        time.sleep(1)
        waiting("id", 'id_email_2')

        # 카카오 로그인
        driver.find_element_by_xpath('//*[@id="id_email_2"]').send_keys(my_ID)
        driver.find_element_by_xpath('//*[@id="id_password_3"]').send_keys(my_PW)

        time.sleep(1)

        driver.find_element_by_css_selector("#login-form > fieldset > div.wrap_btn > button").click()

        # 창전환
        driver.switch_to_window(driver.window_handles[0])

        waiting("class","navtoggle")

        # 배너 클릭
        driver.find_element_by_css_selector("body > container > header > div > nav > div.navtoggle > a").click()
        driver.find_element_by_css_selector("body > container > header > div > nav > div.innerset > ul > li:nth-child(1) > a").click()
        driver.find_element_by_css_selector("body > container > header > div > nav > div.innerset > ul > li.act.on > ul > li:nth-child(1) > a").click()
        break
    except Exception as e:
        print(e)
        driver.close()

# 파일 만들기
df = pd.DataFrame(columns=["time", "price", "result"])
df.to_csv('fx_trade_dataset.csv',encoding='utf-8-sig')

# 이어 붙이기
with open('fx_trade_dataset.csv', 'a') as f:

    # 가장 오래된 결과 수집
    while(1): # 실패하면 계속 시도

        try:
            t = convert_date1(
                driver.find_element_by_css_selector(f'#resultList > tr:nth-child(15) > td:nth-child(1)').get_attribute(
                    "innerHTML"))
            p = driver.find_element_by_css_selector(f'#resultList > tr:nth-child(15) > td:nth-child(2)').get_attribute(
                "innerHTML")
            r = driver.find_element_by_css_selector(
                f'#resultList > tr:nth-child(15) > td:nth-child(3) > span').get_attribute("innerHTML")

            print(F"{t} -> {r}")
            break
        except Exception as e:
            print(e)
            continue

    df = df.append({'time': t, 'price': p, 'result': r}, ignore_index=True)
    df.to_csv('fx_trade_dataset.csv', encoding='utf-8-sig')

    # 그 시간에서 1분씩 증가 시켜가면서 결과를 체크하여 df에 추가
    while(1):

        # 현재 시간값에 1분을 더함
        newTime = date_add_1minute( df.iloc[ len(df)-1 ]["time"] )
        # 새로운 시가와 결과값
        newPrice, newResult = find_price_result(newTime)



        if( (newPrice==0 and newResult==0) or (newResult=="진행중") ):
            print(newTime, "에 대한 결과값을 못찾았습니다.")
            time.sleep(10)
            continue

        print(F"{newTime} -> {newResult}")

        df = df.append({'time': newTime, 'price': p, 'result': newResult}, ignore_index=True)
        df.to_csv('fx_trade_dataset.csv', encoding='utf-8-sig')

