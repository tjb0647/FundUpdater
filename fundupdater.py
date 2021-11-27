#!/usr/bin/python3
# coding: utf-8

# run this to download mutual fund and etf information from morning morningstar
# this should not be used with stocks, bonds, or single fund etfs

# import libraries
from bs4 import BeautifulSoup
import urllib.request as urllib2
import sys, getopt
import csv
from datetime import datetime
import re
import pandas as pd
from selenium import webdriver
import time

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
    if type == 'all':
        # maxfunds information
        quote_page ="http://www.maxfunds.com/funds/data.php?ticker="
        Fund.quote_page = quote_page + Fund.ticker
        # query the website and return the html to the variable ‘page’
        page = urllib2.urlopen(Fund.quote_page).read()
        # parse the html using beautiful soup and store in variable soup
        Fund.soup = BeautifulSoup(page,"html.parser")
        #print soup.prettify()
        Fund.category = Fund.soup.find("span", {"class": "dataspan"})
        exp_ratio = Fund.category.previous_element
        Fund.category = Fund.category.text.strip()
        maxrating = Fund.soup.find("span", {"class": "maxrating"})
        maxrating = maxrating.text.strip()
        Fund.asof = Fund.soup.find("span", {"class": "asof"}).text.strip()
        #category = category_box.string.strip()
        Fund.maxrating = maxrating

        for item in Fund.soup.find_all("span", {"class": "dataspan"}):
            exp_ratio = item
        Fund.exp_ratio = exp_ratio.text.strip()
    else:
        # morningstar information
        driver = webdriver.Safari()
        urlpage = "https://www.morningstar.com/funds/xnas/" + Fund.ticker + "/portfolio"
        if Fund.type == 'etf':
            urlpage = "https://www.morningstar.com/etfs/arcx/" + Fund.ticker + "/portfolio"
        driver.get(urlpage)
        driver.implicitly_wait(30)
        btn = driver.find_element_by_id('styleWeight')
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
        d = {'ticker': [Fund.ticker],
            'U.S. Equity' : float(assetclass['U.S. Equity'])/100 if Fund.type != 'bond' else None,
            'Non-U.S. Equtiy': float(assetclass['Non-U.S. Equity'])/100 if Fund.type != 'bond' else None,
            'Fixed Income': float(assetclass['Fixed Income'])/100 if Fund.type != 'bond' else None,
            'Other': float(assetclass['Other'])/100 if Fund.type != 'bond' else None,
            'Cash' : float(assetclass['Cash'])/100 if Fund.type != 'bond' else None,
            'Not Classified': float(assetclass['Not Classified'])/100 if Fund.type != 'bond' else None,
            'Large Value': [float(re.search(r'Large Value (\d*\.?\d*)',stock_style).groups()[0])/100],
            'Large Blend': [float(re.search(r'Large Blend (\d*\.?\d*)',stock_style).groups()[0])/100],
            'Large Growth': [float(re.search(r'Large Growth (\d*\.?\d*)',stock_style).groups()[0])/100],
            'Medium Value': [float(re.search(r'Medium Value (\d*\.?\d*)',stock_style).groups()[0])/100],
            'Medium Blend': [float(re.search(r'Medium Blend (\d*\.?\d*)',stock_style).groups()[0])/100],
            'Medium Growth': [float(re.search(r'Medium Growth (\d*\.?\d*)',stock_style).groups()[0])/100],
            'Small Value': [float(re.search(r'Small Value (\d*\.?\d*)',stock_style).groups()[0])/100],
            'Small Blend': [float(re.search(r'Small Blend (\d*\.?\d*)',stock_style).groups()[0])/100],
            'Small Growth': [float(re.search(r'Small Growth (\d*\.?\d*)',stock_style).groups()[0])/100],
            'Basic Materials': [float(re.search(r'Basic Materials (\d*\.?\d*)',sectors).groups()[0])/100],
            'Consumer Cyclical':[float(re.search(r'Consumer Cyclical (\d*\.?\d*)',sectors).groups()[0])/100],
            'Financial Services': [float(re.search(r'Financial Services (\d*\.?\d*)',sectors).groups()[0])/100],
            'Real Estate': [float(re.search(r'Real Estate (\d*\.?\d*)',sectors).groups()[0])/100],
            'Communication Services': [float(re.search(r'Communication Services (\d*\.?\d*)',sectors).groups()[0])/100],
            'Energy': [float(re.search(r'Energy (\d*\.?\d*)',sectors).groups()[0])/100],
            'Industrials': [float(re.search(r'Industrials (\d*\.?\d*)',sectors).groups()[0])/100],
            'Technology': [float(re.search(r'Technology (\d*\.?\d*)',sectors).groups()[0])/100],
            'Consumer Defensive': [float(re.search(r'Consumer Defensive (\d*\.?\d*)',sectors).groups()[0])/100],
            'Healthcare': [float(re.search(r'Healthcare (\d*\.?\d*)',sectors).groups()[0])/100],
            'Utilities': [float(re.search(r'Utilities (\d*\.?\d*)',sectors).groups()[0])/100],
            'Date': [(re.search(r'of (...+)', sectors_footer.split("|")[0]).groups()[0]).strip()]}
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

def main():
    funds = grabfunds(FUND_LIST)
    funds.to_csv('history.csv')
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
    btn = driver.find_element_by_id('styleWeight')
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
    re.search(r'Large Value (\d*\.?\d*)',stock_style).groups()[0]

    d = {'ticker': [Fund.ticker],
        'U.S. Equity' : float(assetclass['U.S. Equity'])/100 if Fund.type != 'bond' else None,
        'Non-U.S. Equtiy': float(assetclass['Non-U.S. Equity'])/100 if Fund.type != 'bond' else None,
        'Fixed Income': float(assetclass['Fixed Income'])/100 if Fund.type != 'bond' else None,
        'Other': float(assetclass['Other'])/100 if Fund.type != 'bond' else None,
        'Cash' : float(assetclass['Cash'])/100 if Fund.type != 'bond' else None,
        'Not Classified': float(assetclass['Not Classified'])/100 if Fund.type != 'bond' else None,
        'Large Value': [float(re.search(r'Large Value (\d*\.?\d*)',stock_style).groups()[0])/100],
        'Large Blend': [float(re.search(r'Large Blend (\d*\.?\d*)',stock_style).groups()[0])/100],
        'Large Growth': [float(re.search(r'Large Growth (\d*\.?\d*)',stock_style).groups()[0])/100],
        'Medium Value': [float(re.search(r'Medium Value (\d*\.?\d*)',stock_style).groups()[0])/100],
        'Medium Blend': [float(re.search(r'Medium Blend (\d*\.?\d*)',stock_style).groups()[0])/100],
        'Medium Growth': [float(re.search(r'Medium Growth (\d*\.?\d*)',stock_style).groups()[0])/100],
        'Small Value': [float(re.search(r'Small Value (\d*\.?\d*)',stock_style).groups()[0])/100],
        'Small Blend': [float(re.search(r'Small Blend (\d*\.?\d*)',stock_style).groups()[0])/100],
        'Small Growth': [float(re.search(r'Small Growth (\d*\.?\d*)',stock_style).groups()[0])/100],
        'Basic Materials': [float(re.search(r'Basic Materials (\d*\.?\d*)',sectors).groups()[0])/100],
        'Consumer Cyclical':[float(re.search(r'Consumer Cyclical (\d*\.?\d*)',sectors).groups()[0])/100],
        'Financial Services': [float(re.search(r'Financial Services (\d*\.?\d*)',sectors).groups()[0])/100],
        'Real Estate': [float(re.search(r'Real Estate (\d*\.?\d*)',sectors).groups()[0])/100],
        'Communication Services': [float(re.search(r'Communication Services (\d*\.?\d*)',sectors).groups()[0])/100],
        'Energy': [float(re.search(r'Energy (\d*\.?\d*)',sectors).groups()[0])/100],
        'Industrials': [float(re.search(r'Industrials (\d*\.?\d*)',sectors).groups()[0])/100],
        'Technology': [float(re.search(r'Technology (\d*\.?\d*)',sectors).groups()[0])/100],
        'Consumer Defensive': [float(re.search(r'Consumer Defensive (\d*\.?\d*)',sectors).groups()[0])/100],
        'Healthcare': [float(re.search(r'Healthcare (\d*\.?\d*)',sectors).groups()[0])/100],
        'Utilities': [float(re.search(r'Utilities (\d*\.?\d*)',sectors).groups()[0])/100],
        'Date': [(re.search(r'of (...+)', sectors_footer.split("|")[0]).groups()[0]).strip()]}
    Fund.sectors = pd.DataFrame(data=d)
if __name__ == '__main__':
    main()
