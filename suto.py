import time 
import requests
from pathlib import Path

import telebot
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

CHROMEDRIVER = Path('C://chromedriver.exe')
BOT_TOKEN = ''
bot = telebot.TeleBot(BOT_TOKEN)


def start_driver():
    driver = webdriver.Chrome(executable_path=str(CHROMEDRIVER))
    delete_cache(driver)
    return driver

def delete_cache(driver):
    driver.execute_script("window.open('')")  # Create a separate tab than the main one
    driver.switch_to.window(driver.window_handles[-1])  # Switch window to the second tab
    driver.get('chrome://settings/clearBrowserData')  # Open your chrome settings.
    perform_actions(driver, Keys.TAB * 2 + Keys.DOWN * 4 + Keys.TAB * 5 + Keys.ENTER)  # Tab to the time select and key down to say "All Time" then go to the Confirm button and press Enter
    driver.close()  # Close that window
    driver.switch_to.window(driver.window_handles[0])  # Switch Selenium controls to the original tab to continue normal functionality.

def perform_actions(driver, keys):
    actions = ActionChains(driver)
    actions.send_keys(keys)
    time.sleep(2)
    print('Performing Actions!')
    actions.perform()

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	return message

def get(driver,enrollment = '0101IT191012'):
    # Get to the captcha page
    driver.get("https://www.uitrgpv.ac.in/exam/programselect.aspx")
    driver.find_element(by='xpath',value='//*[@id="ctl00_ContentPlaceHolder1_radlstProgram"]/tbody/tr/td[5]/span').click()
    driver.find_element(by='name',value='ctl00$ContentPlaceHolder1$txtrollno').send_keys(enrollment)
    driver.find_element(by='xpath',value='//*[@id="aspnetForm"]/section[2]/div/div[1]/div[3]/div/div[2]').click()
    driver.find_element(by='xpath',value='//*[@id="aspnetForm"]/section[2]/div/div[1]/div[3]/div/div[2]/ul/li[7]').click()

    # fetch captcha
    image = driver.find_element(by='xpath',value='//*[@id="ctl00_ContentPlaceHolder1_pnlCaptcha"]/div[1]/div/img').get_attribute('src')
    chat_id=''
    bot.send_message(chat_id=chat_id,text=image)
    time.sleep(10)
    
    req = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1')
    # req = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates')
    res = req.json()
    print(res['result'][-1]['message']['text'])
    captcha = res['result'][-1]['message']['text']
    driver.find_element(by='xpath',value='//*[@id="ctl00_ContentPlaceHolder1_TextBox1"]').send_keys(captcha.upper())
    driver.find_element(by='xpath',value='//*[@id="ctl00_ContentPlaceHolder1_btnviewresult"]').click()
    

    # store results in a csv
    name = driver.find_element(by='xpath',value='//*[@id="ctl00_ContentPlaceHolder1_lblNameGrading"]').text
    enrollment = driver.find_element(by='xpath',value='//*[@id="ctl00_ContentPlaceHolder1_lblRollNoGrading"]').text
    sgpa = driver.find_element(by='xpath',value='//*[@id="ctl00_ContentPlaceHolder1_lblSGPA"]').text

    html = driver.find_element(by='xpath',value='//*[@id="aspnetForm"]/section[2]/div/div[3]')
    with open(enrollment+".txt", "a") as f:
        f.write(driver.page_source)
    
    result = {
        'name':name,
        'enrollment':enrollment,
        'sgpa':sgpa
    }

    bot.send_message(chat_id=res['result'][-1]['message']['chat']['id'],text=str(result))
    with open("index.txt", "a") as f:
        f.write(f"{name},{enrollment},{sgpa}\n")
    driver.close()

if __name__ == '__main__':
    exclude = ['0101IT191042','0101IT191044','0101IT191050','0101IT191055','0101IT191056','0101IT191059 ','0101IT191063 ','0101IT191064',]
    for i in range(68,70):
        driver = start_driver()
        enrollment = '0101IT1910'+str(i).zfill(2)
        if enrollment not in exclude:
            get(driver,enrollment)