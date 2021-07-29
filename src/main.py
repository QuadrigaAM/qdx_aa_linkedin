import os
import sys
# sys.path.append(os.path.join(sys.path[0], 'src'))
sys.path.append(os.getcwd() + '//' + 'src')
sys.path.append(os.getcwd())

from connection import QDXLinkedInSpyder

#################################### START TEST CODE ##############################################################
qlink = QDXLinkedInSpyder()
contact_links = qlink.get_company_employees('a&g banca privada')
error, driver = qlink.execute_auto_logging()
# error, profile_data = qlink.get_raw_data(driver, contact_links, filepath='G:\\_NeverBackUp\\AURIGA\\DATA\\LINKEDIN')
error, profile_data_contact_info = qlink.get_raw_data(driver,
                                                      contact_links,
                                                      filepath='G:\\_NeverBackUp\\AURIGA\\DATA\\LINKEDIN',
                                                      content_retrieval='contact')
#################################### END TEST CODE ##############################################################
