from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import requests
import time
from argparse import ArgumentParser


def scrap():
    parser = ArgumentParser()
    parser.add_argument('-a', help='Amount of posts to scrap')
    parser.add_argument('-o', help='Output path')
    parser.add_argument('-d', help='Driver path')
    parser.add_argument('--verbose', help='Print the scraped content',
                        action="store_true")
    parser.add_argument('--tag', help='Scrap tag', action="store_true")

    args = parser.parse_args()
    limit = 100 if args.a == None else int(args.a)
    opath = 'results' if args.o == None else args.o
    tag = False if args.tag == None else True
    verbose = False if args.verbose == None else True
    dpath = "chromedriver.exe" if args.d == None else args.d

    driver = webdriver.Chrome(dpath)
    time.sleep(1)
    driver.get('https://tiktok.com/')

    try:
        _ = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, ".//div[@class='tiktok-3g8031-DivVideoPlayerContainer e1bh0wg715']"))
        )
    finally:
        video = driver.find_element(
            by=By.XPATH, value=".//div[@class='tiktok-3g8031-DivVideoPlayerContainer e1bh0wg715']")
        video.click()

    time.sleep(1)
    chkL = 0
    cpt = False
    print("Waiting for CAPTCHA screen...")
    while(True):
        try:
            _ = driver.find_element(
                by=By.XPATH, value=".//div[@class='captcha_verify_container style__CaptchaWrapper-sc-1gpeoge-0 zGYIR']")
            cpt = True
            if(chkL == 0):
                print("Solve CAPTCHA on browser to continue")
            chkL += 1
        except NoSuchElementException:
            if (cpt):
                break

    record = ""
    for i in range(limit):
        try:
            author = driver.find_element(
                by=By.XPATH, value=".//span[@class='tiktok-1r8gltq-SpanUniqueId evv7pft1']")
            author_string = author.text.strip()
        except NoSuchElementException:
            print('author not found')
            author_string = "[Author not found]"

        labels = driver.find_elements(
            by=By.XPATH, value=".//span[@class='tiktok-j2a19r-SpanText efbd9f0']")
        label_text = [label.text.strip()
                      for label in filter(lambda l: l.text.strip() != "", labels)]
        label_string = "".join(label_text) if len(
            label_text) > 0 else "[Label not found]"

        tags = driver.find_elements(
            by=By.XPATH, value=".//strong[@class='tiktok-f9vo34-StrongText ejg0rhn1']")
        tag_text = [tag.text.strip()
                    for tag in filter(lambda l: l.text.strip() != "", tags)]
        tag_string = ", ".join(tag_text)

        try:
            video = driver.find_element(by=By.TAG_NAME, value="video")
            video_url = video.get_attribute('src')

            response = requests.get(video_url)
            open(f"{opath}/v{i} ({author_string}).mp4",
                 "wb").write(response.content)

            rec = author_string + ", " + label_string
            if(tag):
                rec += ", " + tag_string
            record += rec + "\n"

            if(verbose):
                print(rec + ": " + video_url[:50], end='\n')
        except:
            print("Get video failed", end='\n')

        try:
            button = driver.find_element(
                by=By.XPATH, value=".//button[@class='tiktok-2xqv0y-ButtonBasicButtonContainer-StyledVideoSwitchV2 e11s2kul15' and @data-e2e='arrow-right']")
            button.click()
        except NoSuchElementException:
            print('Scrap terminated')
            break
        time.sleep(0.2)

    f = open(f"{opath}/details.csv", "w", encoding="utf-8")
    f.write(record)
    f.close()


if __name__ == "__main__":
    scrap()
