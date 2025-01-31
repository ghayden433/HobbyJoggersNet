from bs4 import BeautifulSoup
import re
import requests
import pandas as pd
import toSQL

for i in range(50000):
    try:
        if (i % 100) == 0:
            print(str((i/50000) * 100) + '%')
        # request page from athletic.net
        response = requests.get("https://www.athletic.net/CrossCountry/seasonbest?SchoolID=" + str(i) + "&S=2024")
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # get the year of sport, given the link for response is 2024
        year = "2024" 

        # get the season of the sport, given the link for response is cross country only
        season = "Cross Country"

        # get the level, high school or college
        PageInfoTag = soup.find_all('script', type='text/javascript')
        if len(PageInfoTag) >= 3:
            level = re.search("College|High School", PageInfoTag[3].get_text())
        if level:
            level = level.group()
        else:
            #print("No Level Found.")
            continue


        # loops through each nested part of the table to assemble rows of info to be added to a dataframe
        distances = soup.select('.distance')

        for distance in distances:
            distanceTemp = distance.find('h3').contents[0].get_text() # contents is becuase the tag has other nested elements to be removed
            relevantDistances = ["5,000 Meters", "3 Miles", "8,000 Meters", "10,000 Meters", "6,000 Meters"]
            # only do the relevant distances, if its not relevant, move to next distance
            if (distanceTemp not in relevantDistances):
                continue
            genders = distance.select('div[id^="M_"], div[id^="F_"]')
            for gender in genders:
                # create dataframe to store the event, to be passed to the Mysql database
                columns = ['Season', 'Gender', 'Level', 'Event', 'Name', 'Grade', 'Mark', 'PerformanceDate', 'Results']
                newTimes = pd.DataFrame(columns=columns)

                # convert the html into just the raw titles so they can be a part of the row
                genderTemp = re.search("Mens|Womens", gender.find('h4').get_text()).group()
                # create the first part of the output row, it is the same for each input row from this point
                eventInfo = [season, genderTemp, level, distanceTemp]
                rows = gender.find_all("tr")
                for row in rows:
                    items = eventInfo + [tag.get_text() for tag in row.find_all("td")]
                    items.pop(4)

                    #formatting the rows for the way the databes is organized
                    link, grade, name, mark = -1, 4, 5, 6
                    items[name], items[grade] = items[grade], items[name]
                    items[mark] = items[mark].replace("PR", "")
                    items[link] = 'https://athletic.net' + row.find_all('a')[-1].get('href')
                    newTimes.loc[len(newTimes)] = items

                toSQL.df_to_MySQL(newTimes, season, genderTemp, level, distanceTemp, year)
    except:
        continue
    



