from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from pathlib import Path
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from itertools import chain
import os
import time



def delete_old_file(file):
    if os.path.exists(file):
        os.remove(file)
    else:
        print("The file does not exist")

def configure_driver():
    # Add additional Options to the webdriver
    chrome_options = Options()
    # add the argument and make the browser Headless.
    chrome_options.add_argument("--headless")
    #finds and use local chromedriver
    d = Path(__file__).resolve().parents[0]
    driver = webdriver.Chrome(executable_path=str(d)+ "/chromedriver", options = chrome_options)
    return driver


def getData(driver,file,arrow_count):
    #Get Page
    driver.get(f"https://finance.yahoo.com/quote/%5EGSPC/history?period1=-1325635200&period2=1603929600&interval=1mo&filter=history&frequency=1mo&includeAdjustedClose=true")
    try:
        #Simulate Key Down to Load Entire Page
        actions = ActionChains(driver) 
        actions.send_keys(Keys.ARROW_DOWN * arrow_count)
        actions.perform()
    except TimeoutException:
        print("TimeoutException: Element not found")
        return None

    #Create a parse tree of page sources after searching
    soup = BeautifulSoup(driver.page_source, "lxml")
  
    #Find the table element
    table = soup.find('table')

    #Seperate Headers
    headerList=[]
    table_headers = table.find_all('th')
    for th in table_headers:
        col = th.find_all('span')
        row = [i.text for i in col]
        headerList.append(row)

    headerList=list(chain.from_iterable(headerList))
  
    #Seperate Rows
    rowList=[]
    table_rows = table.find_all('tr')
    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        rowList.append(row)

    #Emit CSV
    df = pd.DataFrame(rowList,columns=headerList)
    df.to_csv (file, index = False, header=True)
    return (df)

#Arrow Count Config (for test)
arrow_count=50000
#arrow_count=1
#FileName Config
file_name="data/SPHistory.csv"
#Get Start Time Timing
start_time = time.time()
#delete old file
delete_old_file(file_name)
# create the driver object.
driver = configure_driver()
#search_keyword = "Web Scraping"
df=getData(driver,file_name,arrow_count)
# close the driver.
driver.close()

#df= pd.read_csv(FileName)
print("Compete!!" +"\n\n" +
      "Rows Scraped:" + "\n" + 
      str(df.count()) +  "\n\n"  + 
      "Time Elapsed" +"\n" +
      "--- %s seconds ---" % round((time.time() - start_time),2)
        )

