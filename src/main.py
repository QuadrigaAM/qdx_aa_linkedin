import os
import sys
# sys.path.append(os.path.join(sys.path[0], 'src'))
sys.path.append(os.getcwd() + '//' + 'src')
sys.path.append(os.getcwd())

from prepare import get_investor_datapoints
from pprint import pprint

## environment variables
__INVESTORS__ = ['a&g banca privada']
__PRINT_ON_CONSOLE__ = True

if __name__ == '__main__':

    ## make pipeline
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
