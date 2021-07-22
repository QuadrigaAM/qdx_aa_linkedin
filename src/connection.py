import os
import sys
# sys.path.append(os.path.join(sys.path[0], 'src'))
sys.path.append(os.getcwd() + '//' + 'src')
sys.path.append(os.getcwd())

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from configparser import ConfigParser
from googlesearch import search
from bs4 import BeautifulSoup
import selenium
import logging
import time
import re
import os

## logging configuration
logger = logging.getLogger('logs\\log')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logs\\log.log') # TODO: define multiple logs (one per pipeline)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname) - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logging.getLogger().addHandler(logging.StreamHandler()) # to display message in console

## read configuration files
config = ConfigParser()
config.read('src/config.ini')

## environment variables
BROWSER = config['configuration_parameters']['browser']
DRIVER_FILEPATH = config['configuration_parameters']['driver_filepath']
USERNAME = eval(config['configuration_parameters']['username'])
PASSWORD = eval(config['configuration_parameters']['password'])
LINKEDIN_URL = config['configuration_parameters']['linkedin_url']


class QDXLinkedInSpyder:

    __COUNTRIES__ = {
        'Spain': 'es' # TODO: fill-in the dictionary
    }

    def __init__(self, browser: str = BROWSER, driver_filepath: str = DRIVER_FILEPATH, username: str = USERNAME,
                 password: str = PASSWORD, linkedin_url: str = LINKEDIN_URL, country: str = 'spain'):

        self.browser = browser
        self.driver_filepath = driver_filepath
        self.username = username
        self.password = password
        self.linkedin_url = linkedin_url
        self.username_xpath = '//*[@type="text"]'
        self.password_xpath = '//*[@type="password"]'
        self.login_xpath = '//*[@type="submit"]'
        self.recall_me_xpath = '//*[@type="submit"]'
        self.standard_query_beginning = 'site:linkedin.com/in/'
        self.web_driver = webdriver.Chrome(self.driver_filepath)
        self.contact_info_url_extension = '/detail/contact-info'
        self.contact_info_url_extension_country_replacement = self.__COUNTRIES__.get(country.capitalize()) + '.'

    def get_company_employees(self, company_name: str, retrievals: int = 30, elapse: int = 11, limit: int = 50000): # TODO: ADD Google anti-blocker's policy parameters
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
            time.sleep(3)
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
                     save_data: bool = True, filepath: str = 'default'):
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
                link = link + self.contact_info_url_extension
                profile_name = str(re.findall(r'in/(.+)/detail', link)[0] + '_contact_info')

            data = driver_obj.page_source # TODO: add bs4, scrapy, regex extraction on <driver.page_source>
            profile_raw_data.append(link)
            if save_data:
                with open(directory + '\\' + profile_name + '.txt', 'w') as fd:
                    fd.write(data)

        return error, profile_raw_data






############################# TEST CODE ##############################################################
qlink = QDXLinkedInSpyder()
contact_links = qlink.get_company_employees('a&g banca privada')
error, driver = qlink.execute_auto_logging()
error, profile_data = qlink.get_raw_data(driver, contact_links, filepath='G:\\_NeverBackUp\\AURIGA\\DATA\\LINKEDIN')