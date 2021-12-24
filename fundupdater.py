#!/usr/bin/python3
# coding: utf-8

# run this to download mutual fund and etf information from morning morningstar
# this should not be used with stocks, bonds, or single fund etfs

# selenium needs chrome installed in MacOS
# also needs https://sites.google.com/chromium.org/driver/downloads
# copied into /usr/local/bin/   as chromedriver

# import libraries

import urllib.request as urllib2
import csv, re, time, os.path
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
#pip3 install webdriver_manager
from webdriver_manager.chrome import ChromeDriverManager

# user INPUT
FUND_LIST = dict([
            ('FCPGX', 'mutual'),
            ('FIENX', 'mutual'),
            ('FMIJX', 'mutual'),
            ('FDMO' , 'etf'),
            ('SCHV' , 'etf'),
            ('FNCMX', 'mutual'),
            ('FSRNX', 'mutual'),
            ('FSSNX', 'mutual'),
            ('GTLOX', 'mutual'),
            ('JAENX', 'mutual'),
            ('TLZIX', 'mutual'),
            ('VFIAX', 'mutual'),
            ('VINIX', 'mutual'),
            ('VTIAX', 'mutual')
            ])
# configuration
HISTORY = 'history.csv'
STOCK_STYLES = [
    'Large Value',
    'Large Blend',
    'Large Growth',
    'Medium Value',
    'Medium Blend',
    'Medium Growth',
    'Small Value',
    'Small Blend',
    'Small Growth'
    ]
SECTORS = [
    'Basic Materials',
    'Consumer Cyclical',
    'Financial Services',
    'Real Estate',
    'Communication Services',
    'Energy',
    'Industrials',
    'Technology',
    'Consumer Defensive',
    'Healthcare',
    'Utilities'
    ]

class Fund(object):
    """docstring for Fund."""
    def __init__(self, ticker, category=None, exp_ratio=None, maxrating=None, quote_page=None, asof = None, type='mutual'):
        super(Fund, self).__init__()
        self.ticker = ticker
        self.category = category
        self.exp_ratio = exp_ratio
        self.maxrating = maxrating
        self.quote_page = quote_page
        self.asof = asof
        self.type = type

def main():
    funds = grabfunds(FUND_LIST)
    append_history(funds)
    funds.transpose().to_csv('sectors.csv')
    pass

def grabfunds(fundlist):
    if len(fundlist)>0:
        df = pd.DataFrame()
        driver = initiate_browser()
        print('Getting ',len(fundlist), ' funds...')
        i = 1
        for fund in fundlist:
            print (fund, " - ", i, " of ", len(fundlist))
            df1 = grabinfo(Fund(fund,type=fundlist[fund]),driver=driver).sectors
            df = df.append(df1)
            i = i + 1
        driver.quit()
        df.set_index('ticker',inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        print(df.transpose())
        return df
    pass

def initiate_browser():
    # instantiate a chrome options object so you can set the size and headless preference
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def grabinfo(Fund,type=None, driver=initiate_browser()):
    urlpage = "https://www.morningstar.com/funds/xnas/" + Fund.ticker + "/portfolio"
    if Fund.type == 'etf':
        urlpage = "https://www.morningstar.com/etfs/arcx/" + Fund.ticker + "/portfolio"
    driver.get(urlpage)
    driver.implicitly_wait(30)
    btn = driver.find_element(By.ID,'styleWeight')
    driver.execute_script("arguments[0].click();",btn)
    time.sleep(2)
    sectors = driver.find_element(By.CLASS_NAME,"sal-sector-exposure__sector-table").text
    sectors_footer = driver.find_element(By.CLASS_NAME,"sal-sector-exposure__sector-footer").text
    soup = BeautifulSoup(driver.page_source,features="lxml")
    assetclass = pd.read_html(str(soup.find_all("table")[0]))[0]
    assetclass.set_index('Asset Class', inplace=True)
    if 'Net' in assetclass.columns:
        assetclass = assetclass['Net']
    elif 'Investment' in assetclass.columns:
        assetclass = assetclass['Investment']
    # sectors table...
    # pd.read_html(str(soup.find_all("table")[4]))[0]
    stock_style = driver.find_element(By.CLASS_NAME,"sr-only").text
    # driver.quit()
    dstyles = dsectors = {}
    for style in STOCK_STYLES:
        regex = style + " (\d*\.?\d*)"
        dstyles[style] = float(re.search(regex,stock_style).groups()[0])/100
    for sec in SECTORS:
        regex = sec + " (\d*\.?\d*)"
        dsectors[sec] = float(re.search(regex,sectors).groups()[0])/100
    d = {'ticker': [Fund.ticker],
        'U.S. Equity' : float(assetclass['U.S. Equity'])/100 if Fund.type != 'bond' else None,
        'Non-U.S. Equtiy': float(assetclass['Non-U.S. Equity'])/100 if Fund.type != 'bond' else None,
        'Fixed Income': float(assetclass['Fixed Income'])/100 if Fund.type != 'bond' else None,
        'Other': float(assetclass['Other'])/100 if Fund.type != 'bond' else None,
        'Cash' : float(assetclass['Cash'])/100 if Fund.type != 'bond' else None,
        'Not Classified': float(assetclass['Not Classified'])/100 if Fund.type != 'bond' else None,
        }
    d.update(dstyles)
    d.update(dsectors)
    d['Date'] = (re.search(r'of (...+)', sectors_footer.split("|")[0]).groups()[0]).strip()
    Fund.sectors = pd.DataFrame(data=d)
    return Fund

def append_history(funds):
    if os.path.exists(HISTORY):
        df = pd.read_csv(HISTORY).set_index('ticker')
        merged = pd.concat([funds,df])
        merged['Date'] = pd.to_datetime(merged['Date'])
        merged.reset_index(inplace=True)
        merged['ticker'] = merged['ticker'].astype('str')
        funds = merged.drop_duplicates(subset=['ticker','Date'])
        funds.set_index('ticker',inplace=True)
    funds.sort_values(by=['ticker', 'Date'],ascending=[True,False]).to_csv(HISTORY)
    pass


def test():
    F = grabinfo(Fund('FIENX',type = 'mutual'))
    F.sectors
    F.sectors.dtypes

    Fund.ticker = "FIENX"
    Fund.type = "mutual"
    driver = webdriver.Safari()
    urlpage = "https://www.morningstar.com/funds/xnas/" + Fund.ticker + "/portfolio"
    if Fund.type == 'etf':
        urlpage = "https://www.morningstar.com/etfs/arcx/" + Fund.ticker + "/portfolio"
    driver.get(urlpage)
    driver.implicitly_wait(30)
    btn = driver.find_element(By.ID,'styleWeight')
    driver.execute_script("arguments[0].click();",btn)
    time.sleep(4)
    # assetclass = driver.find_element_by_class_name("sal-columns sal-small-12 sal-asset-allocation__assetTable sal-medium-8")
    sectors = driver.find_element_by_class_name("sal-sector-exposure__sector-table").text
    sectors_footer = driver.find_element_by_class_name("sal-sector-exposure__sector-footer").text
    soup = BeautifulSoup(driver.page_source,features="lxml")
    assetclass = pd.read_html(str(soup.find_all("table")[0]))[0]
    assetclass.set_index('Asset Class', inplace=True)
    if 'Net' in assetclass.columns:
        assetclass = assetclass['Net']
    elif 'Investment' in assetclass.columns:
        assetclass = assetclass['Investment']
    # sectors table...
    # pd.read_html(str(soup.find_all("table")[4]))[0]
    stock_style = driver.find_element_by_class_name("sr-only").text
    driver.quit()

    dstyles = dsectors = {}
    for style in STOCK_STYLES:
        regex = style + " (\d*\.?\d*)"
        dstyles[style] = float(re.search(regex,stock_style).groups()[0])/100
    for sec in SECTORS:
        regex = sec + " (\d*\.?\d*)"
        dsectors[sec] = float(re.search(regex,sectors).groups()[0])/100
    d = {'ticker': [Fund.ticker],
        'U.S. Equity' : float(assetclass['U.S. Equity'])/100 if Fund.type != 'bond' else None,
        'Non-U.S. Equtiy': float(assetclass['Non-U.S. Equity'])/100 if Fund.type != 'bond' else None,
        'Fixed Income': float(assetclass['Fixed Income'])/100 if Fund.type != 'bond' else None,
        'Other': float(assetclass['Other'])/100 if Fund.type != 'bond' else None,
        'Cash' : float(assetclass['Cash'])/100 if Fund.type != 'bond' else None,
        'Not Classified': float(assetclass['Not Classified'])/100 if Fund.type != 'bond' else None,
        }
    d.update(dstyles)
    d.update(dsectors)
    d['Date'] = (re.search(r'of (...+)', sectors_footer.split("|")[0]).groups()[0]).strip()
    Fund.sectors = pd.DataFrame(data=d)

if __name__ == '__main__':
    main()
