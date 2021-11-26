#!/usr/bin/python3.7
# coding: utf-8


# import libraries
from bs4 import BeautifulSoup
import urllib.request as urllib2
import sys, getopt
import csv
from datetime import datetime
import re
import pandas as pd
from selenium import webdriver

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

#with open("/Users/tjb0647/Documents/Financials/Reports/Mutual Funds/funds.csv", "a") as csv_file:
#    writer = csv.writer(csv_file)
#    writer.writerow([sys.argv[1],category,maxrating,exp_ratio,datetime.now()])

def grabinfo(Fund,type=None):
    print( "Fund: " + Fund.ticker)
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
        driver.implicitly_wait(5)
        sectors = driver.find_element_by_class_name("sal-sector-exposure__sector-table").text
        sectors_footer = driver.find_element_by_class_name("sal-sector-exposure__sector-footer").text
        driver.quit()
        d = {'ticker': [Fund.ticker],
            'Basic Materials': [re.search(r'Basic Materials (\d*\.?\d*)',sectors).groups()[0]],
            'Consumer Cyclical':[re.search(r'Consumer Cyclical (\d*\.?\d*)',sectors).groups()[0]],
            'Financial Services': [re.search(r'Financial Services (\d*\.?\d*)',sectors).groups()[0]],
            'Real Estate': [re.search(r'Real Estate (\d*\.?\d*)',sectors).groups()[0]],
            'Communication Services': [re.search(r'Communication Services (\d*\.?\d*)',sectors).groups()[0]],
            'Energy': [re.search(r'Energy (\d*\.?\d*)',sectors).groups()[0]],
            'Industrials': [re.search(r'Industrials (\d*\.?\d*)',sectors).groups()[0]],
            'Technology': [re.search(r'Technology (\d*\.?\d*)',sectors).groups()[0]],
            'Consumer Defensive': [re.search(r'Consumer Defensive (\d*\.?\d*)',sectors).groups()[0]],
            'Healthcare': [re.search(r'Healthcare (\d*\.?\d*)',sectors).groups()[0]],
            'Utilities': [re.search(r'Utilities (\d*\.?\d*)',sectors).groups()[0]],
            'Date': [sectors_footer]}
        Fund.sectors = pd.DataFrame(data=d)
    return Fund

def grabfunds(fundlist):
    if len(fundlist)>0:
        df = pd.DataFrame()
        for fund in fund_list:
            df1 = grabinfo(Fund(fund,type=fund_list[fund])).sectors
            df = df.append(df1)
        df.set_index('ticker',inplace=True)
        print(df.transpose())
        return df.transpose()
    pass


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


def main():
    funds = grabfunds(FUND_LIST)
    funds.to_csv('sectors.csv')
    pass

if __name__ == '__main__':
    main()
