import os
import sys
# sys.path.append(os.path.join(sys.path[0], 'src'))
sys.path.append(os.getcwd() + '//' + 'src')
sys.path.append(os.getcwd())

# from connection import QDXLinkedInSpyder
from libs.qdx_aa_linkedin.src.connection import QuadrigaLinkedInSpyder

qlink = QuadrigaLinkedInSpyder()
error, driver = qlink.execute_auto_logging()


def get_investor_datapoints(investors: list):
    """

    :param investors:
    :return:
    """
    investor_datapoints = {}
    for investor in investors:
        investor_datapoints[investor] = qlink.extract_datapoints(company_name=investor)

    return investor_datapoints


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
    company_links = qlink.get_company_link('a&g banca privada')
    company_linkedin_link = [x for x in company_links if re.findall(r'https://\w+\.linkedin.com/company/.+', x)][0]


    ########## OFFICIAL CODE ###############
    qlink = QDXLinkedInSpyder()
    INVESTORS = ['a&g banca privada']
    error, driver = qlink.execute_auto_logging()

    investor_datapoints = {}
    for investor in INVESTORS:
        investor_datapoints = qlink.extract_datapoints(company_name)