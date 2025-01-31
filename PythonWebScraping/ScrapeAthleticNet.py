from bs4 import BeautifulSoup
import requests
import time
import json
from collections import defaultdict
import re

def toHTML(text):
    with open("template.html", 'r') as file:
        lines = file.readlines()

    lines.insert(40, text + '\n')

    with open("Index.html", 'w') as file:
        file.writelines(lines)


def timeToSec(raceTime):
    result = 0
    # remove "pr"
    if raceTime[-2:] == "PR":
        raceTime = raceTime[:-2]
    if (raceTime == "DNF" or raceTime == ""):
        return 1000000

    #split into hours, mins and seconds
    splitTime = raceTime.split(":")
    splitTime.reverse()
    # multiply reversed list by powers of 60 to convert to seconds
    for i in range(len(splitTime)):
        if splitTime[i] != '':
            result += float(splitTime[i]) * pow(60, i)
    return int(result)

def schoolAttributes(soup):
    # get the school attributes
    attrTag = soup.find('script', type='application/ld+json')
    # Extract and parse the JSON content
    json_data = json.loads(attrTag.string)
    # Extract name values from the itemListElement
    names = [item['name'] for item in json_data['itemListElement'] if 'name' in item]
    return names

# given athletic.net soup extract the performances from the html
# return a list of the times that would be in the top list (faster than the slowest time in the top list)
def extractPerform(soup):
    result = list()
    # get each event from the soup
    events = soup.find_all('div', class_='distance')
    # if there are avaliable events extract the individual performances
    if (events != None):
        for event in events:
            # get the name of the event
            distance = event.find('h3', class_='mt-2').contents[0].strip()

            # divide up each gender
            identities = event.find_all('h4')
            tables = event.find_all('table')

            j = 0
            # two tables per event
            for table in tables:
                #print("---------------------------------------------------------------------------------------------------------")
                # pair identity with the table 
                identity = identities[j].get_text(strip=True)
                rows = table.find_all('tr')

                # get all of their season best data
                for row in rows:
                    # find each td in the row
                    tds = row.find_all('td')
                    # concatenate the persons information into an array
                    rowText = [td.get_text(strip=True) for td in tds]
                    # get the link to each meet and add to rowText
                    urls = re.split(r'href="', str(tds))
                    link = "https://www.athletic.net" + urls[-1][0:urls[-1].find("\"")]
                    rowText.append(link)
                    rowText[0] = identity
                
                    #convert the race time to seconds for easier sorting
                    raceTime = rowText[3]
                    raceTime = timeToSec(raceTime)
                    #if avaliable make a key for the dictionary ex. "Mens College 8,000M"
                    attr = schoolAttributes(soup)
                    if len(attr) <= 3:
                        break
                    key = rowText[0] + " " + attr[3] + " " + distance + "\t"

                    #get the list associated with the key add the new time and remove the slowest
                    currList = topLists[key]
                    currList.append((raceTime, "<td>" + "</td><td>".join(rowText[1:-2]) + "</td>" \
                                    "<td><a target=\"_blank\" href=\"" + rowText[-1] + "\"><button class = \"button\" >" \
                                    + rowText[-2] + "</button></a></td>" ))
                    currList.sort()
                    if len(currList) > 10:
                        currList.pop()
                j+=1   
 
        textOut = ""
        keysToUse = ["Mens High School 5,000 Meters\t", "Mens High School 3 Miles\t", "Womens High School 5,000 Meters\t", "Womens High School 3 Miles\t"]
        if (i % 10 == 0):
            #print("##################################################################################################### " + str(i))
            for keyI in keysToUse:
                k =0
                for item in topLists[keyI]:
                    textOut = textOut + ("<tr><td>" + str(k+1) + ". </td><td>" + keyI + "</td>" + item[1] + "</tr>" + "\n")
                    k += 1
                textOut = textOut + "<tr><td class=\"bordered\" colspan=\"7\"></td></tr>\n"
            toHTML(textOut)
                    
                
    return

topLists = defaultdict(list)
for i in range(50000):
    print(i)
    # sleep as to not get banned for excessive requests
    #time.sleep(0.1)
    # parse html for the school
    response = requests.get("https://www.athletic.net/CrossCountry/seasonbest?SchoolID=" + str(i) + "&S=2024")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # make sure that the school id is valid
    title = soup.title.string
    if (title != '\r\n\tTrack & Field, Cross Country Results, Statistics\r\n'):
        # if it is valid, get each person and their time from the table
        extractPerform(soup)

print("-----Ended-----")

