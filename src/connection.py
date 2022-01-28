import os
import sys
# sys.path.append(os.path.join(sys.path[0], 'src'))
sys.path.append(os.getcwd() + '//' + 'src')
sys.path.append(os.getcwd())
sys.path.insert(0, os.getcwd() + '//' + 'libs')
sys.path.insert(0, os.getcwd() + '//' + 'libs/qdx_aa_linkedin')

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from typing import Optional
from termcolor import colored, cprint
from configparser import ConfigParser
from googletrans import Translator
from googlesearch import search
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
import scipy.stats as ss
import numpy as np
import pandas as pd
import datetime
import requests
import selenium
import logging
import time
from tqdm import tqdm
import re
import os

## logging configuration
try:
    logger = logging.getLogger('logs\\log')
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('logs\\log.log') # TODO: define multiple logs (one per pipeline)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname) - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logging.getLogger().addHandler(logging.StreamHandler()) # to display message in console
except FileNotFoundError:
    pass

## read configuration files
# config = ConfigParser()
# # try:
# #     config.read('libs/qdx_aa_linkedin/src/config.ini')
# # except KeyError:
# config.read('D:\\_NeverBackUp\\AURIGA\\PycharmProjects\\qdx_aa_salesforce\\libs\\qdx_aa_linkedin\\src\\config.ini') # TODO: solve relative path

config = ConfigParser()
try:
    try:
        config.read('libs/qdx_aa_linkedin/src/config.ini')
        if config['configuration_parameters']['browser'] is not None:
            pass
        else:
            config.read('/home/consultant/PycharmProjects/qdx_aa_salesforce/src/config.ini')

    except KeyError:
        config.read('D:/D2/_NeverBackUp/AURIGA/PycharmProjects/qdx_aa_salesforce/libs/qdx_aa_linkedin/src/config.ini')

except KeyError:
    cprint('[Error] missing configuration file or route to it', 'red')
    cprint('[NOTES] please check the config.ini file in the src folder or the OS where the code is running, '
           'as it may be different within a Linux, Windows, MacOS or any other operating system', 'red')

## environment variables
BROWSER = config['configuration_parameters']['browser']
if sys.platform == 'win32':
    DRIVER_FILEPATH = config['configuration_parameters']['driver_filepath']
elif sys.platform == 'linux':
    DRIVER_FILEPATH = config['configuration_parameters']['driver_filepath_linux']
else:
    cprint('[ERROR] Unsupported OS', 'red')
    cprint('[NOTES] The problem with support is not due a software problem, but a pending development for MacOS '
            'systems. This is due the small or null demand for this software running in such operating system so '
            'if needed, its just a matter of developing a new version for MacOS.', 'yellow')

# DRIVER_FILEPATH = config['configuration_parameters']['driver_filepath']
USERNAME = 'world.financial.reporting.data@gmail.com' # FIXME: eval(config['configuration_parameters']['username'])
PASSWORD = 'QuadrigaData2021!' # FIXME: eval(config['configuration_parameters']['password'])
LINKEDIN_URL = config['configuration_parameters']['linkedin_url']
SQL_DATABASE_TYPE = config['quadriga_ai_server']['sql_database_type']
SQL_DATABASE_USERNAME = config['quadriga_ai_server']['sql_database_username']
SQL_DATABASE_NAME = config['quadriga_ai_server']['sql_database_name']
SQL_DATABASE_IP_ADDRESS = config['quadriga_ai_server']['sql_database_ip_address']
SQL_DATABASE_PORT = config['quadriga_ai_server']['sql_database_port']
SQL_DATABASE_PASSWORD = config['quadriga_ai_server']['sql_database_password']


class QuadrigaLinedInNeuralNetwork:

    GENERAL_SENTIMENT_PAIRS = { # TODO: use direct Google translator with
        # 'This is amazing': 'POSITIVE',
        # 'The stock market is amazing': 'POSITIVE',
        # 'The GDP rises': 'POSITIVE',
        # 'The economy is booming': 'POSITIVE',
        # 'The economic outlook is good': 'POSITIVE',
        # 'The US GROWTH is good': 'POSITIVE',
        # 'The inflation rises': 'NEGATIVE',
        # 'The economy is falling': 'NEGATIVE',
        # 'The US GROWTH is falling': 'NEGATIVE',
        # 'The upcoming elections are going to be a disaster': 'NEGATIVE',
        # 'The stock market is falling': 'NEGATIVE',
        # 'Tesla is soaring': 'POSITIVE',
        # 'Tesla shrinks by': 'NEGATIVE',
        'El mercado se está hundiendo': 'NEGATIVE',
        'EL PIB decrece y cae en picado': 'NEGATIVE',
        'Aumenta la deuda pública': 'NEGATIVE',

    }

    GOLD_SENTIMENT_PAIRS = {}


class QuadrigaLinkedInSpyder:

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

        self.desired_width = 320
        self.max_colwidth = 100
        self.max_cols = 20
        self.max_rows = 30
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
        self.standard_main_url = 'site:linkedin.com/company/'
        self.web_driver = webdriver.Chrome(self.driver_filepath)
        self.contact_info_url_extension = '/detail/contact-info'
        self.activity_url_extension = '/detail/recent-activity'
        self.contact_info_url_extension_country_replacement = self.__COUNTRIES__.get(country.capitalize()) + '.'

    def adjust_dataframe_visual_space(self):
        pd.set_option('display.width', self.desired_width)
        np.set_printoptions(linewidth=self.desired_width)
        pd.set_option('display.max_colwidth', self.max_colwidth)
        pd.set_option('display.max_columns', self.max_cols)
        pd.set_option('display.max_rows', self.max_rows)
        cprint('\n[RECALL] To establish default visualization dimensions for a pandas.core.dataframe.DataFrame, '
               'modify __init__ parameters \n', 'cyan')

    def get_company_employees(self, company_name: str, retrievals: int = 10, elapse: int = 11, limit: float = 50000): # TODO: ADD Google anti-blocker's policy parameters
        """
        This method retrieves the employees of a company from LinkedIn. It uses the Google search engine to filter them,
        instead of the LinkedIn search engine. Seems better and more manageable to create new functionalities to search
        and filter other items, topics, etc.

        Also, using Google search engine, seems that the constraints to search, find and retrieve data is higher (under
        Google search policy) than the LinkedIn search engine. This is definitely TRUE for those LinkedIn accounts that
        doesn't have the PREMIUM plan.

        The execution os this class-method runs backend-based, so it doesn't need a UI driver -like Chromedriver- to be
        executed.

        @param company_name: the name of the company to retrieve the employees from. It will retrieve the employees
        from an ad-hoc search on site:linkedin.com/in/, this is only those that exist at LinkedIn. The search is
        performed using the Google search engine.
        @type company_name: str
        @param retrievals: the number of times the program will try to retrieve the employees from the search. Basically,
        it is the number of items (employees) that the program will retrieve from the search. It may be limited due to
        so many conditions, as the Google search engine's policy or as to test the program.
        @type retrievals: int
        @param elapse: the number of seconds the program will wait for the search to be completed. Lapse to wait between
        HTTP requests. A lapse too long will make the search slow, but a lapse too short may cause Google to block your
        IP. Your mileage may vary!
        @type elapse: float
        @param limit: the maximum number of employees to retrieve. Basically, it is the maximum number of automatic
        searches that the program may perform under the Google search policy. It automatically limits the capacity
        of the 'retrievals' parameter.
        @type limit: int
        @return: a list of the employees of the company.
        @rtype: list
        """
        ## query to execute
        query, employee_urls = self.standard_query_beginning + ' AND ' + company_name, []
        start_time = time.time()

        ## assertions :: a lower elapse with respect to the retrievals is limited to 10 (a lower elapse will trigger it)
        assert elapse > 10
        assert retrievals / elapse < 10

        ## searches for the company's employees
        for it, employee_link in enumerate(search(query, tld="co.in", num=retrievals, stop=retrievals, pause=elapse)):
            if it == limit - 1 and time.time() - start_time == 86400 - 1:
                break
            if time.time() - start_time >= 100 - 2 and it == 100 - 1:
                time.sleep(abs(int(np.floor(ss.norm.rvs(3, 1.5, 1)))))
            employee_urls.append(employee_link)

        return employee_urls

    def get_company_link(self, company_name: str, retrievals: int = 10, elapse: int = 11, limit: int = 50000,
                         search_method='wise'): # TODO: ADD Google anti-blocker's policy parameters
        """
        This method provides the link to the company's LinkedIn page. It uses the Google search engine to filter them.

        Also, using Google search engine, seems that the constraints to search, find and retrieve data is higher (under
        Google search policy) than the LinkedIn search engine. This is definitely TRUE for those LinkedIn accounts that
        doesn't have the PREMIUM plan.

        The execution os this class-method runs backend-based, so it doesn't need a UI driver -like Chromedriver- to be
        executed.

        @param company_name: the name of the company to retrieve the related link from. If search_method is 'wise',
        it will retrieve the company's link from an ad-hoc search on site:linkedin.com/in/.
        @type company_name: str
        @param retrievals: the number of times the program will try to retrieve the employees from the search. Basically,
        it is the number of items (employees) that the program will retrieve from the search. It may be limited due to
        so many conditions, as the Google search engine's policy or as to test the program.
        @type retrievals: int
        @param elapse: the number of seconds the program will wait for the search to be completed. Lapse to wait between
        HTTP requests. A lapse too long will make the search slow, but a lapse too short may cause Google to block your
        IP. Your mileage may vary!
        @type elapse: float
        @param limit: the maximum number of employees to retrieve. Basically, it is the maximum number of automatic
        searches that the program may perform under the Google search policy. It automatically limits the capacity
        of the 'retrievals' parameter.
        @type limit: int
        @param search_method: "wise" for the company link, "all" for all possible combinations. Set to "wise" by
        default. An 'all' method may be useful to search for / within all possible combinations for any other purposes.
        @type search_method: str
        @return: a string with the linkedIn url or a list of one or more links to the company's LinkedIn page,
        multiple LinkedIn pages or multiple possible combinations.
        @rtype: str <return type for 'wise' method>, list <return type for 'all' method>
        """

        query, company_urls = self.standard_main_url + ' AND ' + company_name, []
        start_time = time.time()
        assert elapse > 10
        assert retrievals / elapse < 10
        for it, company_link in enumerate(search(query, tld="co.in", num=retrievals, stop=retrievals, pause=elapse)):
            if it == limit - 1 and time.time() - start_time == 86400 - 1:
                break
            if time.time() - start_time >= 100 - 2 and it == 100 - 1:
                time.sleep(abs(int(np.floor(ss.norm.rvs(3, 1.5, 1)))))
            company_urls.append(company_link)
        if search_method == 'all':
            return company_urls
        if search_method == 'wise':
            return [x for x in company_urls if re.findall(r'https://\w+\.linkedin\.com/company/.*', x)][0]

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
            # username = driver.find_element_by_xpath(self.username_xpath) # TODO: remove these commented lines ...
            username = driver.find_element(selenium.webdriver.common.by.By.XPATH, self.username_xpath)
            username.send_keys(self.username)
            time.sleep(abs(int(np.floor(ss.norm.rvs(3, 1.5, 1)))))
            # password = driver.find_element_by_xpath(self.password_xpath)
            password = driver.find_element(selenium.webdriver.common.by.By.XPATH, self.password_xpath)
            password.send_keys(self.password)
            time.sleep(abs(int(np.floor(ss.norm.rvs(3, 1.5, 1)))))
            # login_button = driver.find_element_by_xpath(self.login_xpath)
            login_button = driver.find_element(selenium.webdriver.common.by.By.XPATH, self.login_xpath)
            login_button.click()
            if activate_recall_me:
                recall_me_button = driver.find_element_by_xpath(self.recall_me_xpath)
                recall_me_button.click()
            time.sleep(abs(int(np.floor(ss.norm.rvs(3, 1.5, 1)))))
            if delete_all_cookies:
                driver.delete_all_cookies()

        except Exception as exception_msg:
            error = 1
            logger.error('Exit code {} - Error in automatic logging syntax: {}'.format(error, exception_msg))

        return error, driver

    def quit(self):
        """
        This method quits the browser. Permits closing sessions in a secure way.
        @return: None, just executes the quit method of the browser.
        @rtype: None
        """
        self.web_driver.quit()

    def translate_text(self): # TODO: translate text to spanish for later train of neural network on sentiment analysis and classification towards assets
        pass # TODO: translate any kind of text to english or to spanish or any other combination origin-destiny

    def evaluate_market_sentiment(self, train_first: bool = False, model_to_train: str = None, model_to_infer: str = None): # TODO: infer model in each individual
        pass # TODO: train first if True, then/else infer positive, neutral or negative sentiment

    def evaluate_asset_sentiment(self, train_first: bool = False, model_to_train: str = None, model_to_infer: str = None): #TODO: TODO: infer model in each individual
        pass # TODO: execute previous function (mkt sentiment or asset sentiment) and FILTER by keyword (eg.: if string-contains gold or XAUUSD or XAU/USD)

    def get_profiles_by_job_position(self):
        pass # TODO: (1) load positions from Linkedin (usage of this function by Salesforce repo to check current job title changes)

    def anonymize_profiles(self):
        pass # TODO: pass this function to columns with names so to anonymize them (np.random <random algorithm GDPR> ... not to get back)

    def get_raw_data(self, driver_obj: selenium.webdriver, people_urls: list, content_retrieval: str = 'profile',
                     save_data: bool = True, filepath: str = 'default', add_to_database: bool = True,
                     db_action: str = 'append'): # TODO: review contact-info endpoint raw data
        """
        This method retrieves the raw data from the LinkedIn profile pages.

        @param db_action:
        @param add_to_database:
        @param driver_obj:
        @type driver_obj: selenium.webdriver
        @param filepath:
        @type filepath: str
        @param save_data:
        @type save_data: bool
        @param people_urls:
        @type people_urls: list
        @param content_retrieval:
        possible options:
            - 'profile': retrieves raw data from the main LinkedIn page of a profile
            - 'contact': retrieves raw data from the contact's profile information
            - 'activity': retrieves raw data from recent contact's activity
        :return:
        """
        ## local variables
        error, profile_name = 0, 0
        engine = create_engine(f'{SQL_DATABASE_TYPE}://{SQL_DATABASE_USERNAME}:{SQL_DATABASE_PASSWORD}@'
                               f'{SQL_DATABASE_IP_ADDRESS}:{SQL_DATABASE_PORT}/{SQL_DATABASE_NAME}')

        directory = os.getcwd() + '\\data'
        if filepath != 'default':
            directory = filepath

        profile_raw_data, observations, activity_records_users, activity_records_posts = [], [], [], []
        for link in tqdm(people_urls): # TODO: beware empty list for memory increase :: to be limited
            time.sleep(abs(int(np.floor(ss.norm.rvs(3, 1.5, 1)))))
            if content_retrieval == 'profile':
                driver_obj.get(link)
                profile_name = str(re.findall(r'in/(.+)', link)[0])
            if content_retrieval == 'contact':
                link = link + self.contact_info_url_extension # TODO: add class object instead of 'es'
                link = link.replace('es.', '') # TODO: necessary to change .es any country code?
                driver_obj.get(link)
                profile_name = str(re.findall(r'in/(.+)/detail', link)[0] + '_contact_info')
                # TODO: once the list has N elements (as a paremeter), 1st save on disk, 2nd list = []
            if content_retrieval == 'activity':
                link = link + self.activity_url_extension
                link = link.replace('es.', '')
                driver_obj.get(link)
                profile_name = str(re.findall(r'in/(.+)/detail/recent-activity', link)[0] + '_recent_activity')

                # while driver_obj.find_element_by_tag_name('div'):
                for it in tqdm(range(10)):
                    driver_obj.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(abs(int(np.floor(ss.norm.rvs(3, 1.5, 1)))))
                    # Divs = driver_obj.find_element_by_tag_name('div').text
                    # if 'End of Results' in Divs:
                    #     print('end')
                    if it == 101:
                        print('end')
                        break
                    # else:
                    #     continue

            ## match the name of the profile
            if profile_name.__contains__('/') or profile_name.__contains__('\\'):
                profile_name = profile_name.replace('/', '_')

            data = driver_obj.page_source # TODO: add bs4, scrapy, regex extraction on <driver.page_source>
            profile_raw_data.append(link)

            ## posts on linkedin
            try:
                username = self.web_driver.find_element(selenium.webdriver.common.by.By.XPATH, '//*[@id="recent-activity-top-card"]/div[3]/h3').text
                posts = re.findall(r'<span dir="ltr">(.+)</span>', data)
                writted_posts = [posts[ix + 1] for ix in [it for it, comment in enumerate(posts) if comment == username]]
                try:
                    writted_participation_ratio = len(writted_posts) / len(posts)
                except ZeroDivisionError:
                    writted_participation_ratio = 0

                date_time_with_respect_to_now = re.findall(r'<span><span aria-hidden="true">(.+) •', data)
                participation_size = len(date_time_with_respect_to_now)
                writted_participation_size = len(posts)
                last_participation_date = list(np.sort(re.findall(r'"accessibilityText":"(\d\s\w+) ago', data)))[-1]

                ## translate posts to english to make data available for to be inferred by pre-trained neural networks
                try:
                    translator = Translator()
                    t_posts = [translator.translate(str(post), 'en', translator.detect(post).lang).text for post in posts]
                    t_writted_posts = [t_posts[ix + 1] for ix in [it for it, comment in enumerate(posts) if comment == username]]
                except Exception as exception_message:
                    t_posts = posts
                    t_writted_posts = writted_posts

                ## general sentiment analysis # TODO: add sentiment analysis for spanish (only valid in english in this general sentiment analysis)
                from textblob import TextBlob
                nlp_data = TextBlob(str(t_writted_posts))
                polarity = nlp_data.polarity
                subjectivity = nlp_data.subjectivity

                ## specific sentiment analysis
                # TODO: train and infer a neural network to predict the sentiment of a comment for spanish and english
                # TODO: train and infer a neural network to predict the sentiment on specific topics (gold, stock market, inflation, ...) in spanish and english

                ## convert datapoints to dataframe
                observations.append([
                    profile_name, link, username, last_participation_date, writted_participation_ratio, participation_size,
                    writted_participation_size, polarity, subjectivity
                ])

                liked_users = [posts[ix - 1] for ix in [it for it, comment in enumerate(posts) if comment != username] if
                               len(posts[ix - 1].split()) < 3]

                liked_comments = [posts[ix] for ix in [it for it, comment in enumerate(posts) if comment != username] if
                                  len(posts[ix - 1].split()) < 3]

                if len(liked_users) == len(liked_comments): # better than an assertion: low missed data isn't big problem
                    activity_records_users.append(liked_users)
                    activity_records_posts.append(liked_comments)

                ## save the raw data
                if save_data:
                    try:
                        with open(directory + '\\' + profile_name + '.txt', 'w') as fd:
                            fd.write(data)

                    except UnicodeEncodeError:
                        with open(directory + '\\' + profile_name + '.txt', 'w', encoding='utf-8') as fd:
                            fd.write(data)

                self.adjust_dataframe_visual_space()
                profiles_observations_df = pd.DataFrame(observations, columns=[
                    'profile_name', 'link', 'username', 'last_participation_date', 'participation_ratio',
                    'writted_participation_size', 'writted_participation_size', 'polarity', 'subjectivity'
                ])
                profiles_observations_df['username'] = username
                profiles_posts_df = pd.DataFrame({
                    'liked_name': list(pd.Series(activity_records_users).explode().values),
                    'liked_post': list(pd.Series(activity_records_posts).explode().values)
                })
                profiles_posts_df['username'] = username

                # TODO: add connection and push dataframe to SQL database
                if add_to_database:
                    profiles_observations_df['backupDate'] = pd.to_datetime(datetime.datetime.now().strftime('%Y-%m-%d'), format='%Y-%m-%d')
                    profiles_observations_df.to_sql(name='profiles_stats', con=engine, index=False, if_exists=db_action)
                    profiles_posts_df['backupDate'] = pd.to_datetime(datetime.datetime.now().strftime('%Y-%m-%d'), format='%Y-%m-%d')
                    profiles_posts_df.to_sql(name='profiles_posts', con=engine, index=False, if_exists=db_action)

            except Exception as exception_message:
                print(exception_message)
                continue

        return error, profile_raw_data, profiles_observations_df, profiles_posts_df

    def extract_profile_datapoints_from_url(self, url, element='company'):
        ## 1. download contacts from linkedin
        self.web_driver.get(url=url)
        xpath = selenium.webdriver.common.by.By.XPATH
        if element == 'company':
            return self.web_driver.find_element(xpath, '//*[@id="ember203"]/div[2]/p[2]').text
        if element == 'position':
            return self.web_driver.find_element(xpath, '//*[@id="ember182"]/div[2]/h3').text

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
        url = self.get_company_link(company_name, search_method='wise')
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


# if __name__ == '__main__':
#     qlink = QuadrigaLinkedInSpyder()
#     qlink.execute_auto_logging()
#     employees_urls = qlink.get_company_employees('a&g banca')
#     e, pfraw = qlink.get_raw_data(qlink.web_driver, people_urls=employees_urls,
#                                   filepath='D:/_NeverBackUp/AURIGA/DATA/employees')

if __name__ == '__main__':
    qlink = QuadrigaLinkedInSpyder()
    qlink.execute_auto_logging()
    employees_urls = qlink.get_company_employees('UBS INVESTMENT BANK', retrievals=100)
    error, profile_raw_data, profiles_observations_df, profiles_posts_df = qlink.get_raw_data(
        qlink.web_driver, people_urls=employees_urls,
        filepath='D:/_NeverBackUp/AURIGA/DATA/employees', save_data=True,
        content_retrieval='activity'
    )

'''
 'ALBILAD CAPITAL',
 'ALKIMIA CAPITAL',
 'ALMA CAPITAL',
 'ALMANACK',
 'ALPHA CAP',
 'ALPINUM']
'''




