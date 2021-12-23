#!/usr/bin/python3
# coding: utf-8

# run this to download mutual fund and etf information from morning morningstar
# this should not be used with stocks, bonds, or single fund etfs

# import libraries
from bs4 import BeautifulSoup
import urllib.request as urllib2
import csv
from datetime import datetime
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os.path

HISTORY = 'history.csv'
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

def grabinfo(Fund,type=None):
    # morningstar information
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
    return Fund

def grabfunds(fundlist):
    if len(fundlist)>0:
        df = pd.DataFrame()
        print('Getting ',len(fundlist), ' funds...')
        i = 1
        for fund in fundlist:
            print (fund, " - ", i, " of ", len(fundlist))
            df1 = grabinfo(Fund(fund,type=fundlist[fund])).sectors
            df = df.append(df1)
            i = i + 1
        df.set_index('ticker',inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        print(df.transpose())
        return df
    pass

def append_history(funds):
    if os.path.exists(HISTORY):
        df = pd.read_csv(HISTORY).set_index('ticker')
        merged = pd.concat([funds,df])
        funds = merged.drop_duplicates()
    funds.to_csv(HISTORY)
    pass

def main():
    funds = grabfunds(FUND_LIST)
    append_history(funds)
    funds.transpose().to_csv('sectors.csv')
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
