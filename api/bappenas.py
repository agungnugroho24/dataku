import requests, requests_cache, random, datetime, dateparser, json
import pandas as pd
import parmap

from multiprocessing import Pool
import pandas as pd

requests_cache.install_cache('bappenas_cache', expire_after=28800)
TOKEN = '''eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjIiLCJ1c2VybmFtZSI6InBsaiIsImlhdCI6MTU0MDM0ODYwNiwiZXhwIjoxNTQwMzUyMjA2fQ.DLcgnMpC-NrBpHoiLF3CTz93v3MyICm7VOH5IWXPfNE'''
HEADERS = {'Authorization':'{}'.format(TOKEN),'Content-Type':'application/json'}

with requests.Session() as s:
    s.headers.update(HEADERS)

global baseurl
baseurl = "http://api.satudata.bappenas.go.id/series/api/"

def get_table_for_id(table_id):
    base_url = baseurl + "data"
    params = dict()
    params['table'] = table_id
    query = base_url + "?"
    for param in params:
        query = query + "{}={}&".format(param,params[param])
    table = requests.get(query, headers={'Authorization': TOKEN})
    try:
        if len(table.json()['data']) > 2:
            return table.json()['data']
    except Exception as e:
        print(e)
        return

def get_subjects():
    #params = dict()
    base_url = baseurl + "subj"
    query = base_url + "?"
    subjects = requests.get(query, headers={'Authorization': TOKEN})
    return subjects.json()['data']

def get_table_ids_for_subject(subject_id):
    params = dict()
    params['subject'] = subject_id
    base_url = baseurl + "tablebysubj"
    query = base_url + "?"
    for param in params:
        query = query + "{}={}&".format(param,params[param])
    tables = requests.get(query, headers={'Authorization': TOKEN})
    all_tables = tables.json()['data']
    for table in all_tables:
        table['subject_id'] = subject_id
    return all_tables

def get_all_tables_for_subject_id(subject_id):
    pool = Pool(4)
    tables = list()
    ids = get_table_ids_for_subject(subject_id)
    """for id in ids:
        table = get_table_for_id(id['id'])
        tables.append(table) """
    tables = pool.map(get_table_for_id,[id['id'] for id in ids])
    pool.close()
    pool.join()
    tables = [table for table in tables if (table is not None) and len(table) > 2]
    return tables

def get_range_for_subject(table_set):
    years = dict()
    regions = dict()
    for table in table_set:
        for period in table['period']:
            years[period['val']] = period['label']
        for region in table['region']:
            regions[region['val']] = region['label']
    data = dict()
    data['regions'] = regions
    data['years'] = years
    return data

def has_province_data(table):
    regions = list(set(table['region'].tolist()))
    #regions = list(get_range_for_subject([table])['regions'].values())
    all_provinces = [
         'Aceh',
         'Bali',
         'Bangka Belitung',
         'Banten',
         'Bengkulu',
         'Gorontalo',
         'Jakarta Raya',
         'Jambi',
         'Jawa Barat',
         'Jawa Tengah',
         'Jawa Timur',
         'Kalimantan Barat',
         'Kalimantan Selatan',
         'Kalimantan Tengah',
         'Kalimantan Timur',
         'Kepulauan Riau',
         'Lampung',
         'Maluku',
         'Maluku Utara',
         'Nusa Tenggara Barat',
         'Nusa Tenggara Timur',
         'Papua',
         'Papua Barat',
         'Riau',
         'Sulawesi Barat',
         'Sulawesi Selatan',
         'Sulawesi Tengah',
         'Sulawesi Tenggara',
         'Sulawesi Utara',
         'Sumatera Barat',
         'Sumatera Selatan',
         'Sumatera Utara',
         'Yogyakarta',
         'Kalimantan Utara',
         'National'
    ]
    region_match = len([region for region in regions if region in all_provinces])
    if region_match > (len(all_provinces) / 2):
        return True
    else:
        return False
        
def get_tables_with_any_subject():
    all_tables = list()
    subjects = get_subjects()
    for subject in subjects:
        tables = get_table_ids_for_subject(subject['id'])
        all_tables.extend(tables)
    return all_tables

def make_friendly_name(key):
    n = len(key)
    r = n-4
    table = key[0:4]
    variable = key[4:9]
    turvar = key[9]
    period = key[10:12]
    derperiod = key[12:r]
    region = key[r:n+1]
    return "{},{},{},{},{},{}".format(table,variable,turvar,period,derperiod,region)

def make_flat_table(tabular_data):
    table = tabular_data.groupby(['variable','region','period']).sum().unstack()   
    return table['value'].reset_index()

def make_tabular_data(table,graph_type=None):
    try:
        columns = ['table','variable','turvar','period','derperiod','region','value']
        frame = pd.DataFrame.from_dict(table['value'], orient='index').reset_index()
        frame.columns = ['key','value']
        frame.key = frame.key.apply(make_friendly_name)
        frame = pd.concat([frame.key.str.split(',', expand=True),frame.value], axis=1)
        frame.columns = columns
        frame.value = pd.to_numeric(frame.value)
        if graph_type == 'Map':
            columns = [col for col in columns if col != 'region']
        keys = columns[1:-1]
        mappedLabel = { key: { o['val']: o['label'] for o in table[key] } for key in keys }
        for x in keys: 
            try:
                frame[x] = frame[x].apply(lambda o: mappedLabel[x][o])
            except:
                continue
        frame[columns[0]] = table[columns[0]]['label']
        frame.period = frame.period.astype(int)
        if graph_type == 'Map':
            frame.region = frame.region.astype(str).str.rstrip('0')
        return frame
    except Exception as e:
        print(table)
        print(e)
        return

def parse_key(key):
	hair = len(key) - 4
	return { 'table' : key[:4], 'variable' : key[4:9], 'turvar' : key[9], 'period' : key[10:12], 'derperiod' : key[12:hair], 'region' : key[hair:] }

def construct_tabular(table):
	columns = ['table','variable','turvar','period','derperiod','region','value']
	keys = columns[1:-1]
	mappedLabel = { key: { o['val']: o['label'] for o in table[key] } for key in keys }
	mappedLabel[columns[0]] = { table[columns[0]]['val'] : table[columns[0]]['label']}

	return [ dict({ key: mappedLabel[key][val] for key, val in parse_key(crude).items() }, **{ 'value': value }) for crude, value in table['value'].items() ]

def make_stats_from_tableset(table_set, number_of_stats=6,start_year=None,end_year=2100,region=None):
    stats = list()
    stats = parmap.map(make_stats_from_table,table_set,start_year=start_year,end_year=end_year,region=region)
    stats = [stat for stat in stats if stat is not None]
    if len(stats) > 6:
        stats = random.sample(stats, 6)
    return stats

def make_stats_from_table(this_frame,start_year,end_year,region):
    try:
        tabular_data = make_tabular_data(this_frame)
        if start_year:
            tabular_data = tabular_data[(tabular_data.period >= start_year) & (tabular_data.period <= end_year)]
        if region is not None:
            tabular_data = tabular_data[tabular_data.region == region]
        tabular_data = tabular_data[tabular_data['period'] == tabular_data['period'].max()]
        groupframe = tabular_data.groupby(['variable','region','period']).sum()
        stat = groupframe.sample(1)
        headline = stat.index.get_values()[0][0]
        if (len(headline) < 10) or ('+' in headline):
            headline = "{}, {}".format(this_frame['table']['label'], headline)
        #Make it a % if it's a percentage
        number = round((float(stat.value[0])),2)

        if 'persentase' in str.lower(headline):
            number = round(number,2)
            number = "{}%".format(str(number))
        subtitle = "{}, {}".format(stat.index.get_values()[0][1],stat.index.get_values()[0][2])
        #stats.append((headline,number,subtitle))
    except Exception as e:
        print(e)
        return None
    return headline,number,subtitle

def make_graphs_for_tableset(table_set,start_year,end_year,region):
    graphs = list()
    graphs = parmap.map(make_graph,table_set,start_year=start_year,end_year=end_year,region=region)
    return graphs

def make_map(variable,regions):
    grouped = variable.groupby(['region','period']).sum().unstack()
    most_recent_year = grouped['value'][grouped['value'].columns.max()]
    data = list()
    pairs = list(zip(most_recent_year.index,most_recent_year.tolist()))
    for pair in pairs:
        item = dict()
        item['prov_id'] = pair[0]
        item['value'] = pair[1]
        data.append(item)
    with_id = list()
    for item in data:
        this_prov = dict()
        this_prov['prov_id'] = regions[item['prov_id']].rstrip('0')
        this_prov['value'] = item['value']
        if len(this_prov['prov_id']) > 1:
            with_id.append(this_prov)
    return with_id

def make_map_for_table(table,start_year=1900,end_year=2100,region=None):
    graph_set = list()
    tabular_data = make_tabular_data(table)
    if start_year is not None:
        tabular_data = tabular_data[(tabular_data.period >= start_year) & (tabular_data.period <= end_year)]
    if region is not None:
        tabular_data = tabular_data[tabular_data.region == region]
    ranges = get_range_for_subject([table])
    year_range = sorted(list(ranges['years'].values()))
    regions = ranges['regions']
    regions = dict([(v,k) for (k,v) in regions.items()])
    variables = tabular_data.groupby('variable')
    for title,variable in variables:
        graph = dict()
        graph['variable'] = str(title)
        graph['table_id'] = table['table']['val']
        graph['type'] = 'Map'
        graph['is_map'] = True
        graph['desc'] = str(title)
        graph['title'] = table['table']['label']
        if len(graph['desc']) < 10:
            graph['desc'] = "{}, {}".format(table['table']['label'],graph['desc'])
        graph['year'] = "{}-{}".format(str(year_range[0]),str(year_range[-1]))
        graph['data'] = dict()
        graph['data'] = make_map(variable,regions)
        graph_set.append(graph)
    return graph_set


def make_graph(table,start_year=1900,end_year=2100,region=None,graph_type=None):
    graph_set = list()
    tabular_data = make_tabular_data(table)
    if start_year is not None:
        tabular_data = tabular_data[(tabular_data.period >= start_year) & (tabular_data.period <= end_year)]
    if region is not None:
        tabular_data = tabular_data[tabular_data.region == region]
    variables = tabular_data.groupby('variable')
    ranges = get_range_for_subject([table])
    year_range = sorted(list(ranges['years'].values()))
    regions = ranges['regions']
    regions = dict([(v,k) for (k,v) in regions.items()])
    for title,variable in variables:
        try:
            graph = dict()
            graph['variable'] = str(title)
            graph['table_id'] = table['table']['val']
            if has_province_data(variable):
                graph['type'] = random.choice(['Map','Bar','Line'])
                graph['is_map'] = True
            else:
                graph['type'] = random.choice(['Bar','Line'])
                graph['is_map'] = False
            graph['desc'] = str(title)
            if graph_type == 'Map':
                graph['type'] = 'Map'
                graph['is_map'] = True
            graph['title'] = table['table']['label']
            if (len(graph['desc']) < 10) or ('+' in graph['desc']):
                graph['desc'] = "{}, {}".format(table['table']['label'],graph['desc'])
            graph['year'] = "{}-{}".format(str(year_range[0]),str(year_range[-1]))
            graph['data'] = dict()
            if (graph['type'] == 'Map'):
                graph['data'] = make_map(variable,regions)
            else:
                grouped = variable.groupby('period').sum()
                graph['type'] = random.choice(['Bar','Line'])
                graph['data']['labels'] = list(grouped.index)
                graph['data']['series'] = list()
                graph['data']['series'].append(list(grouped.value.round(2)))
                #graph['data']['series'] = [ round(item, 2) for item in graph['data']['series'] ]
                if len(graph['data']['series'][0]) < 3:
                    continue
                if len(graph['data']['series'][0]) < 4:
                    graph['type'] = 'Pie'
                    graph['data']['labels'] = list(grouped.index)
                    graph['data']['series'] = list(grouped.value) 
            graph_set.append(graph)
        except Exception as e:
            errorstring = "Had a problem creating the graph for table {}. The error was:".format(table['table']['val'])
            print(errorstring)
            print(e)
    return graph_set