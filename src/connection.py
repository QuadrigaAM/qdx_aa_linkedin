import os
import sys
print("LinkedIn Connection.py")
# sys.path.append(os.path.join(sys.path[0], 'src'))
sys.path.append(os.getcwd() + '//' + 'src')
sys.path.append(os.getcwd())
sys.path.insert(0, os.getcwd() + '//' + 'libs')
sys.path.insert(0, os.getcwd() + '//' + 'libs/qdx_aa_linkedin')

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from typing import Optional
from configparser import ConfigParser
from googlesearch import search
from bs4 import BeautifulSoup
import requests
from collections import Counter
import selenium
import logging
import time
import re
import os

## logging configuration
try:
    dir_path = "C:\\Users\\david.serero\\PycharmProjects\\qdx_aa_salesforce\\libs\\qdx_aa_linkedin\\src"
except Exception as e:
    print(e)
    dir_path = os.getcwd()
#print((dir_path), os.path.dirname(dir_path))
logger = logging.getLogger(os.path.dirname(dir_path) + '\\logs\\log')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(os.path.dirname(dir_path) + '\\logs\\log.log') # TODO: define multiple logs (one per pipeline)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname) - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logging.getLogger().addHandler(logging.StreamHandler()) # to display message in console

## read configuration files
config = ConfigParser()
config.read(dir_path + '\\config.ini')

## environment variables
BROWSER = config['configuration_parameters']['browser']
DRIVER_FILEPATH = config['configuration_parameters']['driver_filepath']
#USERNAME = eval(config['configuration_parameters']['username'])
#PASSWORD = eval(config['configuration_parameters']['password'])
USERNAME = "parrilla_diego@yahoo.com"
PASSWORD = "DavidSerero1"
LINKEDIN_URL = config['configuration_parameters']['linkedin_url']


class QDXLinkedInSpyder:

    __COUNTRIES__ = {
        'Spain': 'es' # TODO: fill-in the dictionary
    }
    __ZONE__ = {
        'Region': {
            'EMEA': {
                'SubRegion': {
                    'Europe': {
                        'Country': {
                            'Spain': {
                                'City': ['Madrid', 'Barcelona'],
                            },
                            'France': {
                                'City': ['Paris']
                            }
                        }
                    }
                }
            }
        }
    }

    def __init__(self, browser: str = BROWSER, driver_filepath: str = DRIVER_FILEPATH, username: str = USERNAME,
                 password: str = PASSWORD, linkedin_url: str = LINKEDIN_URL, country: str = 'spain'):

        self.browser = browser
        self.driver_filepath = driver_filepath
        self.username = username
        print(self.username)
        self.password = password
        self.linkedin_url = linkedin_url
        self.username_xpath = '//*[@type="text"]'
        self.password_xpath = '//*[@type="password"]'
        self.login_xpath = '//*[@type="submit"]'
        self.recall_me_xpath = '//*[@type="submit"]'
        self.standard_query_beginning = 'site:linkedin.com/in/'
        self.standard_main_url = 'site:linkedin.com/company/'
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument("--log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.web_driver = webdriver.Chrome(self.driver_filepath, options = options)
        self.contact_info_url_extension = '/detail/contact-info'
        self.contact_info_url_extension_country_replacement = self.__COUNTRIES__.get(country.capitalize()) + '.'

    def get_company_employees(self, company_name: str, retrievals: int = 10, elapse: int = 11, limit: int = 50000): # TODO: ADD Google anti-blocker's policy parameters
        """
        This method

        :param limit:
        :param company_name:
        :param retrievals:
        :param elapse:
        :return:
        """
        query, employee_urls = self.standard_query_beginning + ' AND ' + company_name, []
        start_time = time.time()
        assert elapse > 10
        assert retrievals / elapse < 10
        for it, employee_link in enumerate(search(query, tld="co.in", num=retrievals, stop=retrievals, pause=elapse)):
            if it == limit - 1 and time.time() - start_time == 86400 - 1:
                break
            if time.time() - start_time >= 100 - 2 and it == 100 - 1:
                time.sleep(5)
            employee_urls.append(employee_link)

        return employee_urls

    def get_company_linkedin_link(self, company_name: str): # TODO: ADD Google anti-blocker's policy parameters
        url_to_search = f"https://www.linkedin.com/search/results/companies/?keywords={company_name.replace('&', '%26').replace(' ', '%20')}&origin=SWITCH_SEARCH_VERTICAL&sid=S9U"
        self.web_driver.get(url_to_search)
        try :
            return self.web_driver.find_element_by_xpath('//*[@id="main"]/div/div/div[2]/ul/li[1]/div/div/div[2]/div[1]/div[1]/div/span/span/a').get_attribute("href")
        except:
            return self.web_driver.find_element_by_xpath('//*[@id="main"]/div/div/div[3]/ul/li/div/div/div[2]/div[1]/div[1]/div/span/span/a').get_attribute("href")

    def get_company_link(self, company_name: str): #TODO broken but maybe useless too
        linkedin_url = self.get_company_linkedin_link(company_name = company_name)
        self.web_driver.get(linkedin_url)

        try:
            url = self.web_driver.find_element_by_xpath(f'//*[@id="ember57"]').get_attribute("href")
            print("url:", url)
            return url
        except:
            pass
        """
        extractor = URLExtract()
        urls = extractor.find_urls(self.web_driver.page_source)
        urls = ([s for s in urls if f"{company_name}." in s])
        frequent_urls = [urlparse(url).netloc for url in urls]
        print(frequent_urls)
        return Counter(frequent_urls).most_common(1)[0][0]
        """

    def execute_auto_logging(self, wait: bool = True, implicit_wait_time: int = 10, delete_all_cookies: bool = False,
                             activate_recall_me: bool = False): # TODO: adequate policy to avoid anti-spyders
        """
        This method executes an automatic logging to the browser, directly to the LinkedIn given account throughout the
        usage of the automatic browser service.

        :param activate_recall_me:
        :param delete_all_cookies:
        :param wait:
        :param implicit_wait_time:
        :return:
        """
        ## local variables
        error, driver = 0, 0
        try:
            driver = self.web_driver
            if wait:
                driver.implicitly_wait(implicit_wait_time)
            driver.get(self.linkedin_url)
            username = driver.find_element_by_xpath(self.username_xpath)
            username.send_keys(self.username)
            time.sleep(3) # TODO: change these int values (sleeping) to random numbers in a given range
            password = driver.find_element_by_xpath(self.password_xpath)
            password.send_keys(self.password)
            time.sleep(3)
            login_button = driver.find_element_by_xpath(self.login_xpath)
            login_button.click()
            if activate_recall_me:
                recall_me_button = driver.find_element_by_xpath(self.recall_me_xpath)
                recall_me_button.click()
            time.sleep(3)
            if delete_all_cookies:
                driver.delete_all_cookies()

        except Exception as exception_msg:
            error = 1
            logger.error('Exit code {} - Error in automatic logging syntax: {}'.format(error, exception_msg))

        return error, driver

    def quit(self):
        return self.web_driver.quit()

    def get_raw_data(self, driver_obj: selenium.webdriver, people_urls: list, content_retrieval: str = 'profile',
                     save_data: bool = True, filepath: str = 'default'): # TODO: review contact-info endpoint raw data
        """
        :param driver_obj:
        :param filepath:
        :param save_data:
        :param people_urls:
        :param content_retrieval:
        possible options:
            - 'profile': retrieves raw data from the main linkedin page of a profile
            - 'contact': retrieves raw data from the contact's profile information
            - 'activity': retrieves raw data from recent contact's activity
        :return:
        """
        ## local variables
        error, profile_name = 0, 0

        directory = os.getcwd() + '\\data'
        if filepath != 'default':
            directory = filepath

        profile_raw_data = []
        for link in people_urls: # TODO: beware empty list for memory increase :: to be limited
            time.sleep(3)
            if content_retrieval == 'profile':
                driver_obj.get(link)
                profile_name = str(re.findall(r'in/(.+)', link)[0])
            if content_retrieval == 'contact':
                link = link + self.contact_info_url_extension # TODO: add class object instead of 'es'
                link = link.replace('es.', '')
                driver_obj.get(link)
                profile_name = str(re.findall(r'in/(.+)/detail', link)[0] + '_contact_info')
                # TODO: once the list has N elements (as a paremeter), 1st save on disk, 2nd list = []

            data = driver_obj.page_source # TODO: add bs4, scrapy, regex extraction on <driver.page_source>
            profile_raw_data.append(link)
            if save_data:
                try:
                    with open(directory + '\\' + profile_name + '.txt', 'w') as fd:
                        fd.write(data)

                except UnicodeEncodeError:
                    with open(directory + '\\' + profile_name + '.txt', 'w', encoding='utf-8') as fd:
                        fd.write(data)

        return error, profile_raw_data

    def extract_datapoints(self, company_name: str, save_data: bool = True, filepath: str = 'default'):
        """
        This method extracts datapoints from a given linkedin url, specifically the ones in the "/company-name/about"
        endpoint.

        :param company_name:
        :param driver_obj:
        :param save_data:
        :param filepath:
        :return: selection of datapoints
        :rtype: dict
        """
        ## get investor (company) url (endpoint) and get HTML code
        url = self.get_company_linkedin_link(company_name, search_method='wise')
        assert type(url) == str
        endpoint = url + '/about/'
        self.web_driver.get(url=endpoint)

        ## selection of datapoints to be extracted
        ember_value = 72
        while True:
            try:
                return {
                    'investor_raw_data':
                        self.web_driver.page_source,
                    'overview':
                        self.web_driver.find_element_by_xpath(f'//*[@id="ember{ember_value}"]/section/p').text,
                    'website':
                        self.web_driver.find_element_by_xpath(f'//*[@id="ember{ember_value + 1}"]/span').text,
                    'industry':
                        self.web_driver.find_element_by_xpath(f'//*[@id="ember{ember_value}"]/section/dl/dd[2]').text,
                    'company_size':
                        self.web_driver.find_element_by_xpath(f'//*[@id="ember{ember_value}"]/section/dl/dd[3]').text,
                    'company_linkedin_employees':
                        self.web_driver.find_element_by_xpath(f'//*[@id="ember{ember_value}"]/section/dl/dd[4]').text,
                    'headquarters':
                        self.web_driver.find_element_by_xpath(f'//*[@id="ember{ember_value}"]/section/dl/dd[5]').text,
                    'company_capital_type':
                        self.web_driver.find_element_by_xpath(f'//*[@id="ember{ember_value}"]/section/dl/dd[6]').text,
                    'founded_year':
                        self.web_driver.find_element_by_xpath(f'//*[@id="ember{ember_value}"]/section/dl/dd[7]').text,
                    'specialities':
                        self.web_driver.find_element_by_xpath(f'//*[@id="ember{ember_value}"]/section/dl/dd[8]').text

                }

            except:
                ember_value -= 1
                continue

    def get_linkedin_profiles_search_url(self, company_name: str = None, search_keywords: str = "", country: str = None, page: int = 1):
        if company_name is not None:
            print("company is not none")
            company_linkedin_number = self.get_company_linkedin_number(company_name)
            compa_arg = f"""currentCompany=%5B%22{company_linkedin_number}%22%5D&"""
        else:
            compa_arg = ""

        if country is not None:
            if country == "Spain":
                country_arg = """geoUrn=%5B"105646813"%5D&"""
            if country == "France":
                country_arg = """geoUrn=%5B"105015875"%5D&"""
        else:
            country_arg = ""
        search_url = f"""https://www.linkedin.com/search/results/people/?{compa_arg}{country_arg}keywords={search_keywords.replace(' ', '%20')}&origin=FACETED_SEARCH&page={page}&sid=t%2CN"""
        return search_url

    def get_company_linkedin_number(self, company_name: str):
        company_linkedin_url = self.get_company_linkedin_link(company_name=company_name)
        self.web_driver.get(company_linkedin_url)
        company_linkedin_number = Counter(re.findall('currentCompany=%5B%22(.*?)%', self.web_driver.page_source)).most_common()[0][0]
        return company_linkedin_number