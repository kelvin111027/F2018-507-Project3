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

                insertion = (None, row[0], row[1], row[2], row[3], row[4], locationId, row[6], row[7], beanOriginId)
                statement = 'INSERT INTO "Bars"'
                statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                cur.execute(statement, insertion)
        conn.commit()
    conn.close()

create_populate_Countries()
create_populate_Bars()


'''
with open(COUNTRIESJSON, encoding = 'utf-8') as countries_file:
    countries_lst = json.load(countries_file)

print(type(countries_lst))
print(len(countries_lst))
print(countries_lst[0])
print("\n\n\n\n\n")
print(countries_lst[1])
print(type(countries_lst[0]))
#print("\n{}".format(countries_dct))
countries_file.close()'''


# Part 2: Implement logic to process user commands
def process_command(command):
    return []


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

# Make sure nothing runs or prints out when this file is run as a module
if __name__=="__main__":
    interactive_prompt()
