import re
from bs4 import BeautifulSoup
import lxml
import requests

# param   - html of results page
# return  - void
# adds the results to database
def extractResults():
    return 0

def main():
    # create a BeautifulSoup object from the html parsed
    soup = BeautifulSoup(requests.get("https://tfrrs.org/results.rss").text, features="xml")

    # get a list of all of all links to recent meets in the html
    links = soup.find_all("link")
    for i in range(len(links)):
        links[i] = links[i].text.strip()
    # the first link references the site we're on(tfrrs.org/results.rss), so remove it
    links.pop(0)

    # get links for the mens and womens compiled results of each meet
    # all links to results pages are stored in compiled_results_link
    compiled_results_link = list()
    for link in links:
        bs4_link = BeautifulSoup(requests.get(link).text, features="xml")
        two_links = (bs4_link.find("span", class_="panel-heading-normal-text")).find_all("a")
        for link in two_links:
            compiled_results_link.append(link.get("href"))
    
    for link in compiled_results_link:
        
        
    
        


    # for each meet extract data
    #for 

main()