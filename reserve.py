from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
from time import sleep
import os
from datetime import datetime

from selenium.webdriver.support.wait import WebDriverWait

# 获取项目根目录
_ = os.path.abspath(os.path.dirname(__file__))  # 返回当前文件路径
root_path = os.path.abspath(os.path.join(_, '..'))  # 返回根目录文件夹
chrome_option = Options()
chrome_option.add_experimental_option("detach", True)
chrome_driver_path = root_path + '/reserving_concert-main/' + 'chromedriver_mac64/chromedriver'  # chromedriver位置
chrome_option.add_argument("--disable-blink-features")
chrome_option.add_argument("--disable-blink-features=AutomationControlled")
chrome_option.add_experimental_option("excludeSwitches", ['enable-automation'])  # 不显示正在受自动化软件控制
# get直接返回，不再等待界面加载完成
desired_capabilities = DesiredCapabilities.CHROME
desired_capabilities["pageLoadStrategy"] = "none"
driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_option,
                          desired_capabilities=desired_capabilities)
wait = WebDriverWait(driver, 3)
driver.maximize_window()
userdetail_file = "userdetail.json"
count = 0
with open(userdetail_file, 'r') as f:
    user = json.load(f)
email = user["email"]
password = user["pwd"]
zone = user["zone"]
name = user["name"]
concert_url = user["concert_url"]
zone_list = 0
next_zone_index = 1


def setup():
    print('[START] setUp')
    try:
        driver.get(concert_url)
        driver.implicitly_wait(3)
    except Exception as e:
        print('[FAIL] setUp', e)


def login():
    print('[START] login')
    try:
        driver.find_element(
            By.XPATH, '//*[@class="btn-signin item d-none d-lg-inline-block"]').click()
        sleep(1)
        username = driver.find_element(By.NAME, "username")
        username.send_keys(email)
        pwd = driver.find_element(By.NAME, "password")
        pwd.send_keys(password)
        driver.find_element(By.XPATH, '//*[@class="btn-red btn-signin"]').click()
        sleep(10)
        driver.refresh()
        sleep(10)
    except Exception as e:
        print('[FAIL] login', e)
        login()


def select_show():
    print('[START] select_show')
    deal_fault('')
    try:
        cur_url = driver.current_url
        # if findUrl("verify_condition", cur_url) or findUrl("zones", cur_url):
        #     return
        if cur_url != concert_url:
            driver.get(concert_url)
        element = driver.find_element(
            By.XPATH,
            '//*[@id="section-event-round"]/div/div[1]/div[3]/div[2]/div/div[2]/div[2]/span/a')
        # TODO JUST FOR TEST
        # element = driver.find_element(
        #     By.XPATH,
        #     '//*[ @ id = "section-event-round"] / div / div[2] / div[3] / div[2] / div / div[2] / span / a')

        href = element.get_attribute('href')
        while href == 'javascript:;':
            sleep(1)
            driver.refresh()
            select_show()
        myClick(element)
    except Exception as e:
        print('[FAIL] select_show', e)
        select_show()


def verify():
    print('[START] verify')
    deal_fault('verify_condition')
    try:
        result = findUrl("verify_condition", driver.current_url)
        zones = findUrl("zones", driver.current_url)
        if result:
            element = driver.find_element(By.ID, "rdagree")
            myClick(element)
            sleep(0.5)
            verify_btn = driver.find_element(
                By.ID, 'btn_verify')
            myClick(verify_btn)
            sleep(0.1)
    except Exception as e:
        print('[FAIL] verify', e)
        if result:
            verify()
        if not result and not zones:
            main()


def findUrl(msg, link):
    if (link.find(msg) > 0):
        return True
    else:
        return False


def select_zone(zone=zone):
    print('[START] select_zone')
    deal_fault('zones')
    try:
        # count_zone = 0
        # index = 0
        # while count_zone == 0:
        #     count_zone = driver.execute_script(
        #         "return document.getElementsByTagName('area').length")
        # for i in range(1, count_zone + 1):
        #     seat = driver.find_element(
        #         By.XPATH, f'//map/area[{i}]').get_attribute("href")
        #     result = finZone(zone, seat)
        #     if result:
        #         index = i
        #         break
        # element = driver.find_element(
        #     By.XPATH, f'//map/area[{index}]')
        # myClick(element)
        get_zone_button = driver.find_element(
            By.ID, "popup-avail")
        myClick(get_zone_button)

        driver.find_element(By.ID, "avail_data")

        count_zone = 0
        index = 0
        while count_zone == 0:
            count_zone = driver.execute_script(
                "return document.getElementsByTagName('tr').length")
        for i in range(1, count_zone + 1):
            seat_type = driver.find_element(
                By.XPATH, f'//tbody/tr[{i}]/td[1]').get_attribute("textContent")
            seat_number = driver.find_element(
                By.XPATH, f'//tbody/tr[{i}]/td[2]/a').get_attribute("textContent")
            if (seat_number == 'Available' or int(seat_number) > 0) and seat_type in zone:
                index = i
                break
        if index == 0:
            driver.find_element(
                By.XPATH, f'//*[@class="fancybox-close"]').click()
            select_zone()
        else:
            element = driver.find_element(
                By.XPATH, f'//tbody/tr[{index}]')
            myClick(element)

    except Exception as e:
        print('[FAIL] select_zone', e)
        select_zone()


def finZone(msg, link):
    get_zone = link.split('#')
    if msg == get_zone[2]:
        return True
    else:
        return False


def select_seat(number=len(name)):
    print('[START] select_seat')
    deal_fault('fixed')
    try:
        if findUrl('fixed', driver.current_url):
            driver.find_element(By.ID, 'tableseats')
            count_loop = driver.execute_script(
                "return document.getElementsByClassName('seatuncheck').length")

            if count_loop < number:
                go_to_next_zone()

            for i in range(1, count_loop + 1):
                result = driver.execute_script(
                    "return document.getElementsByClassName('seatchecked').length")
                if result == number:
                    break
                print(i)
                driver.execute_script(
                    f"document.getElementsByClassName('seatuncheck')[{i - 1}].click()")
                sleep(0.6)
                result = driver.execute_script(
                    "return document.getElementsByClassName('seatchecked').length")
                if result == number:
                    break

            res = driver.find_element(
                By.XPATH, f' // *[ @ class = "result"] /span').get_attribute('textContent')
            if res == 'Available':
                booknow = driver.find_element(
                    By.XPATH, f' // *[@id="booknow"]')
                myClick(booknow)
            else:
                go_to_next_zone()
        else:
            driver.find_element(
                By.ID, 'book_cnt').click()
            driver.find_element(
                By.XPATH, f' // *[@id="book_cnt"] / option[{number + 1}]').click()
            res = driver.find_element(
                By.XPATH, f' // *[ @ class = "result"] /span').get_attribute('textContent')
            if res == 'Available':
                booknow = driver.find_element(
                    By.XPATH, f' // *[@id="booknow"]')
                myClick(booknow)
            else:
                go_to_next_zone()
    except Exception as e:
        print('[FAIL] select_seat', e)
        select_seat()


def go_to_next_zone():
    print('[START] go_to_next_zone')
    if findUrl("zones", driver.current_url):
        select_zone()
    try:
        back = driver.find_element(By.XPATH, f'//*[@class="btn-action"]')
        myClick(back)
        is_back = False
        while not is_back:
            is_back = findUrl("zones", driver.current_url)
        if is_back:
            select_zone()
            select_seat()
    except Exception as e:
        print('[FAIL] go_to_next_zone', e)
        go_to_next_zone()


def fill_name():
    print('[START] fill_name')
    deal_fault('enroll_fest')
    if findUrl('enroll_fest', driver.current_url):
        try:
            fills = driver.find_elements(
                By.CLASS_NAME, "input-txt")
            for i in range(0, len(name)):
                fill = fills[i]
                fill.send_keys(name[i])
            regnow = driver.find_element(By.ID, 'btn_regnow')
            myClick(regnow)
        except Exception as e:
            print('[FAIL] fill_name', e)
            fill_name()


def confirm():
    print('[START] confirm')
    deal_fault('paymentall')
    try:
        check_protect = driver.find_element(By.ID, "check-protect")
        myClick(check_protect)

        btn_pickup = driver.find_element(By.ID, "btn_pickup")
        myClick(btn_pickup)

        alipay = driver.find_elements(By.ID, "btn_alipay")

        if len(alipay):
            myClick(alipay[0])
        else:
            btn_creditcard = driver.find_element(By.ID, "btn_creditcard")
            myClick(btn_creditcard)

        checkagree = driver.find_element(By.ID, "checkagree")
        myClick(checkagree)

        btn_confirm = driver.find_element(By.ID, "btn_confirm")
        myClick(btn_confirm)
    except Exception as e:
        print('[FAIL] confirm', e)
        confirm()


def deal_fault(cur_step):
    if findUrl("verify_condition", driver.current_url) and cur_step != "verify_condition":
        verify()
    if findUrl("zones", driver.current_url) and cur_step != "zones":
        select_zone()
    if findUrl('fixed', driver.current_url) and cur_step != "fixed":
        select_seat()
    if findUrl('enroll_fest', driver.current_url) and cur_step != "enroll_fest":
        fill_name()
    if findUrl('paymentall', driver.current_url) and cur_step != "paymentall":
        confirm()


def confirm_ticketprotect():
    driver.find_element_by_partial_link_text(
        "ยืนยันที่นั่ง / Book Now").click()
    driver.implicitly_wait(50)
    driver.find_element_by_partial_link_text("Continue").click()
    driver.implicitly_wait(40)


def myClick(elm):
    actions = ActionChains(driver)
    actions.move_to_element(elm).perform()
    driver.execute_script("arguments[0].click();", elm)


# ===依据时间间隔, 自动计算并休眠到指定时间
def sleep_until_run_time(run_time):
    sleep(max(0, (run_time - datetime.now()).seconds))
    while True:  # 在靠近目标时间时
        if datetime.now() > run_time:
            break
    return run_time


def main():
    try:
        select_show()
        verify()
        select_zone()
        select_seat()
        fill_name()
        confirm()
    except Exception as e:
        print('[FAIL] main', e)


if __name__ == '__main__':
    setup()
    login()
    # TODO
    print('等待程序启动中')
    # sleep_until_run_time(datetime.strptime('2023-07-15 13:59:30', '%Y-%m-%d %H:%M:%S'))
    print('程序启动')
    main()
