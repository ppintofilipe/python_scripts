from urllib.request import urlopen
import time

import requests
from bs4 import BeautifulSoup as bsp
import pandas as pd

def read_cello(url):
    '''
    This method reads the output of an already known Cellossaurus
    Accession Number.
    Using this as input, it outputs a dictionary comprising all the
    information available at the cell line page.

    INPUT:
        url     str     url of the cell line page in Cellossaurus.

    RETURNS:
                dict   comprising all the information available in the page
                       given as input.
    '''
    pg = urlopen(url)
    soup = bsp(pg, 'html.parser')
    tbl = soup.find('table')

    rows = tbl.find_all('tr')

    vals = []
    keas = []

    for row in rows:
        cols = row.find_all('td')
        ttls = row.find_all('th')

        vals.append([ele.text.strip() for ele in cols])
        keas.append([ele.text.strip() for ele in ttls])
    
    t_keys = []

    for i in keas:
        if len(i) == 0:
            k = 'NA'
        else:
            k = i[0]
        t_keys.append(k)

    return {t_keys[x]: vals[x] for x in range(len(keas))}

def find_cell(cell_name):
    '''
    For cases when the accesion number of the cell line is unknown,
    this funcion can be used to find it by making a simple query
    in cellossaurus using accession numbers of other databases
    (eg. CCLE; NCI...)
    Outuputs the specific url of the first cell line in the results
    page.

    INPUT:
        cell_name  str     value wanted as query.

    RETURNS:
        url        str     url of the page correspondinto to that query.
    '''

    filler = {
        'input': cell_name,
    }

    r = requests.post('https://web.expasy.org/cgi-bin/cellosaurus/search', data = filler, timeout=(3.05, 27))

    results = []

    for x in r.iter_lines():
        url_str = str(x).split('"')
        if "<tr><td><a href=" in url_str[0]:
            results.append(url_str[1])
    
    return str('https://web.expasy.org' + results[0])

def get_disease(cell, info = None):
    '''
    Allows for the output of only one information available at
    cellossaurus. If no information is given, the whole
    dictionay (corresponding to the cell line page) is returned.

    INPUT:
            cell    str     url of the cell line page in Cellossaurus.
            info    str     name of the information the user wants to
                            retrieve. corresponds to the indexes in
                            the results page in cellossaurus.
    '''
    query_val = find_cell(cell)
    cell_info = read_cello(query_val)

    if info:
        return cell_info[info][0]
    else:
        return cell_info

def produce_output(vals, info = 'Disease', output_name = None):
    '''
    Allows automated queries using cell names from a list. If only
    one name is given (as a form of a string), the output is returned
    printed on the screen. Otherwise, a csv file is produced (named
    after something that the user gives as input).

    INPUT:
            vals         str or list  names of the cell lines to be retrieved.
            info         str          name of the information the user wants to
                                      retrieve. corresponds to the indexes in
                                      the results page in cellossaurus.
            output_name  str          name of the output file (will be a csv file!).
    '''
    if type(vals) == list:
        output_file = open('{}.csv'.format(output_name), 'w')
        output_file.write('ds_name,disease\n')
        for i in vals:
            try:
                inform = get_disease(i, info = info)
                print(inform)
                output_file.write('{},{}\n'.format(i, inform))
            except:
                print(i, ' produced an error. It was not included in output.')
        output_file.close()
    
    else:
        print(i, get_disease(i, info = info), sep=' | ')


ds = pd.read_csv('ef_CNV.csv')
wanted = list(ds['cells'])

produce_output(wanted, output_name='cell_line_diseases')
