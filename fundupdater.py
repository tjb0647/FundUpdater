#!/usr/bin/python

# coding: utf-8


# import libraries
from bs4 import BeautifulSoup
import urllib2
import sys, getopt
import csv
from datetime import datetime

#print ("the script has the name %s" % (sys.argv[0]))
# specify the url
quote_page ="http://www.maxfunds.com/funds/data.php?ticker="
quote_page = quote_page + sys.argv[1]
#print quote_page
# query the website and return the html to the variable ‘page’
page = urllib2.urlopen(quote_page).read()
# parse the html using beautiful soup and store in variable soup
soup = BeautifulSoup(page,"html.parser")

#print soup.prettify()

category = soup.find("span", {"class": "dataspan"})
exp_ratio = category.previous_element
category = category.text.strip()
maxrating = soup.find("span", {"class": "maxrating"})
maxrating = maxrating.text.strip()

#category = category_box.string.strip()
print "Category:" +category
print "Rating:" +maxrating
for item in soup.find_all("span", {"class": "dataspan"}):
    exp_ratio = item

exp_ratio = exp_ratio.text.strip()
print "Expense Ratio: " +exp_ratio

with open("/Users/tjb0647/Documents/Financials/Reports/Mutual Funds/funds.csv", "a") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow([sys.argv[1],category,maxrating,exp_ratio,datetime.now()])
