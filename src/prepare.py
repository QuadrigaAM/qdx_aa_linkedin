import os
import sys
import json
import pandas as pd
from nameparser import HumanName
from validate_email import validate_email
import unicodedata
import itertools
from tqdm import tqdm
import requests
# sys.path.append(os.path.join(sys.path[0], 'src'))
sys.path.append(os.getcwd() + '//' + 'src')
sys.path.append(os.getcwd())

from connection import QDXLinkedInSpyder

qlink = QDXLinkedInSpyder()
error, driver = qlink.execute_auto_logging()


def check_email(email_address):
    api_key = "978866a4-48ec-4233-84a2-5d332c32af15"
    response = requests.get(
        "https://isitarealemail.com/api/email/validate",
        params = {'email': email_address},
        headers = {'Authorization': "Bearer " + api_key })

    status = response.json()['status']
    if status == "valid":
        return True
    elif status == "invalid":
        return False
    else:
        return True


def get_investor_datapoints(investors: list):
    """
    :param investors:
    :return:
    """
    investor_datapoints = {}
    for investor in investors:
        investor_datapoints[investor] = qlink.extract_datapoints(company_name=investor)
    return investor_datapoints

def first_and_last_names_combinations(name_str):
    possible_emails = []
    words = [x for x in name_str.split(" ") if x[0]!=x[0].lower()]
    my_permutations = list(itertools.permutations(words, 2))
    """
    print(my_permutations)
    for i in range(len(my_permutations)):
            possible_email = f'{my_permutations[i][0]}.{my_permutations[i][1]}'
            possible_emails.append(possible_email)
    """
    for possible_email in my_permutations:
        if "-" in possible_email[0]:
            my_permutations.append(tuple([possible_email[0].replace("-",""), possible_email[1]]))
        if "-" in possible_email[1]:
            my_permutations.append(tuple([possible_email[0], possible_email[1].replace("-","")]))
    return my_permutations

def email_format(company_linkedin_link, first_name, last_name):
    """
    returns
    """
    if company_linkedin_link == "https://www.linkedin.com/company/caixabank/":
        email_domains = ["caixabank.es"]
        format_name = [f"{first_name}.{last_name}"]
    if company_linkedin_link == "https://www.linkedin.com/company/a&g-banca-privada/":
        email_domains = ["crc.ayg.es", "ayg.es"]
        format_name = [f"{first_name}.{last_name}"]
    if company_linkedin_link == "https://www.linkedin.com/company/citi/":
        email_domains = ["citi.com", "citigroup.com"]
        format_name = [f"{first_name}.{last_name}"]
    if company_linkedin_link == "https://www.linkedin.com/company/bbva/":
        email_domains = ["bbva.com"]
        format_name = [f"{first_name}.{last_name}"]
    if company_linkedin_link == "https://www.linkedin.com/company/bankinter/":
        email_domains = ["bankinter.es"]
        format_name = [f"{first_name[:2]}{last_name}"]
    if company_linkedin_link == "https://www.linkedin.com/company/alantra/":
        email_domains = ["alantra.com"]
        format_name = [f"{first_name}.{last_name}"]
    if company_linkedin_link == "https://www.linkedin.com/company/banco-santander/":
        email_domains = ["santander.com", "santanderrio.com.ar", "pb-santander.com"]
        format_name = [f"{first_name[0]}.{last_name}", f"{first_name[:2]}.{last_name}"]
    if company_linkedin_link == "https://www.linkedin.com/company/banco-santander/":
        email_domains = ["santander.com", "santanderrio.com.ar", "pb-santander.com"]
        format_name = [f"{first_name[0]}.{last_name}", f"{first_name[:2]}.{last_name}"]
    possible_emails = ["@".join(possible_email) for possible_email in list(itertools.product(format_name, email_domains))]
    emails = []
    for email in (possible_emails):
        if check_email(remove_accents_lower(email)):
            emails.append(email)
    return emails

def find_email_master(company_linkedin_link, name_str):
    emails = []
    print(name_str)
    if name_str == "Name Error":
        print(emails)
        return emails
    else:
        for first_name, last_name in tqdm(first_and_last_names_combinations(name_str)):
            emails = emails + email_format(company_linkedin_link, first_name, last_name)
        return emails

def first_name(name):
    name = HumanName(name)
    return name.first

def last_name(name):
    name = HumanName(name)
    return name.last

def remove_accents_lower(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii.lower().decode("utf-8")

def find_useful_info_from_people_search(company_name: str, role: str, page: int, premium_plan = True, search_email = True): #TODO : set_location_to_madrid
    data = []
    searched_role = role
    driver.get(qlink.get_linkedin_profiles_search_url(company_name = company_name, role = role, page = page))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    if premium_plan:
        add = 2
    else:
        add = 0
    for i in range(10, 20):
        place = (json.loads((soup.find_all("code")[14+add].contents[0])[3:])["included"][i])["secondarySubtitle"]["text"]
        try:
            name = (json.loads((soup.find_all("code")[14+add].contents[0])[3:])["included"][i])["image"][
                "accessibilityText"]
        except:
            name = "Name Error"
        role = (json.loads((soup.find_all("code")[14+add].contents[0])[3:])["included"][i])["primarySubtitle"]["text"]
        link = (json.loads((soup.find_all("code")[14+add].contents[0])[3:])["included"][i])["navigationUrl"]
        print(i, name, role, place, link)
        data.append([name, role, place, link])
    linkedin_data = pd.DataFrame(data, columns = ["Name", "Role", "Place", "LinkedIn Profile"])
    linkedin_data["First Name"] = linkedin_data["Name"].apply(lambda x: first_name(x))
    linkedin_data["Last Name"] = linkedin_data["Name"].apply(lambda x: last_name(x))
    linkedin_data["Company Name"] = company_name
    print(f"{len(linkedin_data)} people found, searching for their emails")
    if search_email:
        tqdm.pandas()
        linkedin_data["Email"] = linkedin_data["Name"].progress_apply(lambda x: find_email_master(company_linkedin_link, x))
    linkedin_data.to_csv(f"{company_name}_{searched_role}_{page}.csv")
    return linkedin_data

if 1 == 0:
    #################################### START TEST CODE ##############################################################
    qlink = QDXLinkedInSpyder()

    concepts = ['banquero privado', 'asesor patrimonial'] # TODO: fill a dict or list w/ all possible keywords
    institutions = ['a&g banca privada', 'ubs ...']

    contact_links = qlink.get_company_employees('a&g banca privada')
    error, driver = qlink.execute_auto_logging()
    error, profile_data = qlink.get_raw_data(driver, contact_links, filepath='G:\\_NeverBackUp\\AURIGA\\DATA\\LINKEDIN')
    error, profile_data_contact_info = qlink.get_raw_data(driver,
                                                          contact_links,
                                                          filepath='G:\\_NeverBackUp\\AURIGA\\DATA\\LINKEDIN',
                                                          content_retrieval='contact')
    #################################### END TEST CODE ##############################################################


    #################################### START EXTRACT INVESTOR DATAPOINTS FROM LINKEDIN ############################
    from bs4 import BeautifulSoup
    import requests
    import re

    # TODO: create code to find and extract each investor endpoint
    url = 'https://www.linkedin.com/company/a&g-banca-privada/about/'
    html_code = requests.get(url).text
    soup = BeautifulSoup(html_code, "lxml")
    print(soup.prettify())

    qlink = QDXLinkedInSpyder()
    error, driver = qlink.execute_auto_logging()
    driver.get(url=url)
    investor_raw_data = driver.page_source
    overview = driver.find_element_by_xpath('//*[@id="ember72"]/section/p').text
    website = driver.find_element_by_xpath('//*[@id="ember73"]/span').text
    industry = driver.find_element_by_xpath('//*[@id="ember72"]/section/dl/dd[2]').text
    company_size = driver.find_element_by_xpath('//*[@id="ember72"]/section/dl/dd[3]').text
    company_linkedin_employees = driver.find_element_by_xpath('//*[@id="ember72"]/section/dl/dd[4]').text
    headquarters = driver.find_element_by_xpath('//*[@id="ember72"]/section/dl/dd[5]').text
    company_capital_type = driver.find_element_by_xpath('//*[@id="ember72"]/section/dl/dd[6]').text
    founded_year = driver.find_element_by_xpath('//*[@id="ember72"]/section/dl/dd[7]').text
    specialities = driver.find_element_by_xpath('//*[@id="ember72"]/section/dl/dd[8]').text
    #################################### END EXTRACT INVESTOR DATAPOINTS FROM LINKEDIN ############################

    #################################### START EXTRACT INVESTOR LINKEDIN URL ######################################
    import re
    qlink = QDXLinkedInSpyder()
    error, driver = qlink.execute_auto_logging()
    company_links = qlink.get_company_linkedin_link('a&g banca privada')
    company_linkedin_link = [x for x in company_links if re.findall(r'https://\w+\.linkedin.com/company/.+', x)][0]


    ########## OFFICIAL CODE ###############
    qlink = QDXLinkedInSpyder()
    INVESTORS = ['a&g banca privada']
    error, driver = qlink.execute_auto_logging()

    investor_datapoints = {}
    for investor in INVESTORS:
        investor_datapoints = qlink.extract_datapoints(company_name)

"""
for i in range(8,11):
    print(f"page : {i}")
    find_useful_info_from_people_search(company_name = "BBVA", role = "asesor", page = i, premium_plan = False)
"""