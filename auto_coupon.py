"""
Author: Ni Runyu & MonkeyDC
Date: 2023-09-18 21:59:45
LastEditors: Ni Runyu & MonkeyDC
LastEditTime: 2023-09-21 20:51:04
Description: 用于自动领取魔灵召唤的优惠券

Copyright (c) 2023 by Ni Runyu, All Rights Reserved. 
"""
import time

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select


def is_korean_char(char):
    # 转换字符为Unicode编码
    char_code = ord(char)

    # 检查是否在韩文字符范围内
    if (
        (char_code >= 0xAC00 and char_code <= 0xD7A3)
        or (char_code >= 0x1100 and char_code <= 0x11FF)
        or (char_code >= 0x3130 and char_code <= 0x318F)
        or (char_code >= 0xA960 and char_code <= 0xA97F)
    ):
        return True
    else:
        return False


def read_info(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def use_coupon(user_id, user_server, coupon):
    """
    description: 使用coupon
    param user_id: hive id
    param user_server: [global, korea, japan, china, asia, europe]
    param coupon: coupon code
    return {*}
    """

    url = "https://event.withhive.com/ci/smon/evt_coupon"
    driver = webdriver.Chrome(
        # executable_path="/mnt/d/download/chromedriver_win32/",
    )

    # Navigate to the webpage
    driver.get(url)

    # Fill in the user ID (assuming it's an input field with id="EVTid")
    user_id_input = driver.find_element(By.ID, "EVTid")
    user_id_input.send_keys(user_id)
    cupon_input = driver.find_element(By.ID, "EVTcode")
    cupon_input.send_keys(coupon)
    user_server_select = driver.find_element(By.ID, "EVTselect")
    js = 'arguments[0].removeAttribute("style");'
    driver.execute_script(js, user_server_select)
    ## 等待使用js 语法来操作隐藏的属性
    time.sleep(0.5)
    user_server_select = Select(user_server_select)
    user_server_select.select_by_value(user_server)

    # Simulate clicking the "使用优惠券" button
    try:
        coupon_button = driver.find_element(By.CLASS_NAME, "btn_use")
        coupon_button.click()
    except:
        return "invalid user ID"

    time.sleep(1)

    # <div id="EVTpop_coupon" class="pop_wrap pop_coupon" style="display:none;">
    pop = driver.find_element(By.ID, "EVTpop_coupon")
    driver.execute_script(js, pop)
    confirm_button = driver.find_element(By.CLASS_NAME, "btn_confirm")
    confirm_button.click()
    confirm_button.send_keys(Keys.ENTER)

    time.sleep(1)
    pop1 = driver.find_element(By.ID, "EVTpop_1")
    driver.execute_script(js, pop1)
    # message = driver.find_element(By.CLASS_NAME, "wrap_cont")
    # message.execute_script(js, message)

    message = pop1.text.split("\n")
    while any(is_korean_char(m) for m in pop1.text):
        time.sleep(1)
        pop1.click()
        message = pop1.text.split("\n")
    # Wait for some time (e.g., 5 seconds) to see the result
    # WebDriverWait(driver, 1).until(EC.url_changes(url))

    # Close the browser when done
    driver.quit()

    return "".join(message[:-1])


if __name__ == "__main__":
    user_info_path = "./user_info.txt"
    coupon_path = "./coupon.txt"
    user_ids = list()
    user_servers = list()

    for user_info in read_info(user_info_path):
        try:
            user_id, user_server = user_info.strip().split(":")
        except:
            print("User information format is wrong")

        user_ids.append(user_id)
        user_servers.append(user_server)

    coupons = read_info(coupon_path)

    for i, id in enumerate(user_ids):
        for coupon in coupons:
            message = use_coupon(user_id=id, user_server=user_servers[i], coupon=coupon)
            print(id, "+", coupon, ": ", message)
