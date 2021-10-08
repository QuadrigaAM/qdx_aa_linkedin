import os
import sys
# sys.path.append(os.path.join(sys.path[0], 'src'))
sys.path.append(os.getcwd() + '//' + 'src')
sys.path.append(os.getcwd())
sys.path.append('C:\\Users\\david.serero\\AppData\\Local\\Programs\\Python\\Python38\\lib\\site-packages\\')
#from prepare import get_investor_datapoints
from prepare import get_contact_info, find_useful_info_from_people_search
import time
import xlwings as xw
import pandas as pd
from pprint import pprint
print(sys.argv)

## environment variables
__INVESTORS__ = ['a&g banca privada']
__PRINT_ON_CONSOLE__ = True
excel_path = "linkedin_salesforce_interface.xlsx"

def sheet1():
    wb = xw.Book(excel_path)
    sht1 = wb.sheets[0]
    to_search = [" ".join(search) for search in sht1.range((7, 4), (10, 5)).value if search[0] is not None]
    data = []
    for search in to_search:
        data.append(get_contact_info(search))
    data = pd.concat(data)
    possible_investors = qrest.get_items_by_values(s_object="Account", search_values=data["current_company"], field_name = "Name")
    data[["Possible SF Investor1", "Possible SF Inv2", "Possible SF Inv3"]] = pd.DataFrame(possible_investors, index = data.index)
    sht1.range(6, 8).value = data

def sheet2():
    wb = xw.Book(excel_path)
    sht1 = wb.sheets[1]
    to_search = [search for search in sht1.range((7, 4), (15, 7)).value if search != [None] * len(search)]
    data = []
    for search in to_search:
        print(search)
        print(search[0])
        data.append(find_useful_info_from_people_search(company_name=search[0],search_keywords=search[1], page=int(search[2]), country=search[3]))
    data = pd.concat(data)
    print(data)
    sht1.range(5, 9).value = data

if __name__ == '__main__':
    if sys.argv[1] == "Sheet1":
        sheet1()
    if sys.argv[1] == "Sheet2":
        sheet2()
    ## make pipeline
    if 1 == 0:
        investors_datapoints = get_investor_datapoints(__INVESTORS__)
        if __PRINT_ON_CONSOLE__:
            print('######################################################################################################')
            print('####################### INVESTOR DATAPOINTS ##########################################################')
            print('######################################################################################################')
            for investor in __INVESTORS__:
                for key in list(investors_datapoints[investor].keys())[1:]:
                    print(f'\n\n{key}: {investors_datapoints[investor][key]}')

            print()
            print()
