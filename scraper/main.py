from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import socket

from selenium.webdriver.remote.command import Command
import requests
import json
from time import sleep
import datetime

home_url = 'https://prenotaonline.esteri.it/login.aspx?cidsede=100076&returnUrl=//'
email = 'marisabaiocchi@yahoo.com'
password = 'Marisa25'
anti_captcha_key = '4a4f81601e0acb667fc2062c06e014a5'
captcha_create_task_url = 'http://api.anti-captcha.com/createTask'
get_captcha_task_result_url = 'https://api.anti-captcha.com/getTaskResult'


def get_status(driver):
    try:
        driver.execute(Command.STATUS)
        return "Alive"
    except:
        return "Dead"

        
def wait(driver, timeout=30):
    return WebDriverWait(driver, timeout)

def format_datetime(dt):
    # dd/mm/YY H:M:S
    return dt.strftime("%d/%m/%Y %H:%M:%S")

def ceil_dt(dt=None, delta=datetime.timedelta(minutes=15)):
    return dt + (datetime.datetime.min - dt) % delta


def create_captcha_task(base64_image):
    payload =  {
            "clientKey":anti_captcha_key,
            "task":
                {
                    "type":"ImageToTextTask",
                    "body":base64_image,
                    "phrase":"false",
                    "case":"false",
                    "numeric":0,
                    "math":"false",
                    "minLength":4,
                    "maxLength":4
                }
            }
    return json.dumps(payload)

def request_captcha_solve(base64_image):
    return requests.post(captcha_create_task_url, data=create_captcha_task(base64_image)).json()

def at_home_page(driver):
    return 'login' in driver.current_url.lower() and 'returnurl=%2f%2f' not in driver.current_url.lower()

def at_login_form(driver):
    return 'login' in driver.current_url.lower() and 'returnurl=%2f%2f' in driver.current_url.lower()

def at_landing_page(driver):
    return 'default.aspx' in driver.current_url.lower()

def at_service_selection_page(driver):
    return 'selecciona el servicio' in driver.title.lower()

def at_confirm_reconstrucion_page(driver):
    return 'reconstrucción de ciudadanía' in driver.title.lower()

def at_calendar_page(driver):
    return 'acc_prenota.aspx' in driver.current_url.lower() and not at_confirm_reconstrucion_page(driver) and not at_service_selection_page(driver)
    
def is_open_date(date):
    return date.get_attribute("class") != 'noSelectableDay' and date.get_attribute("class") != 'otherMonthDay'

def get_calendar_month(calendar):
    return calendar.find_element_by_xpath("/html/body/form/div[2]/div[3]/div[2]/div[2]/span/table/tbody/tr[1]/th[2]/span").text

def click_home_logo(driver):
    logo =  wait(driver).until((EC.presence_of_element_located((By.ID,'img_logo'))))
    logo.click()
    driver.implicitly_wait(10)


sleep(10)



while True:
    print("Starting driver...", flush=True)
    # Run locally
    #driver = webdriver.Firefox(executable_path='./geckodriver', keep_alive=True) 
    # Run with docker
    driver = webdriver.Remote(command_executor='http://selenium:4444/wd/hub', desired_capabilities=DesiredCapabilities.FIREFOX, keep_alive=True) 
    driver.get(home_url)
    driver.implicitly_wait(5)
    while get_status(driver) == 'Alive':
        try:
            if at_home_page(driver):
                print("Opening login form...", flush=True)
                
                login_nav_button = wait(driver).until((EC.presence_of_element_located((By.ID, "BtnLogin"))))
                login_nav_button.click()
                driver.implicitly_wait(20)

            if at_login_form(driver):
                print("Logging in...", flush=True)
                user_name_field = wait(driver).until((EC.presence_of_element_located((By.ID, "UserName"))))
                user_name_field.clear()
                user_name_field.send_keys(email)

                password_field = wait(driver).until((EC.presence_of_element_located((By.ID, "Password"))))
                password_field.clear()
                password_field.send_keys(password)
                
                captcha_image = wait(driver).until((EC.presence_of_element_located((By.XPATH, '//*[@id="captchaLogin"]'))))
                captcha_as_base64 = captcha_image.screenshot_as_base64

                captcha_request = request_captcha_solve(captcha_as_base64)
                print(f"Captcha Request: {captcha_request}", flush=True)

                # Request failed, Keep retrying
                while(captcha_request['errorId'] != 0):
                    print("Captcha Request failed. Retrying...", flush=True)
                    captcha_request = request_captcha_solve(captcha_as_base64)

                captcha_task_id = captcha_request['taskId']
                captcha_response = requests.post(get_captcha_task_result_url, data=json.dumps({"clientKey": anti_captcha_key, "taskId": captcha_task_id})).json()

                while(captcha_response['status'] != 'ready'):
                    print("Captcha not solved yet, waiting 10 seconds...")
                    sleep(20)
                    captcha_response = requests.post(get_captcha_task_result_url, data=json.dumps({"clientKey": anti_captcha_key, "taskId": captcha_task_id})).json()

                print(f"Captcha Response: {captcha_response}", flush=True)    
                captcha_field = wait(driver).until((EC.presence_of_element_located((By.NAME, 'loginCaptcha'))))
                captcha_field.clear()
                captcha_field.send_keys(captcha_response['solution']['text'])
    
                login_button =  wait(driver).until((EC.presence_of_element_located((By.NAME, 'BtnConfermaL'))))
                login_button.click()
                driver.implicitly_wait(20)

            if at_landing_page(driver):
                print("Navigating through landing page...", flush=True)
                cita_nav_link = wait(driver).until((EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_repFunzioni_ctl00_btnMenuItem"]'))))
                cita_nav_link.click()
                driver.implicitly_wait(20)

            if at_service_selection_page(driver):
                print("Selecting service: Reconstrucción de ciudadanía...", flush=True)
                reconstrucion_nav_link = wait(driver).until((EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_rpServizi_ctl03_btnNomeServizio"]'))))
                reconstrucion_nav_link.click()
                driver.implicitly_wait(20)

            if at_confirm_reconstrucion_page(driver):
                print("Navigating through Reconstrucción de ciudadanía confirmation...", flush=True)
                confirm_button = wait(driver).until((EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_acc_datiAddizionali1_btnContinua"]'))))
                confirm_button.click()
                driver.implicitly_wait(20)

            if at_calendar_page(driver):
                print("Checking calendar...", flush=True)
                
                month_search_depth = 15
                for month in range(0, month_search_depth):
                    calendar =  wait(driver).until((EC.visibility_of_element_located((By.CLASS_NAME, 'calendario'))))
                    month_name = get_calendar_month(calendar)

                    for date in calendar.find_elements_by_tag_name('td'):
                        if is_open_date(date):
                            print(f"FOUND: {month_name} {date.text}", flush=True)
                            print(date.get_attribute('outerHTML'), flush=True)
                    
                    next_month_button = wait(driver).until((EC.visibility_of_element_located((By.XPATH, '/html/body/form/div[2]/div[3]/div[2]/div[2]/span/table/tbody/tr[1]/th[3]/input'))))
                    next_month_button.click()
                    driver.implicitly_wait(10)

                print("Finished checking calendar, closing driver...", flush=True)
                driver.quit()

                sleep_till_dt = ceil_dt(dt=datetime.datetime.now(), delta=datetime.timedelta(minutes=10))
                print(F"Current time: {format_datetime(datetime.datetime.now())}", flush=True)
                print(f"Sleeping {(sleep_till_dt - datetime.datetime.now()).total_seconds()} seconds till {format_datetime(sleep_till_dt)}", flush=True)
                sleep((sleep_till_dt - datetime.datetime.now()).total_seconds()) # Sleep 10 minutes
                break

        except Exception as e:
            print(f"ERROR: {e}", flush=True)
            continue
        

# yxxp msqq opmr dlsg 
