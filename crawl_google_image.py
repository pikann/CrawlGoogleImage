import sys
import time
import csv
import urllib.parse as urlparse
from urllib.parse import parse_qs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException


def search(key_word, driver_path):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')

    driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

    print("Search image with key word: " + key_word)

    url = "https://www.google.com.vn/imghp"
    driver.get(url)

    timeout = 5
    try:
        element_present = EC.presence_of_element_located((By.XPATH, "//input[@class='gLFyf gsfi']"))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        raise Exception("Timed out waiting for page to load")

    search_box = driver.find_element(By.XPATH, "//input[@class='gLFyf gsfi']")
    search_box.send_keys(key_word)
    search_box.send_keys(Keys.ENTER)

    try:
        element_present = EC.presence_of_element_located((By.XPATH, "//div[@class='isv-r PNCib MSM1fd BUooTd']"))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        raise Exception("Timed out waiting for page to load")

    return driver


def load_image(driver):
    print("Loading image")
    image_number_previous = 0

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        image_number = len(driver.find_elements(By.XPATH, "//div[@class='isv-r PNCib MSM1fd BUooTd']"))

        wait_count = 0

        try:
            while image_number == image_number_previous:
                image_number = len(driver.find_elements(By.XPATH, "//div[@class='isv-r PNCib MSM1fd BUooTd']"))
                wait_count += 1
                time.sleep(1)

                if wait_count >= 5:
                    show_more_btn = driver.find_element(By.XPATH, "//input[@class='mye4qd']")
                    show_more_btn.click()
                    break
        except ElementNotInteractableException:
            break

        print("Loaded " + str(image_number) + " images!")

        image_number_previous = image_number


def save_image_url(driver, writer):
    print("Save image url")
    for i in range(len(driver.find_elements(By.XPATH, "//div[@class='isv-r PNCib MSM1fd BUooTd']"))):
        image_block = driver.find_elements(By.XPATH, "//div[@class='isv-r PNCib MSM1fd BUooTd']")[i]

        image_block.find_element(By.XPATH, ".//a[@class='wXeWr islib nfEiy']").click()

        image_block = driver.find_elements(By.XPATH, "//div[@class='isv-r PNCib MSM1fd BUooTd']")[i]

        image_url_attribute = image_block.find_element(By.XPATH, ".//a[@class='wXeWr islib nfEiy']").get_attribute('href')
        parsed = urlparse.urlparse(image_url_attribute)

        image_url = parse_qs(parsed.query)['imgurl'][0]

        writer.writerow([i, image_url])
        print(str(i) + ": " + image_url)


if __name__ == "__main__":
    opts = [opt for opt in sys.argv[1:] if opt.startswith("--")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if "--keyword" in opts:
        key_word = args[opts.index("--keyword")]
    else:
        raise Exception("Keyword not found")
    if "--driver" in opts:
        driver_path = args[opts.index("--driver")]
    else:
        raise Exception("Driver not found")

    file = open(key_word + '.csv', mode='w')
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    driver = search(key_word, driver_path)
    load_image(driver)
    save_image_url(driver, writer)
