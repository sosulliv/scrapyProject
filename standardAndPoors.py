# pluralsight.py
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from pathlib import Path
#import time
import pandas as pd
#from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from itertools import chain


def configure_driver():
    # Add additional Options to the webdriver
    chrome_options = Options()
    # add the argument and make the browser Headless.
    chrome_options.add_argument("--headless")
    # Instantiate the Webdriver: Mention the executable path of the webdriver you have downloaded
    # For linux/Mac
    # driver = webdriver.Chrome(options = chrome_options)
    # For windows
    d = Path(__file__).resolve().parents[0]
    print("hello")
    print(str(d)+ "/chromedriver")
    driver = webdriver.Chrome(executable_path=str(d)+ "/chromedriver", options = chrome_options)
    #driver = webdriver.Chrome(executable_path="./chromedriver.exe", options = chrome_options)
    return driver


def getCourses(driver, search_keyword):
    # Step 1: Go to pluralsight.com, category section with selected search keyword
    driver.get(f"https://finance.yahoo.com/quote/%5EGSPC/history?period1=-1325635200&period2=1603929600&interval=1mo&filter=history&frequency=1mo&includeAdjustedClose=true")
    # wait for the element to load
    try:
        #WebDriverWait(driver, 10).until(lambda s: s.find_element_by_xpath("//option[@value='Dec 01, 1927']").is_displayed())
        #lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        #match=False
        #while(match==False):
         #       lastCount = lenOfPage
          #      time.sleep(5)
           #     lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            #    if lastCount==lenOfPage:
             #       match=True
        actions = ActionChains(driver) 
        actions.send_keys(Keys.ARROW_DOWN * 50000)
        actions.perform()
    except TimeoutException:
        print("TimeoutException: Element not found")
        return None

    # Step 2: Create a parse tree of page sources after searching
    soup = BeautifulSoup(driver.page_source, "lxml")
    #print(soup)
    #rows=soup.findAll("tr")

   # headers=soup.findAll("th")
    #for header in headers:
     #   print(header)

    table = soup.find('table')

    headerList=[]
    table_headers = table.find_all('th')
    for th in table_headers:
        col = th.find_all('span')
        row = [i.text for i in col]
        headerList.append(row)

    headerList=list(chain.from_iterable(headerList))
    #print(headerList)

    rowList=[]
    table_rows = table.find_all('tr')
    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        rowList.append(row)

    df = pd.DataFrame(rowList,columns=headerList)
    df.to_csv ('sandp.csv', index = False, header=True)


# create the driver object.
driver = configure_driver()
search_keyword = "Web Scraping"
getCourses(driver, search_keyword)
# close the driver.
driver.close()