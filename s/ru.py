# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import traceback
import re
import datetime
import MySQLdb

columns = {
'股票名称': 'mingcheng',
'今开': 'jinkai',
'成交量': 'chengjiaoliang',
'最高': 'zuigao',
'涨停': 'zhangting',
'内盘': 'neipan',
'成交额': 'chengjiaoe',
'委比': 'weibi',
'流通市值': 'liutongshizhi',
'市盈率MRQ': 'shiyinglv',
'每股收益': 'meigushouyi',
'总股本': 'zongguben',
'昨收': 'zuoshou',
'换手率': 'huanshoulv',
'最低': 'zuidi',
'跌停': 'dieting',
'外盘': 'waipan',
'振幅': 'zhenfu',
'量比': 'liangbi',
'总市值': 'zongshizhi',
'市净率': 'shijinglv',
'每股净资产': 'meigujingzichan',
'流通股本': 'liutongguben',
'zuixin':'zuixin',
'zhangfu' : 'zhangfu',
'zhangbi' : 'zhangbi',
'zhuliliurubili':'zhuliliurubili',
'zhuliliuruzijin':'zhuliliuruzijin',
'sanhuliurubili':'sanhuliurubili',
'sanhuliuruzijin':'sanhuliuruzijin',
'zhuliliuchubili':'zhuliliuchubili',
'zhuliliuchuzijin':'zhuliliuchuzijin',
'sanhuliuchubili':'sanhuliuchubili',
'sanhuliuchuzijin':'sanhuliuchuzijin',
'净值':'jingzhi',
'折价率':'zhejialv'
}



def getHTMLText(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""


def getStockList(lst, stockURL):
    html = getHTMLText(stockURL)
    soup = BeautifulSoup(html, 'html.parser')
    a = soup.find_all('a')
    for i in a:
        try:
            href = i.attrs['href']
            lst.append(re.findall(r"[s][hz]\d{6}", href)[0])
        except:
            continue


def getStockInfo(lst, stockURL, fpath):
    count = 0
    dt = datetime.datetime.now().strftime("%Y-%m-%d")
    db = MySQLdb.connect("localhost", "share", "share", "share", charset='utf8')

    cursor = db.cursor()
    for stock in lst:
        url = stockURL + stock + ".html"
        html = getHTMLText(url)
        try:
            if html == "":
                continue
            infoDict = {}
            soup = BeautifulSoup(html, 'html.parser')
            stockInfo = soup.find('div', attrs={'class': 'stock-bets'})

            name = stockInfo.find_all(attrs={'class': 'bets-name'})[0]
            infoDict.update({'股票名称': name.text.split()[0]})

            keyList = stockInfo.find_all('dt')
            valueList = stockInfo.find_all('dd')
            for i in range(len(keyList)):
                key = keyList[i].text
                val = valueList[i].text
                infoDict[key] = val

            stock_newest = soup.find('div', attrs={'class': 'price'})
            newest_price = stock_newest.find('strong').text
            zhangfu = stock_newest.find_all('span')[0].text
            zhangbi = stock_newest.find_all('span')[1].text
            infoDict['zuixin'] = newest_price
            infoDict['zhangfu'] = zhangfu
            infoDict['zhangbi'] = zhangbi

            # zijin = soup.find('div', attrs={'class': 'side-fund-today'})
            # zhuliliuru = zijin.find_all()[0]
            # zhuliliurubili = zhuliliuru.find_all()[1].text
            # zhuliliuruzijin = zhuliliuru.find_all()[2].text
            # sanhuliuru = zijin.find_all()[1]
            # sanhuliurubili = sanhuliuru.find_all()[1]# .text
            # sanhuliuruzijin = sanhuliuru.find_all()[2].text
            # zhuliliuchu = zijin.find_all()[2]
            # zhuliliuchubili = zhuliliuchu.find_all()[1].text
            # zhuliliuchuzijin = zhuliliuchu.find_all()[2].text
            # sanhuliuchu = zijin.find_all()[3]
            # sanhuliuchubili = sanhuliuchu.find_all()[1].text
            # sanhuliuchuzijin = sanhuliuchu.find_all()[2].text

            # infoDict['zhuliliurubili'] = zhuliliurubili
            # infoDict['zhuliliuruzijin'] = zhuliliuruzijin
            # infoDict['sanhuliurubili'] = sanhuliurubili
            # infoDict['sanhuliuruzijin'] = sanhuliuruzijin
            # infoDict['zhuliliuchubili'] = zhuliliuchubili
            # infoDict['zhuliliuchuzijin'] = zhuliliuchuzijin
            # infoDict['sanhuliuchubili'] = sanhuliuchubili
            # infoDict['sanhuliuchuzijin'] = sanhuliuchuzijin



            with open(fpath, 'a', encoding='utf-8') as f:
                f.write(str(infoDict) + '\n')
                insert_into_db(db, cursor, infoDict, dt)
                count = count + 1
                print("\r当前进度: {:.2f}%".format(count * 100 / len(lst)), end="")
        except BaseException as e:
            count = count + 1
            print("error")
            print(e)
            print(url)
            print("\r当前进度: {:.2f}%".format(count * 100 / len(lst)), end="")
            continue
    cursor.close()
    db.close()

def insert_into_db(db, cursor, info_dict,dt):
    table_name='gupiaoxiangqing'
    sql_key = ''  # 数据库行字段
    sql_value = ''  # 数据库值
    for key in info_dict.keys():  # 生成insert插入语句
        sql_value = (sql_value + '"' + info_dict[key] + '"' + ',')
        sql_key = sql_key + ' ' + columns[key] + ','

    sql_value = sql_value + '"'+dt+'"'
    sql_key = sql_key + ' getdate'
    try:
        cursor.execute(
            "INSERT INTO %s (%s) VALUES (%s)" % (table_name, sql_key, sql_value))
        db.commit()  # 提交当前事务
    except BaseException as e:
        print(e.with_traceback())

def main():
    stock_list_url = 'http://quote.eastmoney.com/stocklist.html'
    stock_info_url = 'https://gupiao.baidu.com/stock/'
    output_file = 'D:/BaiduStockInfo.txt'
    slist = []
    getStockList(slist, stock_list_url)
    getStockInfo(slist, stock_info_url, output_file)


main()