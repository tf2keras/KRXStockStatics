# -*- coding: utf-8 -*-
import FinanceDataReader as Fdr
from datetime import datetime as dt
from datetime import timedelta as td
import csv

'''Global variables'''
above_target_price_dict = {}    # key: date, value: item
above_profit_target_price_dict = {}  # key: date, value: item
companies_above_target_price_dict = {}    # key: date, value: company list
companies_above_profit_target_price_dict = {}  # key: date, value: company list
complement_companies_set_dict = {}      # companies_above_profit_target - companies_above_target
'''Global variables end'''


def main():
    global above_target_price_dict
    global above_profit_target_price_dict
    global companies_above_target_price_dict
    global companies_above_profit_target_price_dict
    global complement_companies_set_dict

    """ Main program """
    '''Input options'''
    lookup_days = 10
    daily_num = 3
    k = 0.5
    list_type = 'KRX'  # select from KRX(Both KOSPI and KOSDAQ), KOSPI, KOSDAQ
    profit_percent = 1.5
    lookup_item_limit = 5  # For debugging
    '''Input options end'''

    '''Local variables'''
    company_symbol_name_dict = {}
    '''Local variables end'''

    df_krx = Fdr.StockListing(list_type)
    for x in df_krx.values:
        company_symbol_name_dict[x[0]] = x[1]

    print("({}) Company Symbols: {}".format(list_type, company_symbol_name_dict.items()))

    lookup_item_idx = 0
    for key, value in company_symbol_name_dict.items():
        print("{}/{} Calculating...".format(lookup_item_idx+1, len(company_symbol_name_dict)))
        try:
            df = Fdr.DataReader(key, (dt.now() - td(days=lookup_days)).strftime('%Y-%m-%d'))

            prev_day_item = None
            # ['2018-07-19', '001040', 'CJ', 139000.0, 144500.0, 146500.0, 138500.0, 656d20.0, -0.0381]
            # date(0), symbol(1), name(2), close(3), open(4), high(5), low(6), volume(7), change(8)
            for item in [[x[0].to_pydatetime().strftime('%Y-%m-%d'), key, value] + list(x[1])
                         for x in zip(df.index.tolist(), df.values)]:
                if dt.strptime(item[0], '%Y-%m-%d').weekday() in [5, 6]:
                    continue    # 5=saturday, 6=sunday
                if prev_day_item is None:
                    prev_day_item = item
                    continue

                prev_uprate = prev_day_item[8]  # use change as uprate value.
                # 1. 최대값(고가) 이 목표가(target price) 를 넘어선 횟수
                # 27일 target price = 27일 시가 46450 + k(26일고가47000 - 26일 저가46000 )
                # k는 유저에게 받아서 예를 들어 k를 1 로 하면
                # target price = 47450 이 됩니다
                if item[4] + k*(prev_day_item[5] - prev_day_item[6]) < item[5]:
                    # 이것을 '27일' 고가 47000 이 넘었는지 못넘었는지 체크합니다.
                    # [1, '001040', 'CJ', 8000.0], [0, '082740', 'HSD엔진', 275.0]
                    # key: date, item: [0/1(0), symbol(1), name(2), prev_high - prev_low(3)]. Use (3) to sort the list.
                    if item[0] in above_target_price_dict:
                        above_target_price_dict[item[0]] = above_target_price_dict[item[0]] \
                                                           + [[1, item[1], item[2], prev_uprate]]
                    else:
                        above_target_price_dict[item[0]] = [[1, item[1], item[2], prev_uprate]]
                else:
                    if item[0] in above_target_price_dict:
                        above_target_price_dict[item[0]] = above_target_price_dict[item[0]] \
                                                           + [[0, item[1], item[2], prev_uprate]]
                    else:
                        above_target_price_dict[item[0]] = [[0, item[1], item[2], prev_uprate]]

                # 2. 최대값(고가)이 목표가(target price) * 수익률을 넘어선 횟수
                # 잘못 말씀드린 것 같은게 있어서 target price * 수익률 < Max price
                # 인지를 체크해야 합니다. 예를 들어 제가 목표로하는 수익률이 1%라고 하면
                # target price * 1.01 < Max price 이런식입니다.
                # Save above result to another dictionary.
                if ((100.0+profit_percent)/100.0)*(item[4] + k*(prev_day_item[5] - prev_day_item[6])) < item[5]:
                    if item[0] in above_profit_target_price_dict:
                        above_profit_target_price_dict[item[0]] = above_profit_target_price_dict[item[0]] \
                                                           + [[1, item[1], item[2], prev_uprate]]
                    else:
                        above_profit_target_price_dict[item[0]] = [[1, item[1], item[2], prev_uprate]]
                else:
                    if item[0] in above_profit_target_price_dict:
                        above_profit_target_price_dict[item[0]] = above_profit_target_price_dict[item[0]] \
                                                           + [[0, item[1], item[2], prev_uprate]]
                    else:
                        above_profit_target_price_dict[item[0]] = [[0, item[1], item[2], prev_uprate]]
                prev_day_item = item

        except ValueError:  # pass when there is no data for given company symbol
            pass

        # Don't look items more than lookup_item_limit. This is for fast debugging.
        lookup_item_idx = lookup_item_idx + 1
        if lookup_item_idx > lookup_item_limit-1:
            break

    for date, item in above_target_price_dict.items():
        above_target_price_dict[date].sort(key=lambda q: q[3], reverse=True)
        above_target_price_dict[date] = above_target_price_dict[date][:daily_num]
        above_profit_target_price_dict[date].sort(key=lambda q: q[3], reverse=True)
        above_profit_target_price_dict[date] = above_profit_target_price_dict[date][:daily_num]

    for key, value in above_target_price_dict.items():
        companies_above_target_price_dict[key] = [t[2] for t in above_target_price_dict[key] if t[0] == 1]
        companies_above_profit_target_price_dict[key] = [t[2] for t in above_profit_target_price_dict[key] if t[0] == 1]
        complement_companies_set_dict[key] = list(set(companies_above_target_price_dict[key]) -
                                                  set(companies_above_profit_target_price_dict[key]))
        above_target_price_dict[key] = [sum([x[0] for x in above_target_price_dict[key]])]
        above_profit_target_price_dict[key] = [sum([x[0] for x in above_profit_target_price_dict[key]])]

    sum1 = 0.00000000001    # to escape from divided by zero exception
    sum2 = 0.00000000001    # same as above
    for key, value in above_target_price_dict.items():
        sum1 = sum1 + above_target_price_dict[key][0]
        sum2 = sum2 + above_profit_target_price_dict[key][0]
    sum2_divided_by_sum1 = sum2/sum1

    print("Sum1: {}".format(sum1))
    print("Sum2: {}".format(sum2))
    print("Sum2/Sum1: {}".format(sum2_divided_by_sum1))

    print(above_target_price_dict)
    print(above_profit_target_price_dict)
    print(companies_above_target_price_dict)
    print(companies_above_profit_target_price_dict)
    print(complement_companies_set_dict)

    data_names = [[above_target_price_dict, "AT"],
                  [above_profit_target_price_dict, "APT"],
                  [companies_above_target_price_dict, "CAT"],
                  [companies_above_profit_target_price_dict, "CAPT"],
                  [complement_companies_set_dict, "CC"]]

    for data_name in data_names:
        with open("D{}_C{}_K{:.1f}_P{}_{}_{}.csv".format(lookup_days,
                                                         daily_num, k, profit_percent, list_type, data_name[1]),
                  'w', newline='') as my_file:
            wr = csv.writer(my_file, quoting=csv.QUOTE_ALL)
            for key, value in data_name[0].items():
                wr.writerow([key] + value)


if __name__ == "__main__":
    main()
