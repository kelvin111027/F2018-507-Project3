import sqlite3
import csv
import json

# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data from CSV and JSON into a new database called choc.db
DBNAME = 'choc.db'
BARSCSV = 'flavors_of_cacao_cleaned.csv'
COUNTRIESJSON = 'countries.json'

def create_populate_Countries():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = '''
       DROP TABLE IF EXISTS 'Countries';
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Countries'(
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Alpha2' TEXT,
            'Alpha3' TEXT,
            'EnglishName' TEXT,
            'Region' TEXT,
            'Subregion' TEXT,
            'Population' INTEGER,
            'Area' REAL
        );
    '''
    cur.execute(statement)
    conn.commit()

    #open and read json file
    with open(COUNTRIESJSON, encoding = 'utf-8') as countries_file:
        countries_lst = json.load(countries_file)
    countries_file.close()
    for c in countries_lst:
        insertion = (None, c['alpha2Code'], c['alpha3Code'], c['name'], c['region'], c['subregion'], c['population'], c['area'])
        statement = 'INSERT INTO "Countries"'
        statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)
    conn.commit()
    conn.close()


def create_populate_Bars():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = '''
        DROP TABLE IF EXISTS 'Bars';
    '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE 'Bars'(
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Company' TEXT NOT NULL,
            'SpecificBeanBarName' TEXT NOT NULL,
            'REF' TEXT,
            'ReviewDate' TEXT,
            'CocoaPercent' REAL,
            'CompanyLocationId' INTEGER,
            'Rating' REAL,
            'BeanType' TEXT,
            'BroadBeanOriginId' INTEGER
        );
    '''
    cur.execute(statement)
    conn.commit()
    #open and read csv file
    with open("flavors_of_cacao_cleaned.csv") as f:
        csvReader = csv.reader(f)
        for row in csvReader:
            if row[0] != "Company" and row[2] != "REF" :
                locationCountry = row[5]
                stm_loc = 'SELECT Id FROM Countries WHERE EnglishName = ?'
                cur.execute(stm_loc, (locationCountry,))
                try:
                    locationId = cur.fetchone()[0]
                except:
                    locationId = "NULL"

                beanOriginCountry = row[8]
                stm_ori = 'SELECT Id FROM Countries WHERE EnglishName = ?'
                cur.execute(stm_ori, (beanOriginCountry,))
                try:
                    beanOriginId = cur.fetchone()[0]
                #a format bug: the Côte d'Ivoire in csv file is not read correctly
                except:
                    if row[8] != "Unknown":
                        cur.execute(stm_ori, ("Côte d'Ivoire",))
                        beanOriginId = cur.fetchone()[0]
                    else:
                        beanOriginId = "NULL"

                insertion = (None, row[0], row[1], row[2], row[3], row[4][:-1], locationId, row[6], row[7], beanOriginId)
                statement = 'INSERT INTO "Bars"'
                statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                cur.execute(statement, insertion)
        conn.commit()
    conn.close()

create_populate_Countries()
create_populate_Bars()



# Part 2: Implement logic to process user commands

def process_command(command):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cmd_lst = command.split()
    if cmd_lst[0] == "bars":
        stm = 'SELECT b.SpecificBeanBarName, b.Company, c.EnglishName, b.Rating, b.CocoaPercent, o.EnglishName '
        stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
        if len(cmd_lst) == 1: #command = "bar"
            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id ORDER BY b.Rating DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        else:
            if cmd_lst[1].startswith("sellcountry"):
                sellcountry = cmd_lst[1].split("=")[1]
                flag1 = 1
            elif cmd_lst[1].startswith("sourcecountry"):
                sourcecountry = cmd_lst[1].split("=")[1]
                flag1 = 2
            elif cmd_lst[1].startswith("sellregion"):
                sellregion = cmd_lst[1].split("=")[1]
                flag1 = 3
            elif cmd_lst[1].startswith("sourceregion"):
                sourceregion = cmd_lst[1].split("=")[1]
                flag1 = 4
            else:
                flag1 = 0

            if flag1 != 0:
                if len(cmd_lst) == 2 or len(cmd_lst) == 3 and cmd_lst[2] == "ratings":
                    flag2 = 0
                    flag3 = 0
                    if flag1 == 1:
                        stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Alpha2 = ? ORDER BY b.Rating DESC LIMIT 10'
                        cur.execute(stm, (sellcountry,))
                        lst = cur.fetchall()
                    elif flag1 == 2:
                        stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Alpha2 = ? ORDER BY b.Rating DESC LIMIT 10'
                        cur.execute(stm, (sourcecountry,))
                        lst = cur.fetchall()
                    elif flag1 == 3:
                        stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Region = ? ORDER BY b.Rating DESC LIMIT 10'
                        cur.execute(stm, (sellregion,))
                        lst = cur.fetchall()
                    elif flag1 == 4:
                        stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Region = ? ORDER BY b.Rating DESC LIMIT 10'
                        cur.execute(stm, (sourceregion,))
                        lst = cur.fetchall()

                elif len(cmd_lst) == 3:

                    if cmd_lst[2] == "cocoa":
                        flag2 = 2
                        flag3 = 0
                        if flag1 == 1:
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Alpha2 = ? ORDER BY b.CocoaPercent DESC LIMIT 10'
                            cur.execute(stm, (sellcountry,))
                            lst = cur.fetchall()
                        elif flag1 == 2:
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Alpha2 = ? ORDER BY b.CocoaPercent DESC LIMIT 10'
                            cur.execute(stm, (sourcecountry,))
                            lst = cur.fetchall()
                        elif flag1 == 3:
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Region = ? ORDER BY b.CocoaPercent DESC LIMIT 10'
                            cur.execute(stm, (sellregion,))
                            lst = cur.fetchall()
                        elif flag1 == 4:
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Region = ? ORDER BY b.CocoaPercent DESC LIMIT 10'
                            cur.execute(stm, (sourceregion,))
                            lst = cur.fetchall()
                    elif cmd_lst[2].startswith("top"):
                        limit = int(cmd_lst[2].split("=")[1])
                        flag2 = 0
                        flag3 = 1
                        if flag1 == 1:
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Alpha2 = ? ORDER BY b.Rating DESC LIMIT {}'.format(limit)
                            cur.execute(stm, (sellcountry,))
                            lst = cur.fetchall()
                        elif flag1 == 2:
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Alpha2 = ? ORDER BY b.Rating DESC LIMIT {}'.format(limit)
                            cur.execute(stm, (sourcecountry,))
                            lst = cur.fetchall()
                        elif flag1 == 3:
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Region = ? ORDER BY b.Rating DESC LIMIT {}'.format(limit)
                            cur.execute(stm, (sellregion,))
                            lst = cur.fetchall()
                        elif flag1 == 4:
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Region = ? ORDER BY b.Rating DESC LIMIT {}'.format(limit)
                            cur.execute(stm, (sourceregion,))
                            lst = cur.fetchall()
                    elif cmd_lst[2].startswith("bottom"):
                        limit = int(cmd_lst[2].split("=")[1])
                        flag2 = 0
                        flag3 = 2
                        if flag1 == 1:
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Alpha2 = ? ORDER BY b.Rating ASC LIMIT {}'.format(limit)
                            cur.execute(stm, (sellcountry,))
                            lst = cur.fetchall()
                        elif flag1 == 2:
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Alpha2 = ? ORDER BY b.Rating ASC LIMIT {}'.format(limit)
                            cur.execute(stm, (sourcecountry,))
                            lst = cur.fetchall()
                        elif flag1 == 3:
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Region = ? ORDER BY b.Rating ASC LIMIT {}'.format(limit)
                            cur.execute(stm, (sellregion,))
                            lst = cur.fetchall()
                        elif flag1 == 4:
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Region = ? ORDER BY b.Rating ASC LIMIT {}'.format(limit)
                            cur.execute(stm, (sourceregion,))
                            lst = cur.fetchall()
                elif len(cmd_lst) == 4:
                    if cmd_lst[2] == "ratings":
                        flag2 = 1
                        if cmd_lst[3].startswith("top"):
                            limit = int(cmd_lst[3].split("=")[1])
                            flag3 = 1
                            if flag1 == 1:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Alpha2 = ? ORDER BY b.Rating DESC LIMIT {}'.format(limit)
                                cur.execute(stm, (sellcountry,))
                                lst = cur.fetchall()
                            elif flag1 == 2:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Alpha2 = ? ORDER BY b.Rating DESC LIMIT {}'.format(limit)
                                cur.execute(stm, (sourcecountry,))
                                lst = cur.fetchall()
                            elif flag1 == 3:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Region = ? ORDER BY b.Rating DESC LIMIT {}'.format(limit)
                                cur.execute(stm, (sellregion,))
                                lst = cur.fetchall()
                            elif flag1 == 4:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Region = ? ORDER BY b.Rating DESC LIMIT {}'.format(limit)
                                cur.execute(stm, (sourceregion,))
                                lst = cur.fetchall()
                        elif cmd_lst[3].startswith("bottom"):
                            limit = int(cmd_lst[3].split("=")[1])
                            flag3 = 2
                            if flag1 == 1:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Alpha2 = ? ORDER BY b.Rating ASC LIMIT {}'.format(limit)
                                cur.execute(stm, (sellcountry,))
                                lst = cur.fetchall()
                            elif flag1 == 2:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Alpha2 = ? ORDER BY b.Rating ASC LIMIT {}'.format(limit)
                                cur.execute(stm, (sourcecountry,))
                                lst = cur.fetchall()
                            elif flag1 == 3:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Region = ? ORDER BY b.Rating ASC LIMIT {}'.format(limit)
                                cur.execute(stm, (sellregion,))
                                lst = cur.fetchall()
                            elif flag1 == 4:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Region = ? ORDER BY b.Rating ASC LIMIT {}'.format(limit)
                                cur.execute(stm, (sourceregion,))
                                lst = cur.fetchall()
                    elif cmd_lst[2] == "cocoa":
                        flag2 = 2
                        if cmd_lst[3].startswith("top"):
                            limit = int(cmd_lst[3].split("=")[1])
                            flag3 = 1
                            if flag1 == 1:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Alpha2 = ? ORDER BY b.CocoaPercent DESC LIMIT {}'.format(limit)
                                cur.execute(stm, (sellcountry,))
                                lst = cur.fetchall()
                            elif flag1 == 2:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Alpha2 = ? ORDER BY b.CocoaPercent DESC LIMIT {}'.format(limit)
                                cur.execute(stm, (sourcecountry,))
                                lst = cur.fetchall()
                            elif flag1 == 3:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Region = ? ORDER BY b.CocoaPercent DESC LIMIT {}'.format(limit)
                                cur.execute(stm, (sellregion,))
                                lst = cur.fetchall()
                            elif flag1 == 4:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Region = ? ORDER BY b.CocoaPercent DESC LIMIT {}'.format(limit)
                                cur.execute(stm, (sourceregion,))
                                lst = cur.fetchall()
                        elif cmd_lst[3].startswith("bottom"):
                            limit = int(cmd_lst[3].split("=")[1])
                            flag3 = 2
                            if flag1 == 1:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Alpha2 = ? ORDER BY b.CocoaPercent ASC LIMIT {}'.format(limit)
                                cur.execute(stm, (sellcountry,))
                                lst = cur.fetchall()
                            elif flag1 == 2:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Alpha2 = ? ORDER BY b.CocoaPercent ASC LIMIT {}'.format(limit)
                                cur.execute(stm, (sourcecountry,))
                                lst = cur.fetchall()
                            elif flag1 == 3:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE c.Region = ? ORDER BY b.CocoaPercent ASC LIMIT {}'.format(limit)
                                cur.execute(stm, (sellregion,))
                                lst = cur.fetchall()
                            elif flag1 == 4:
                                stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id WHERE o.Region = ? ORDER BY b.CocoaPercent ASC LIMIT {}'.format(limit)
                                cur.execute(stm, (sourceregion,))
                                lst = cur.fetchall()
            else: #flag1 = 0
                if len(cmd_lst) == 2:
                    if cmd_lst[1] == "ratings":
                        flag2 = 1
                        flag3 = 0
                        stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id ORDER BY b.Rating DESC LIMIT 10'
                        cur.execute(stm)
                        lst = cur.fetchall()
                    elif cmd_lst[1] == "cocoa":
                        flag2 = 2
                        flag3 = 0
                        stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id ORDER BY b.CocoaPercent DESC LIMIT 10'
                        cur.execute(stm)
                        lst = cur.fetchall()
                    elif cmd_lst[1].startswith("top"):
                        limit = int(cmd_lst[1].split("=")[1])
                        flag2 = 0
                        flag3 = 1
                        stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id ORDER BY b.Rating DESC LIMIT {}'.format(limit)
                        cur.execute(stm)
                        lst = cur.fetchall()
                    elif cmd_lst[1].startswith("bottom"):
                        limit = int(cmd_lst[1].split("=")[1])
                        flag2 = 0
                        flag3 = 2
                        stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id ORDER BY b.Rating ASC LIMIT {}'.format(limit)
                        cur.execute(stm)
                        lst = cur.fetchall()
                elif len(cmd_lst) == 3:
                    if cmd_lst[1] == "ratings":
                        flag2 = 1
                        if cmd_lst[2].startswith("top"):
                            limit = int(cmd_lst[2].split("=")[1])
                            flag3 = 1
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id ORDER BY b.Rating DESC LIMIT {}'.format(limit)
                            cur.execute(stm)
                            lst = cur.fetchall()
                        elif cmd_lst[2].startswith("bottom"):
                            limit = int(cmd_lst[2].split("=")[1])
                            flag3 = 2
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id ORDER BY b.Rating ASC LIMIT {}'.format(limit)
                            cur.execute(stm)
                            lst = cur.fetchall()
                    elif cmd_lst[1] == "cocoa":
                        flag2 = 2
                        if cmd_lst[2].startswith("top"):
                            limit = int(cmd_lst[2].split("=")[1])
                            flag3 = 1
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id ORDER BY b.CocoaPercent DESC LIMIT {}'.format(limit)
                            cur.execute(stm)
                            lst = cur.fetchall()
                        elif cmd_lst[2].startswith("bottom"):
                            limit = int(cmd_lst[2].split("=")[1])
                            flag3 = 2
                            stm += 'LEFT JOIN Countries AS o ON b.BroadBeanOriginId = o.Id ORDER BY b.CocoaPercent ASC LIMIT {}'.format(limit)
                            cur.execute(stm)
                            lst = cur.fetchall()


    elif cmd_lst[0] == "companies":
        flag = ""
        if len(cmd_lst) == 1:
            flag = "000"
        elif len(cmd_lst) == 2:
            if cmd_lst[1].startswith("country"):
                flag = "100"
                sellcountry = cmd_lst[1].split("=")[1]
            elif cmd_lst[1].startswith("region"):
                flag = "200"
                sellregion = cmd_lst[1].split("=")[1]
            elif cmd_lst[1] == "ratings":
                flag = "010"
            elif cmd_lst[1] == "cocoa":
                flag = "020"
            elif cmd_lst[1] == "bars_sold":
                flag = "030"
            elif cmd_lst[1].startswith("top"):
                flag = "001"
                limit = int(cmd_lst[1].split("=")[1])
            elif cmd_lst[1].startswith("bottom"):
                flag = "002"
                limit = int(cmd_lst[1].split("=")[1])
        elif len(cmd_lst) == 3:
            if cmd_lst[1].startswith("country"):
                sellcountry = cmd_lst[1].split("=")[1]
                if cmd_lst[2] == "ratings":
                    flag = "110"
                elif cmd_lst[2] == "cocoa":
                    flag = "120"
                elif cmd_lst[2] == "bars_sold":
                    flag = "130"
            elif cmd_lst[1].startswith("region"):
                sellregion = cmd_lst[1].split("=")[1]
                if cmd_lst[2] == "ratings":
                    flag = "210"
                elif cmd_lst[2] == "cocoa":
                    flag = "220"
                elif cmd_lst[2] == "bars_sold":
                    flag = "230"
            elif cmd_lst[1] == "ratings":
                if cmd_lst[2].startswith("top"):
                    flag = "011"
                elif cmd_lst[2].startswith("bottom"):
                    flag = "012"
                limit = int(cmd_lst[2].split("=")[1])
            elif cmd_lst[1] == "cocoa":
                if cmd_lst[2].startswith("top"):
                    flag = "021"
                elif cmd_lst[2].startswith("bottom"):
                    flag = "022"
                limit = int(cmd_lst[2].split("=")[1])
            elif cmd_lst[1] == "bars_sold":
                if cmd_lst[2].startswith("top"):
                    flag = "031"
                elif cmd_lst[2].startswith("bottom"):
                    flag = "032"
                limit = int(cmd_lst[2].split("=")[1])
        elif len(cmd_lst) == 4:
            limit = int(cmd_lst[3].split("=")[1])
            if cmd_lst[1].startswith("country"):
                sellcountry = cmd_lst[1].split("=")[1]
                if cmd_lst[2] == "ratings":
                    if cmd_lst[3].startswith("top"):
                        flag = "111"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "112"
                elif cmd_lst[2] == "cocoa":
                    if cmd_lst[3].startswith("top"):
                        flag = "121"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "122"
                elif cmd_lst[2] == "bars_sold":
                    if cmd_lst[3].startswith("top"):
                        flag = "131"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "132"
            elif cmd_lst[1].startswith("region"):
                sellregion = cmd_lst[1].split("=")[1]
                if cmd_lst[2] == "ratings":
                    if cmd_lst[3].startswith("top"):
                        flag = "211"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "212"
                elif cmd_lst[2] == "cocoa":
                    if cmd_lst[3].startswith("top"):
                        flag = "221"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "222"
                elif cmd_lst[2] == "bars_sold":
                    if cmd_lst[3].startswith("top"):
                        flag = "231"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "232"

        if flag == "000" or flag == "010":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "020":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "030":
            stm = 'SELECT b.Company, c.EnglishName, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY b.Company HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "100" or flag == "110":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Alpha2 = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT 10'
            cur.execute(stm, (sellcountry,))
            lst = cur.fetchall()
        elif flag == "120":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Alpha2 = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT 10'
            cur.execute(stm, (sellcountry,))
            lst = cur.fetchall()
        elif flag == "130":
            stm = 'SELECT b.Company, c.EnglishName, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Alpha2 = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT 10'
            cur.execute(stm, (sellcountry,))
            lst = cur.fetchall()
        elif flag == "200" or flag == "210":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT 10'
            cur.execute(stm, (sellregion,))
            lst = cur.fetchall()
        elif flag == "220":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT 10'
            cur.execute(stm, (sellregion,))
            lst = cur.fetchall()
        elif flag == "230":
            stm = 'SELECT b.Company, c.EnglishName, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT 10'
            cur.execute(stm, (sellregion,))
            lst = cur.fetchall()
        elif flag == "001":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "002":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.Rating) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "011":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "012":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.Rating) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "021":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "022":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "031":
            stm = 'SELECT b.Company, c.EnglishName, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY b.Company HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "032":
            stm = 'SELECT b.Company, c.EnglishName, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY b.Company HAVING count(*) > 4 ORDER BY count(*) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "111":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Alpha2 = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT {}'.format(limit)
            cur.execute(stm, (sellcountry,))
            lst = cur.fetchall()
        elif flag == "112":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Alpha2 = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.Rating) ASC LIMIT {}'.format(limit)
            cur.execute(stm, (sellcountry,))
            lst = cur.fetchall()
        elif flag == "121":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Alpha2 = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT {}'.format(limit)
            cur.execute(stm, (sellcountry,))
            lst = cur.fetchall()
        elif flag == "122":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Alpha2 = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) ASC LIMIT {}'.format(limit)
            cur.execute(stm, (sellcountry,))
            lst = cur.fetchall()
        elif flag == "131":
            stm = 'SELECT b.Company, c.EnglishName, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Alpha2 = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT {}'.format(limit)
            cur.execute(stm, (sellcountry,))
            lst = cur.fetchall()
        elif flag == "132":
            stm = 'SELECT b.Company, c.EnglishName, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Alpha2 = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY count(*) ASC LIMIT {}'.format(limit)
            cur.execute(stm, (sellcountry,))
            lst = cur.fetchall()
        elif flag == "211":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT {}'.format(limit)
            cur.execute(stm, (sellregion,))
            lst = cur.fetchall()
        elif flag == "212":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.Rating) ASC LIMIT {}'.format(limit)
            cur.execute(stm, (sellregion,))
            lst = cur.fetchall()
        elif flag == "221":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT {}'.format(limit)
            cur.execute(stm, (sellregion,))
            lst = cur.fetchall()
        elif flag == "222":
            stm = 'SELECT b.Company, c.EnglishName, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) ASC LIMIT {}'.format(limit)
            cur.execute(stm, (sellregion,))
            lst = cur.fetchall()
        elif flag == "231":
            stm = 'SELECT b.Company, c.EnglishName, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT {}'.format(limit)
            cur.execute(stm, (sellregion,))
            lst = cur.fetchall()
        elif flag == "232":
            stm = 'SELECT b.Company, c.EnglishName, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY b.Company HAVING count(*) > 4 ORDER BY count(*) ASC LIMIT {}'.format(limit)
            cur.execute(stm, (sellregion,))
            lst = cur.fetchall()

    elif cmd_lst[0] == "countries":
        flag = ""
        if len(cmd_lst) == 1:
            flag = "0000"
        elif len(cmd_lst) == 2:
            if cmd_lst[1].startswith("region"):
                flag = "1000"
                region = cmd_lst[1].split("=")[1]
            elif cmd_lst[1] == "sellers":
                flag = "0100"
            elif cmd_lst[1] == "sources":
                flag = "0200"
            elif cmd_lst[1] == "ratings":
                flag = "0010"
            elif cmd_lst[1] == "cocoa":
                flag = "0020"
            elif cmd_lst[1] == "bars_sold":
                flag = "0030"
            else:
                limit = int(cmd_lst[1].split("=")[1])
                if cmd_lst[1].startswith("top"):
                    flag = "0001"
                elif cmd_lst[1].startswith("bottom"):
                    flag = "0002"
        elif len(cmd_lst) == 3:
            if cmd_lst[1].startswith("region"):
                region = cmd_lst[1].split("=")[1]
                if cmd_lst[2] == "sellers":
                    flag = "1100"
                elif cmd_lst[2] == "sources":
                    flag = "1200"
                elif cmd_lst[2] == "ratings":
                    flag = "1010"
                elif cmd_lst[2] == "cocoa":
                    flag = "1020"
                elif cmd_lst[2] == "bars_sold":
                    flag = "1030"
                else:
                    limit = int(cmd_lst[2].split("=")[1])
                    if cmd_lst[2].startswith("top"):
                        flag = "1001"
                    elif cmd_lst[2].startswith("bottom"):
                        flag = "1002"
            elif cmd_lst[1] == "sellers":
                if cmd_lst[2] == "ratings":
                    flag = "0110"
                elif cmd_lst[2] == "cocoa":
                    flag = "0120"
                elif cmd_lst[2] == "bars_sold":
                    flag = "0130"
                else:
                    limit = int(cmd_lst[2].split("=")[1])
                    if cmd_lst[2].startswith("top"):
                        flag = "0101"
                    elif cmd_lst[2].startswith("bottom"):
                        flag = "0102"
            elif cmd_lst[1] == "sources":
                if cmd_lst[2] == "ratings":
                    flag = "0210"
                elif cmd_lst[2] == "cocoa":
                    flag = "0220"
                elif cmd_lst[2] == "bars_sold":
                    flag = "0230"
                else:
                    limit = int(cmd_lst[2].split("=")[1])
                    if cmd_lst[2].startswith("top"):
                        flag = "0201"
                    elif cmd_lst[2].startswith("bottom"):
                        flag = "0202"
            elif cmd_lst[1] == "ratings":
                limit = int(cmd_lst[2].split("=")[1])
                if cmd_lst[2].startswith("top"):
                    flag = "0011"
                elif cmd_lst[2].startswith("bottom"):
                    flag = "0012"
            elif cmd_lst[1] == "cocoa":
                limit = int(cmd_lst[2].split("=")[1])
                if cmd_lst[2].startswith("top"):
                    flag = "0021"
                elif cmd_lst[2].startswith("bottom"):
                    flag = "0022"
            elif cmd_lst[1] == "bars_sold":
                limit = int(cmd_lst[2].split("=")[1])
                if cmd_lst[2].startswith("top"):
                    flag = "0031"
                elif cmd_lst[2].startswith("bottom"):
                    flag = "0032"
        elif len(cmd_lst) == 4:
            if cmd_lst[1].startswith("region"):
                region = cmd_lst[1].split("=")[1]
                if cmd_lst[2]  == "sellers":
                    if cmd_lst[3] == "ratings":
                        flag = "1110"
                    elif cmd_lst[3] == "cocoa":
                        flag = "1120"
                    elif cmd_lst[3] == "bars_sold":
                        flag = "1130"
                    else:
                        limit = int(cmd_lst[3].split("=")[1])
                        if cmd_lst[3].startswith("top"):
                            flag = "1101"
                        elif cmd_lst[3].startswith("bottom"):
                            flag = "1102"
                elif cmd_lst[2] == "sources":
                    if cmd_lst[3] == "ratings":
                        flag = "1210"
                    elif cmd_lst[3] == "cocoa":
                        flag = "1220"
                    elif cmd_lst[3] == "bars_sold":
                        flag = "1230"
                    else:
                        limit = int(cmd_lst[3].split("=")[1])
                        if cmd_lst[3].startswith("top"):
                            flag = "1201"
                        elif cmd_lst[3].startswith("bottom"):
                            flag = "1202"
                elif cmd_lst[2] == "ratings":
                    limit = int(cmd_lst[3].split("=")[1])
                    if cmd_lst[3].startswith("top"):
                        flag = "1011"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "1012"
                elif cmd_lst[2] == "cocoa":
                    limit = int(cmd_lst[3].split("=")[1])
                    if cmd_lst[3].startswith("top"):
                        flag = "1021"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "1022"
                elif cmd_lst[2] == "bars_sold":
                    limit = int(cmd_lst[3].split("=")[1])
                    if cmd_lst[3].startswith("top"):
                        flag = "1031"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "1032"
            elif cmd_lst[1] == "sellers":
                limit = int(cmd_lst[3].split("=")[1])
                if cmd_lst[2] == "ratings":
                    if cmd_lst[3].startswith("top"):
                        flag = "0111"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "0112"
                elif cmd_lst[2] == "cocoa":
                    if cmd_lst[3].startswith("top"):
                        flag = "0121"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "0122"
                elif cmd_lst[2] == "bars_sold":
                    if cmd_lst[3].startswith("top"):
                        flag = "0131"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "0132"
            elif cmd_lst[1] == "sources":
                limit = int(cmd_lst[3].split("=")[1])
                if cmd_lst[2] == "ratings":
                    if cmd_lst[3].startswith("top"):
                        flag = "0211"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "0212"
                elif cmd_lst[2] == "cocoa":
                    if cmd_lst[3].startswith("top"):
                        flag = "0221"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "0222"
                elif cmd_lst[2] == "bars_sold":
                    if cmd_lst[3].startswith("top"):
                        flag = "0231"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "0232"
        elif len(cmd_lst) == 5:
            region = cmd_lst[1].split("=")[1]
            limit = int(cmd_lst[4].split("=")[1])
            if cmd_lst[2] == "sellers":
                if cmd_lst[3] == "ratings":
                    if cmd_lst[4].startswith("top"):
                        flag = "1111"
                    elif cmd_lst[4].startswith("bottom"):
                        flag = "1112"
                elif cmd_lst[3] == "cocoa":
                    if cmd_lst[4].startswith("top"):
                        flag = "1121"
                    elif cmd_lst[4].startswith("bottom"):
                        flag = "1122"
                elif cmd_lst[3] == "bars_sold":
                    if cmd_lst[4].startswith("top"):
                        flag = "1131"
                    elif cmd_lst[4].startswith("bottom"):
                        flag = "1132"
            elif cmd_lst[2] == "sources":
                if cmd_lst[3] == "ratings":
                    if cmd_lst[4].startswith("top"):
                        flag = "1211"
                    elif cmd_lst[4].startswith("bottom"):
                        flag = "1212"
                elif cmd_lst[3] == "cocoa":
                    if cmd_lst[4].startswith("top"):
                        flag = "1221"
                    elif cmd_lst[4].startswith("bottom"):
                        flag = "1222"
                elif cmd_lst[3] == "bars_sold":
                    if cmd_lst[4].startswith("top"):
                        flag = "1231"
                    elif cmd_lst[4].startswith("bottom"):
                        flag = "1232"
        if flag == "0000" or flag == "0100" or flag == "0110" or flag == "0010":
            stm = 'SELECT c.EnglishName, c.Region, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0001" or flag == "0101" or flag == "0111" or flag == "0011":
            stm = 'SELECT c.EnglishName, c.Region, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0002" or flag == "0102" or flag == "0012" or flag == "0112":
            stm = 'SELECT c.EnglishName, c.Region, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.Rating) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "1000" or flag == "1100" or flag == "1110" or flag == "1010":
            stm = 'SELECT c.EnglishName, c.Region, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT 10'
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "0200" or flag == "0210":
            stm = 'SELECT o.EnglishName, o.Region, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0020" or flag == "0120":
            stm = 'SELECT c.EnglishName, c.Region, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0030" or flag == "0130":
            stm = 'SELECT c.EnglishName, c.Region, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "1200" or flag == "1210":
            stm = 'SELECT o.EnglishName, o.Region, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'WHERE o.Region = ? GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT 10'
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1020" or flag == "1120":
            stm = 'SELECT c.EnglishName, c.Region, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT 10'
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1030" or flag == "1130":
            stm = 'SELECT c.EnglishName, c.Region, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT 10'
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1001" or flag == "1101" or flag == "1111" or flag == "1011":
            stm = 'SELECT c.EnglishName, c.Region, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT {}'.format(limit)
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1002" or flag == "1102" or flag == "1112" or flag == "1012":
            stm = 'SELECT c.EnglishName, c.Region, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.Rating) ASC LIMIT {}'.format(limit)
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "0220":
            stm = 'SELECT o.EnglishName, o.Region, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0230":
            stm = 'SELECT o.EnglishName, o.Region, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0201" or flag == "0211":
            stm = 'SELECT o.EnglishName, o.Region, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0202" or flag == "0212":
            stm = 'SELECT o.EnglishName, o.Region, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.Rating) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0021" or flag == "0121":
            stm = 'SELECT c.EnglishName, c.Region, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0022" or flag == "0122":
            stm = 'SELECT c.EnglishName, c.Region, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0031" or flag == "0131":
            stm = 'SELECT c.EnglishName, c.Region, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0032" or flag == "0132":
            stm = 'SELECT c.EnglishName, c.Region, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY count(*) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "1220":
            stm = 'SELECT o.EnglishName, o.Region, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'WHERE o.Region = ? GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT 10'
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1230":
            stm = 'SELECT o.EnglishName, o.Region, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'WHERE o.Region = ? GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT 10'
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1201" or flag == "1211":
            stm = 'SELECT o.EnglishName, o.Region, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'WHERE o.Region = ? GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT {}'.format(limit)
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1202" or flag == "1212":
            stm = 'SELECT o.EnglishName, o.Region, round(AVG(b.Rating),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'WHERE o.Region = ? GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.Rating) ASC LIMIT {}'.format(limit)
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1021" or flag == "1121":
            stm = 'SELECT c.EnglishName, c.Region, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT {}'.format(limit)
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1022" or flag == "1122":
            stm = 'SELECT c.EnglishName, c.Region, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) ASC LIMIT {}'.format(limit)
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1031" or flag == "1131":
            stm = 'SELECT c.EnglishName, c.Region, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT {}'.format(limit)
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1032" or flag == "1132":
            stm = 'SELECT c.EnglishName, c.Region, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS c on b.CompanyLocationId = c.Id '
            stm += 'WHERE c.Region = ? GROUP BY c.EnglishName HAVING count(*) > 4 ORDER BY count(*) ASC LIMIT {}'.format(limit)
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "0221":
            stm = 'SELECT o.EnglishName, o.Region, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0222":
            stm = 'SELECT o.EnglishName, o.Region, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0231":
            stm = 'SELECT o.EnglishName, o.Region, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "0232":
            stm = 'SELECT o.EnglishName, o.Region, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY count(*) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "1221":
            stm = 'SELECT o.EnglishName, o.Region, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'WHERE o.Region = ? GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT {}'.format(limit)
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1222":
            stm = 'SELECT o.EnglishName, o.Region, round(AVG(b.CocoaPercent),1) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'WHERE o.Region = ? GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) ASC LIMIT {}'.format(limit)
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1231":
            stm = 'SELECT o.EnglishName, o.Region, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'WHERE o.Region = ? GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT {}'.format(limit)
            cur.execute(stm, (region,))
            lst = cur.fetchall()
        elif flag == "1232":
            stm = 'SELECT o.EnglishName, o.Region, count(*) '
            stm += 'FROM Bars AS b LEFT JOIN Countries AS o on b.BroadBeanOriginId = o.Id '
            stm += 'WHERE o.Region = ? GROUP BY o.EnglishName HAVING count(*) > 4 ORDER BY count(*) ASC LIMIT {}'.format(limit)
            cur.execute(stm, (region,))
            lst = cur.fetchall()


    elif cmd_lst[0] == "regions":
        flag = ""
        if len(cmd_lst) == 1:
            flag = "000"
        elif len(cmd_lst) == 2:
            if cmd_lst[1] == "sellers":
                flag = "100"
            elif cmd_lst[1] == "sources":
                flag = "200"
            elif cmd_lst[1] == "ratings":
                flag = "010"
            elif cmd_lst[1] == "cocoa":
                flag = "020"
            elif cmd_lst[1] == "bars_sold":
                flag = "030"
            else:
                limit = int(cmd_lst[1].split("=")[1])
                if cmd_lst[1].startswith("top"):
                    flag = "001"
                elif cmd_lst[1].startswith("bottom"):
                    flag = "002"
        elif len(cmd_lst) == 3:
            if cmd_lst[1] == "sellers":
                if cmd_lst[2] == "ratings":
                    flag = "110"
                elif cmd_lst[2] == "cocoa":
                    flag = "120"
                elif cmd_lst[2] == "bars_sold":
                    flag = "130"
                else:
                    limit = int(cmd_lst[2].split("=")[1])
                    if cmd_lst[2].startswith("top"):
                        flag = "101"
                    elif cmd_lst[2].startswith("bottom"):
                        flag = "102"
            elif cmd_lst[1] == "sources":
                if cmd_lst[2] == "ratings":
                    flag = "210"
                elif cmd_lst[2] == "cocoa":
                    flag = "220"
                elif cmd_lst[2] == "bars_sold":
                    flag = "230"
                else:
                    limit = int(cmd_lst[2].split("=")[1])
                    if cmd_lst[2].startswith("top"):
                        flag = "201"
                    elif cmd_lst[2].startswith("bottom"):
                        flag = "202"
            else:
                limit = int(cmd_lst[2].split("=")[1])
                if cmd_lst[1] == "ratings":
                    if cmd_lst[2].startswith("top"):
                        flag = "011"
                    elif cmd_lst[2].startswith("bottom"):
                        flag = "012"
                elif cmd_lst[1] == "cocoa":
                    if cmd_lst[2].startswith("top"):
                        flag = "021"
                    elif cmd_lst[2].startswith("bottom"):
                        flag = "022"
                elif cmd_lst[1] == "bars_sold":
                    if cmd_lst[2].startswith("top"):
                        flag = "031"
                    elif cmd_lst[2].startswith("bottom"):
                        flag = "032"
        elif len(cmd_lst) == 4:
            limit = int(cmd_lst[3].split("=")[1])
            if cmd_lst[1] == "sellers":
                if cmd_lst[2] == "ratings":
                    if cmd_lst[3].startswith("top"):
                        flag = "111"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "112"
                elif cmd_lst[2] == "cocoa":
                    if cmd_lst[3].startswith("top"):
                        flag = "121"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "122"
                elif cmd_lst[2] == "bars_sold":
                    if cmd_lst[3].startswith("top"):
                        flag = "131"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "132"
            elif cmd_lst[1] == "sources":
                if cmd_lst[2] == "ratings":
                    if cmd_lst[3].startswith("top"):
                        flag = "211"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "212"
                elif cmd_lst[2] == "cocoa":
                    if cmd_lst[3].startswith("top"):
                        flag = "221"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "222"
                elif cmd_lst[2] == "bars_sold":
                    if cmd_lst[3].startswith("top"):
                        flag = "231"
                    elif cmd_lst[3].startswith("bottom"):
                        flag = "232"

        if flag == "000" or flag == "100" or flag == "010" or flag =="110":
            stm = 'SELECT c.Region, round(AVG(b.Rating),1) FROM Bars AS b '
            stm += 'JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.Region HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "200" or flag == "210":
            stm = 'SELECT o.Region, round(AVG(b.Rating),1) FROM Bars AS b '
            stm += 'JOIN Countries AS o ON b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.Region HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "120" or flag == "020":
            stm = 'SELECT c.Region, round(AVG(b.CocoaPercent),1) FROM Bars AS b '
            stm += 'JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.Region HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "130" or flag == "030":
            stm = 'SELECT c.Region, count(*) FROM Bars AS b '
            stm += 'JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.Region HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "001" or flag == "011" or flag == "111" or flag == "101":
            stm = 'SELECT c.Region, round(AVG(b.Rating),1) FROM Bars AS b '
            stm += 'JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.Region HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "002" or flag == "012" or flag == "112" or flag == "102":
            stm = 'SELECT c.Region, round(AVG(b.Rating),1) FROM Bars AS b '
            stm += 'JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.Region HAVING count(*) > 4 ORDER BY AVG(b.Rating) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "220":
            stm = 'SELECT o.Region, round(AVG(b.CocoaPercent),1) FROM Bars AS b '
            stm += 'JOIN Countries AS o ON b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.Region HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "230":
            stm = 'SELECT o.Region, count(*) FROM Bars AS b '
            stm += 'JOIN Countries AS o ON b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.Region HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT 10'
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "201" or flag == "211":
            stm = 'SELECT o.Region, round(AVG(b.Rating),1) FROM Bars AS b '
            stm += 'JOIN Countries AS o ON b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.Region HAVING count(*) > 4 ORDER BY AVG(b.Rating) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "202" or flag == "212":
            stm = 'SELECT o.Region, round(AVG(b.Rating),1) FROM Bars AS b '
            stm += 'JOIN Countries AS o ON b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.Region HAVING count(*) > 4 ORDER BY AVG(b.Rating) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "021" or flag == "121":
            stm = 'SELECT c.Region, round(AVG(b.CocoaPercent),1) FROM Bars AS b '
            stm += 'JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.Region HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "022" or flag == "122":
            stm = 'SELECT c.Region, round(AVG(b.CocoaPercent),1) FROM Bars AS b '
            stm += 'JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.Region HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "031" or flag == "131":
            stm = 'SELECT c.Region, count(*) FROM Bars AS b '
            stm += 'JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.Region HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "032" or flag == "132":
            stm = 'SELECT c.Region, count(*) FROM Bars AS b '
            stm += 'JOIN Countries AS c ON b.CompanyLocationId = c.Id '
            stm += 'GROUP BY c.Region HAVING count(*) > 4 ORDER BY count(*) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "221":
            stm = 'SELECT o.Region, round(AVG(b.CocoaPercent),1) FROM Bars AS b '
            stm += 'JOIN Countries AS o ON b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.Region HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "222":
            stm = 'SELECT o.Region, round(AVG(b.CocoaPercent),1) FROM Bars AS b '
            stm += 'JOIN Countries AS o ON b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.Region HAVING count(*) > 4 ORDER BY AVG(b.CocoaPercent) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "231":
            stm = 'SELECT o.Region, count(*) FROM Bars AS b '
            stm += 'JOIN Countries AS o ON b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.Region HAVING count(*) > 4 ORDER BY count(*) DESC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()
        elif flag == "232":
            stm = 'SELECT o.Region, count(*) FROM Bars AS b '
            stm += 'JOIN Countries AS o ON b.BroadBeanOriginId = o.Id '
            stm += 'GROUP BY o.Region HAVING count(*) > 4 ORDER BY count(*) ASC LIMIT {}'.format(limit)
            cur.execute(stm)
            lst = cur.fetchall()

    conn.close()
    return lst



def load_help_text():
    with open('help.txt') as f:
        return f.read()

# Part 3: Implement interactive prompt. We've started for you!
def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('Enter a command: ')
        if response == 'help':
            print(help_text)
            continue
        elif response == 'exit':
            print("bye")
            continue
        else:
            try:
                lst = process_command(response)
                if response.startswith("bars"):
                    for t in lst:
                        slst = []
                        for i in t:
                            try: #if i is a string obj
                                s = (i[:12] + '...') if len(i) > 12 else i
                                slst.append(s)
                            except: #if i is not a string obj
                                slst.append(str(i))
                        if slst[5] == 'None':
                            print('{:15} {:15} {:15} {:4} {:6} {:15}'.format(slst[0],slst[1],slst[2],slst[3],slst[4]+'%',"Unknown"))
                        else:
                            print('{:15} {:15} {:15} {:4} {:6} {:15}'.format(slst[0],slst[1],slst[2],slst[3],slst[4]+'%',slst[5]))

                elif response.startswith("companies"):
                    for t in lst:
                        slst = []
                        for i in t:
                            try: #if i is a string obj
                                s = (i[:12] + '...') if len(i) > 12 else i
                                slst.append(s)
                            except: #if i is not a string obj
                                slst.append(str(i))
                        if "cocoa" in response:
                            print('{:15} {:15} {:8}'.format(slst[0],slst[1],slst[2]+'%'))
                        else:
                            print('{:15} {:15} {:8}'.format(slst[0],slst[1],slst[2]))

                elif response.startswith("countries"):
                    for t in lst:
                        slst = []
                        for i in t:
                            try: #if i is a string obj
                                s = (i[:12] + '...') if len(i) > 12 else i
                                slst.append(s)
                            except: #if i is not a string obj
                                slst.append(str(i))
                        if "cocoa" in response:
                            print('{:15} {:15} {:8}'.format(slst[0],slst[1],slst[2]+'%'))
                        else:
                            print('{:15} {:15} {:8}'.format(slst[0],slst[1],slst[2]))

                elif response.startswith("regions"):
                    for t in lst:
                        slst = []
                        for i in t:
                            try: #if i is a string obj
                                s = (i[:12] + '...') if len(i) > 12 else i
                                slst.append(s)
                            except: #if i is not a string obj
                                slst.append(str(i))
                        if "cocoa" in response:
                            print('{:15} {:8}'.format(slst[0],slst[1]+'%'))
                        else:
                            print('{:15} {:8}'.format(slst[0],slst[1]))
                print(" ")
            except:
                print("Command not recognized: {}, enter 'help' for instructions\n".format(response))


# Make sure nothing runs or prints out when this file is run as a module
if __name__=="__main__":
    interactive_prompt()
