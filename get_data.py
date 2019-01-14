import requests
import pandas as pd
from urllib.parse import quote
from bs4 import BeautifulSoup


def create_post_body(insturment_number, from_date, to_date):
    post_params = f'''<post>
        <param name="Exchange" value="NMF"/>
        <param name="SubSystem" value="History"/>
        <param name="Action" value="GetDataSeries"/>
        <param name="AppendIntraDay" value="no"/>
        <param name="Instrument" value="{insturment_number}"/>
        <param name="FromDate" value="{from_date}"/>
        <param name="ToDate" value="{to_date}"/>
        <param name="hi__a" value="0,1,2,4,21,8,10,11,12"/>
        <param name="ext_xslt" value="/nordicV3/hi_table.xsl"/>
        <param name="ext_xslt_lang" value="en"/>
        <param name="ext_xslt_hiddenattrs" value=",ip,iv,"/>
        <param name="ext_xslt_tableId" value="historicalTable"/>
        <param name="app" value="/shares/historicalprices"/>
        </post>'''
    return 'xmlquery=' + quote(post_params)


def fetch_instrument_data(url, headers, post_body):
    req = requests.post(url, data=post_body, headers=headers).text
    return BeautifulSoup(req, 'html.parser')


def parse_instrument_data(insturment_name, from_date, to_date, raw_instrument_data):
    headers = raw_instrument_data.thead.findAll('th')

    column_names = list()
    for header in headers:
        column_names.append(header.getText())

    table_data = pd.DataFrame(columns=column_names)
    table = raw_instrument_data.tbody.findAll('tr')
    for table_row in table:
        values = table_row.findAll('td')
        row = list()
        for value in values:
            row.append(value.getText())
        table_data = table_data.append(pd.DataFrame([row], columns=column_names))

    table_data.to_csv(f'{insturment_name}_{from_date}_{to_date}.csv', index=False, sep=';', decimal=',')


if __name__=='__main__':
    # Instrument values = {'OMXS30': 'SE0000337842'
    #                     'NASDAQ OMX NORDIC 120': 'SE000327087'}
    url = 'http://www.nasdaqomxnordic.com/webproxy/DataFeedProxy.aspx'
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

    post_body = create_post_body('SE0000337842', '2018-10-19', '2018-11-19')
    raw_instrument_data = fetch_instrument_data(url, headers, post_body)
    parse_instrument_data('OMXS30', '2018-10-19', '2018-11-19', raw_instrument_data)
