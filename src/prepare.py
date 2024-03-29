import os
import sys
import json
import time

import pandas as pd
from nameparser import HumanName
from validate_email import validate_email
import unicodedata
import itertools
from tqdm import tqdm
import difflib
from collections import Counter
from flashgeotext.geotext import GeoText
from bs4 import BeautifulSoup
import re

import requests

# sys.path.append(os.path.join(sys.path[0], 'src'))
sys.path.append(os.getcwd() + '//' + 'src')
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# from connection import QDXLinkedInSpyder
from libs.qdx_aa_linkedin.src.connection import QDXLinkedInSpyder

qlink = QDXLinkedInSpyder()
error, driver = qlink.execute_auto_logging()

def send_message(profile_url, message, premium_account=False):
    driver.get(profile_url)
    # is there a message button?
    # if yes, take action? If yes, send message? if yes, which message?
    # is there a invite button?
    # if yes, take action? If yes, send invitation?
    degree_path = "/html/body/div[7]/div[3]/div/div/div/div/div[3]/div/div/main/div/section/div[2]/div[2]/div[1]/div[1]/span/span[2]"
    degree = driver.find_element_by_xpath(degree_path).text[0]
    if degree == "1":
        message_or_connect_button_xpath = "/html/body/div[7]/div[3]/div/div/div/div/div[3]/div/div/main/div/section/div[2]/div[3]/div/a"
        message_or_connect_button = driver.find_element_by_xpath(message_or_connect_button_xpath)
        button_text = message_or_connect_button.text
    if degree == "2":
        message_or_connect_button_xpath = '/html/body/div[7]/div[3]/div/div/div/div/div[3]/div/div/main/div/section/div[2]/div[3]/div/button[1]'
        message_or_connect_button = driver.find_element_by_xpath(message_or_connect_button_xpath)
        button_text = message_or_connect_button.text
    if degree == "3":
        print("3rd degree person, no message sent")
        return "3rd degree person, no message sent"
    """
    if premium_account:
    if message_or_connect_button.text == "View in Sales Navigator":
        message_or_connect_button_xpath = "/html/body/div[7]/div[3]/div/div/div/div/div[3]/div/div/main/div/section/div[2]/div[3]/div/a"
        message_or_connect_button = driver.find_element_by_xpath(message_or_connect_button_xpath)
    message_is_main_button = message_or_connect_button.text == "Message"
    print(message_is_main_button, message_or_connect_button.text)
    if message_is_main_button:
        if message != "":
            message_or_connect_button.click()
            text_area_xpath = '/html/body/div[7]/aside/div[2]/div[1]/form/div[3]/div/div[1]/div[1]/p'
            text_area = driver.find_element_by_xpath(text_area_xpath)
            text_area.click()
            text_area.send_keys(message)
            time.sleep(0.5)
            send_button_xpath = '/html/body/div[7]/aside/div[2]/div[1]/form/footer/div[2]/div[1]/button'
            send_button = driver.find_element_by_xpath((send_button_xpath))
            send_button.click()
        if send_invite:
            more_button_xpath = '/html/body/div[7]/div[3]/div/div/div/div/div[3]/div/div/main/div/section/div[2]/div[3]/div/div/button'
            more_button = driver.find_element_by_xpath(more_button_xpath)
            more_button.click()
            send_invite_xpath = '/html/body/div[7]/div[3]/div/div/div/div/div[3]/div/div/main/div/section/div[2]/div[3]/div/div/div/div/ul/li[4]/div'
            send_invite = driver.find_element_by_xpath(send_invite_xpath)
            send_invite.click()
    if message_is_main_button == False:
        if send_invite:
            message_or_connect_button.click()
        if message != "":
            add_a_note_path = "/html/body/div[3]/div/div/div[3]/button[1]"
            add_a_note_button = driver.find_element_by_xpath(add_a_note_path)
            add_a_note_button.click()
            text_area_path = "/html/body/div[3]/div/div/div[2]/div/textarea"
            text_area = driver.find_element_by_xpath(text_area_path)
            text_area.click()
            text_area.send_keys(message)
            time.sleep(0.5)
            send_button_xpath = '/html/body/div[3]/div/div/div[3]/button[2]'
            send_button = driver.find_element_by_xpath((send_button_xpath))
            send_button.click()
            """
    if button_text == "Connect":
        message_or_connect_button.click()
        nota_xpath = "/html/body/div[3]/div/div/div[3]/button[1]"
        nota = driver.find_element_by_xpath(nota_xpath)
        nota.click()
        text_area_xpath = "/html/body/div[3]/div/div/div[2]/div[1]/textarea"
        text_area = driver.find_element_by_xpath(text_area_xpath)
        text_area.click()
        text_area.send_keys(message)
        send_button_xpath = '/html/body/div[3]/div/div/div[3]/button[2]'
        send_button = driver.find_element_by_xpath(send_button_xpath)
        send_button.click()
        return "Message sent!"
    if message_or_connect_button.text == "Message" and message is not None:
        message_or_connect_button.click()
        text_area_xpath = '/html/body/div[7]/aside/div[2]/div[1]/form/div[3]/div/div[1]/div[1]/p'
        text_area = driver.find_element_by_xpath(text_area_xpath)
        text_area.click()
        text_area.send_keys(message)
        time.sleep(0.5)
        send_button_xpath = '/html/body/div[7]/aside/div[2]/div[1]/form/footer/div[2]/div[1]/button'
        send_button = driver.find_element_by_xpath((send_button_xpath))
        send_button.click()
        return "Message sent!"

def check_email(email_address):
    api_key = "978866a4-48ec-4233-84a2-5d332c32af15"
    response = requests.get(
        "https://isitarealemail.com/api/email/validate",
        params={'email': email_address},
        headers={'Authorization': "Bearer " + api_key})

    status = response.json()['status']
    if status == "valid":
        return True
    elif status == "invalid":
        return False
    else:
        return False


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
    words = [x for x in name_str.split(" ") if x[0] != x[0].lower()]
    my_permutations = list(itertools.permutations(words, 2))
    """
    print(my_permutations)
    for i in range(len(my_permutations)):
            possible_email = f'{my_permutations[i][0]}.{my_permutations[i][1]}'
            possible_emails.append(possible_email)
    """
    for possible_email in my_permutations:
        if "-" in possible_email[0]:
            my_permutations.append(tuple([possible_email[0].replace("-", ""), possible_email[1]]))
        if "-" in possible_email[1]:
            my_permutations.append(tuple([possible_email[0], possible_email[1].replace("-", "")]))
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
    possible_emails = ["@".join(possible_email) for possible_email in
                       list(itertools.product(format_name, email_domains))]
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


def find_useful_info_from_people_search(company_name: str, search_keywords: str, page: int, country: str,
                                        premium_plan=False, search_email=False, detailed = True):  # TODO : set_location_to_madrid
    data = []
    searched_role = search_keywords
    driver.get(qlink.get_linkedin_profiles_search_url(company_name=company_name, search_keywords=search_keywords,
                                                      country=country, page=page))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    if premium_plan:
        add = 2
    else:
        add = 0
    for i in range(10, 20):
        place = (json.loads((soup.find_all("code")[14 + add].contents[0])[3:])["included"][i])["secondarySubtitle"][
            "text"]
        try:
            name = (json.loads((soup.find_all("code")[14 + add].contents[0])[3:])["included"][i])["image"][
                "accessibilityText"]
        except:
            name = "Name Error"
        role = (json.loads((soup.find_all("code")[14 + add].contents[0])[3:])["included"][i])["primarySubtitle"]["text"]
        link = (json.loads((soup.find_all("code")[14 + add].contents[0])[3:])["included"][i])["navigationUrl"]
        #print(i, name, role, place, link)
        data.append([name, role, place, link])
    linkedin_data = pd.DataFrame(data, columns=["Name", "Role", "Place", "LinkedIn Profile"])
    linkedin_data["First Name"] = linkedin_data["Name"].apply(lambda x: first_name(x))
    linkedin_data["Last Name"] = linkedin_data["Name"].apply(lambda x: last_name(x))
    linkedin_data["Company Name"] = company_name
    print(f"{len(linkedin_data)} people found")
    if search_email:
        tqdm.pandas()
        linkedin_data["Email"] = linkedin_data["Name"].progress_apply(
            lambda x: find_email_master(company_linkedin_link, x))
    if detailed == False:
        linkedin_data.to_csv(f"{company_name}_{searched_role}_{page}.csv")
        return linkedin_data
    if detailed == True:
        data = []
        for url in tqdm(linkedin_data["LinkedIn Profile"]):
            if "headless" not in url:
                data.append(get_profile_infos(url))
        return pd.concat(data)

def remove_all_extra_spaces(string):
    return " ".join(string.split())

def find_text_multiple_xpaths(xpaths, illegal_string):
    """
    the aim here is to return the text of field we are searching for. Continue looking into the list of xpaths until it is valid. Then use it and get .text attribute
    """
    for xpath in xpaths:
        try:
            text = driver.find_element_by_xpath(xpath).text
            if illegal_string.lower() not in text.lower():
                return text
        except:
            pass
    return ""

def get_profile_infos(url):
    driver.get(url)
    time.sleep(0.5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    """
    mini_url = re.search('in/(.*)\?', url).group(1)
    file = open(f"sample{mini_url}.html", "w", encoding='utf-8')
    file.write(driver.page_source)
    file.close()
    """
    first = Counter(re.findall(r',"firstName":"(.*?)"', soup.text)).most_common(2)[1][0]
    last = Counter(re.findall(r',"lastName":"(.*?)"', soup.text)).most_common(2)[1][0]
    print(first)
    l = []
    for i, a in enumerate(soup.find_all("a")):
        for s in a.text.split("\n"):
            l.append(remove_all_extra_spaces(s))
        if "company" in a.get('href'):
            l.append(a.get('href'))
    l = [s for s in l if s != '']
    #print(l)

    try:
        current_company = l[l.index("Company Name") + 1]
        print("print normal")
    except:
        current_company_xpaths = [
            '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[3]/div[3]/ul/li[1]/div/div[2]/div/div[1]/span[1]/span[1]',
            '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[4]/div[3]/ul/li[1]/div/div[2]/div/div[1]/span[1]/span[1]',
            "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[5]/div[3]/ul/li[1]/div/div[2]/div[1]/div[1]/span[1]/span[1]",
            
            '/html/body/div[7]/div[3]/div/div/div[2]/div/div/main/section[3]/div[3]/ul/li[1]/div/div[2]/div/div[1]/span[1]/span[1]',
            '/html/body/div[7]/div[3]/div/div/div[2]/div/div/main/section[4]/div[3]/ul/li[1]/div/div[2]/div/div[1]/span[1]/span[1]',

            "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[3]/div[3]/ul/li[1]/div/div[2]/div[1]/a/div/span/span[1]",
            "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[4]/div[3]/ul/li[1]/div/div[2]/div[1]/a/div/span/span[1]",
            "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[5]/div[3]/ul/li[1]/div/div[2]/div[1]/a/div/span/span[1]"
                                  ]
        current_company = find_text_multiple_xpaths(current_company_xpaths, first)

    roles_xpaths = [
        "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[3]/div[3]/ul/li[1]/div/div[2]/div/div[1]/div/span/span[1]",
        '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[4]/div[2]/ul/li/div/div[2]/div/div[1]/div/span/span[1]',
        "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[4]/div[3]/ul/li[1]/div/div[2]/div/div[1]/div/span/span[1]",
        "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[5]/div[3]/ul/li[1]/div/div[2]/div[1]/div[1]/div/span/span[1]",

        "/html/body/div[7]/div[3]/div/div/div[2]/div/div/main/section[5]/div[3]/ul/li[1]/div/div[2]/div/div[1]/span[1]/span[1]",
        '/html/body/div[7]/div[3]/div/div/div[2]/div/div/main/section[4]/div[2]/ul/li/div/div[2]/div/div[1]/div/span/span[1]',
        '/html/body/div[7]/div[3]/div/div/div[2]/div/div/main/section[4]/div[3]/ul/li[1]/div/div[2]/div/div[1]/div/span/span[1]',
        '/html/body/div[7]/div[3]/div/div/div[2]/div/div/main/section[4]/div[3]/ul/li[1]/div/div[2]/div/div[1]/div/span/span[1]',

        "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[4]/div[3]/ul/li[1]/div/div[2]/div[2]/ul/li[1]/div/div[2]/div/a/div/span/span[1]",
        "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[3]/div[3]/ul/li[1]/div/div[2]/div[2]/ul/li[1]/div/div[2]/div/a/div/span/span[1]",
        "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[5]/div[3]/ul/li[1]/div/div[2]/div[2]/ul/li[1]/div/div[2]/div[1]/a/div/span/span[1]"
    ]
    role = find_text_multiple_xpaths(roles_xpaths, first)
    print(role)

    try:
        location = l[l.index("Location") + 1]
    except:
        location = ""
    location = location + " " + " ".join(re.findall(r'"defaultLocalizedName":"(.*?)"', soup.text))
    geotext = GeoText()
    try:
        city = list(geotext.extract(location)["cities"].keys())[0]
    except:
        city = None
        print(f"Could not find exact city with {location} as location info")
    try:
        country = list(geotext.extract(location)["countries"].keys())[0]
    except:
        country = None
        print(f"Could not find exact country with {location} as location info")
    try:
        current_company_linkedin_url = [s for s in l if "/company/" in s][0]
        if "linkedin.com" not in current_company_linkedin_url:
            current_company_linkedin_url = "https://www.linkedin.com" + current_company_linkedin_url
    except:
        current_company_linkedin_url = ""
    try:
        last_company = l[[i for i, x in enumerate(l) if x == "Company Name"][1] + 1]
    except:
        last_company = "None"
    try:
        end_of_studies = l[[i for i, x in enumerate(l) if x == "Dates attended or expected graduation"][0] + 1]
        end_of_studies = re.findall(r'\d+', end_of_studies)[-1]
    except:
        end_of_studies = ""
    print(f"First Name: {first.title()}, Last Name:{last.title()}, Url: {url}, Role: {role.title()}, Current Company: {current_company}, "
          f"City: {city}, Country: {country}, Company Url: {current_company_linkedin_url}, Previous Company: {last_company}, Year of last Study: {end_of_studies}")
    df = pd.DataFrame(
        [first.title(), last.title(), url, role.title(), current_company.upper(), city, country, current_company_linkedin_url, last_company, end_of_studies],
        index=["First Name", "Last Name", "LinkedIn URL", "Role", "Current Company", "City", "Country",
               "Company LinkedIn URL", "Last Company", "Year of last Study"]).T

    return df


def get_contact_info(search_keywords, premium_plan=False):
    """
    Aim : find information about someone using linkedin \n
    Step 1 : linkedin search with the keywords (usually full name and his firm) \n
    Step 2 : grab the linkedin url of the correct person (most probable the first result of the search) \n
    Step 3 : go inside the linkedin profile url \n
    Step 4 : fetch information (First name, last name, current firm name as displayed on linkedin,
    current firm linkedin url, start date of current role, start date of first job (can help estimate the age),
    previous firm name, role (see NB) \n
    Step 5 : organise this data, put it in a pandas df/series and return it \n
    NB: role fetching is difficult, easier to fetch it by scapping the search page, so we have have access to it around step 2 \n
    :param search_keywords:
    :return:
    """
    # Step 1
    print(search_keywords)
    time.sleep(2)
    driver.get(qlink.get_linkedin_profiles_search_url(search_keywords=search_keywords, global_or_faced_search = "global"))
    soup = BeautifulSoup(driver.page_source, "html.parser")

    #Check if search is empty
    no_search_result = False

    for h1 in soup.find_all("h1"):
        no_search_result = (remove_all_extra_spaces(h1.text.replace("\n", "")) == "No results found")
    if no_search_result:
        return pd.DataFrame(
            ["No Results, this person probably doesn't have a LinkedIn profile", "", "", "", "", "", "", "", "",
             ""],
            index=["First Name", "Last Name", "LinkedIn URL", "Role", "Current Company", "City", "Country",
                   "Company LinkedIn URL", "Last Company", "Year of last Study"]).T
    else:
        if premium_plan:
            add = 2
        else:
            add = 0
        attempts = 0
        data = []
        while attempts < 11:
            try:
                role = \
                (json.loads((soup.find_all("code")[14 + add].contents[0])[3:])["included"][attempts])["primarySubtitle"][
                    "text"]
                linkedin_profile_url = \
                (json.loads((soup.find_all("code")[14 + add].contents[0])[3:])["included"][attempts])["navigationUrl"]
                try:
                    name = (json.loads((soup.find_all("code")[14 + add].contents[0])[3:])["included"][attempts])["image"][
                        "accessibilityText"]
                except:
                    name = "Name Error"
                data.append([role, linkedin_profile_url, name])
            except:
                pass
            attempts += 1
        data = pd.DataFrame(data, columns=["role", "url", "name"])
        data["Full info"] = data["role"] + data["name"]
        #Step 2 : find the best match thanks to difflib.get_close_matches
        best_match = data[data["Full info"] == difflib.get_close_matches(search_keywords, data["Full info"], cutoff=0.)[0]]
        #Step 3, 4 and 5
        return get_profile_infos(best_match["url"].values[0])

if 1 == 0:
    #################################### START TEST CODE ##############################################################
    qlink = QDXLinkedInSpyder()

    concepts = ['banquero privado', 'asesor patrimonial']  # TODO: fill a dict or list w/ all possible keywords
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
