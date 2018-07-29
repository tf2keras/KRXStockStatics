# -*- coding: utf-8 -*-
import FinanceDataReader as Fdr
from datetime import datetime as dt
from datetime import timedelta as td

'''Global variables'''
# None
'''Global variables end'''


def main():
    """ Main program """
    '''Input options'''
    lookup_days = 10
    daily_num = 15
    k = 0.5
    list_type = 'KRX'  # select from KRX(Both KOSPI and KOSDAQ), KOSPI, KOSDAQ
    profit_percent = 5
    '''Input options end'''

    '''Debugging options'''
    lookup_item_limit = 5
    lookup_item_idx = 0
    '''Debugging options end'''

    '''Local variables'''
    company_symbol_name_dict = {}
    '''Local variables end'''

    df_krx = Fdr.StockListing(list_type)
    for x in df_krx.values:
        company_symbol_name_dict[x[0]] = x[1]

    print("({}) Company Symbols: {}".format(list_type, company_symbol_name_dict.items()))

    for key, value in company_symbol_name_dict.items():
        try:
            df = Fdr.DataReader(key, (dt.now() - td(days=lookup_days)).strftime('%Y-%m-%d'))
            for [timestamp, company_symbol_name, company_data] in [[x[0], [key, value], list(x[1])] for x in zip(df.index.tolist(), df.values)]:
                print([timestamp, company_symbol_name, company_data])
        except ValueError:  # pass when there is no data for given company symbol
            pass

        if lookup_item_idx > lookup_item_limit:
            break
        lookup_item_idx = lookup_item_idx + 1

    return 0


if __name__ == "__main__":
    main()
