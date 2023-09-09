import os
from flask import Flask, redirect, url_for, session, request, jsonify, render_template, Response
#import flask_restful
from werkzeug.datastructures import Headers
import pandas as pd
import json
import random
import sqlite3
from flask_cors import CORS
from flask_caching import Cache
import bappenas
import datetime
from dateutil.relativedelta import relativedelta

cache = Cache(config={'CACHE_TYPE': 'simple','CACHE_DEFAULT_TIMEOUT': 96400})
app = Flask(__name__)
cache.init_app(app)
app.debug = True
CORS(app)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def filter_by_region(table_set, target_region):
    filtered_tables = list()
    for table in table_set:
        regions = [region['val'] for region in table['region']]
        if target_region in regions:
            filtered_tables.append(table)
    return filtered_tables

def filter_by_year(table_set, year):
    filtered_tables = list()
    for table in table_set:
        years = [period['val'] for period in table['period']]
        if year in years:
            filtered_tables.append(table)
    return filtered_tables

@app.route('/subjects', methods=['GET'])
@cache.cached()
def get_subjects():
    subjects = bappenas.get_subjects()
    return jsonify(subjects)

@app.route('/map/<table_id>', methods=['POST','GET'])
def make_map_for_variable(table_id,variable=None,region=None):
    table = bappenas.get_table_for_id(table_id)
    args = request.args
    if 'region' in args:
        region = args['region']
    else:
        region = None
    variable = args['variable']
    maps = bappenas.make_map_for_table(table,region=region)
    this_map = [graph for graph in maps if graph['variable'] == variable]
    if len(this_map == 0):
        error_string = "Couldn't generate a map for this table"
        return jsonify(error_string)
    return jsonify(this_map)


@app.route('/stats/<subject_id>', methods=['GET'])

def return_stats_for_subject(subject_id):
    region = None
    start_year = None
    end_year = 2100
    data = dict()
    args = request.args
    subjects = bappenas.get_subjects()
    subject_ids = list([subject['id'] for subject in subjects])
    if subject_id not in subject_ids:
        error = "The subject_id {} doesn't exist".format(str(subject_id))        
        raise InvalidUsage(error, status_code=400)
    tables = bappenas.get_all_tables_for_subject_id(subject_id)
    tables = [table for table in tables if len(table['value']) > 10]
    ranges = bappenas.get_range_for_subject(tables)
    if 'region' in args:
        regions = ranges['regions'].values()
        if args['region'] not in regions:
            error = "There are no records for region {} for this subject".format(str(args['region']))        
            raise InvalidUsage(error, status_code=400)
        tables = filter_by_region(tables,args['region'])
        region = args['region']
    if 'start_year' in args:
        start_year = int(args['start_year'])
    if 'end_year' in args:
        end_year = int(args['end_year'])
    data['status'] = 'Success'
    data['subject'] = next(item for item in subjects if item["id"] == str(subject_id))
    data['summary'] = bappenas.make_stats_from_tableset(table_set=tables,start_year=start_year,end_year=end_year,region=region)
    return jsonify(data)

@app.route('/subjects/<subject_id>/', methods=['GET'])
@cache.cached(query_string = True)

def get_all_tables_for_subject_id(subject_id):
    region = None
    start_year = None
    end_year = 2100
    data = dict()
    args = request.args

    subjects = bappenas.get_subjects()
    subject_ids = list([subject['id'] for subject in subjects])
    if subject_id not in subject_ids:
        error = "The subject_id {} doesn't exist".format(str(subject_id))        
        raise InvalidUsage(error, status_code=400)

    tables = bappenas.get_all_tables_for_subject_id(subject_id)
    #tables = [table for table in tables if len(table['value']) > 10]
    ranges = bappenas.get_range_for_subject(tables)
    
    if 'region' in args:
        regions = ranges['regions'].values()
        if args['region'] not in regions:
            error = "There are no records for region {} for this subject".format(str(args['region']))        
            raise InvalidUsage(error, status_code=400)
        #tables = filter_by_region(tables,args['region'])
        region = args['region']

    if 'start_year' in args:
        start_year = int(args['start_year'])

    if 'end_year' in args:
        end_year = int(args['end_year'])

    data['status'] = 'Success'
    data['subject'] = next(item for item in subjects if item["id"] == str(subject_id))
    
    data['summary'] = bappenas.make_stats_from_tableset(table_set=tables,start_year=start_year,end_year=end_year,region=region)
    
    data['graphs'] = list()
    #number_of_tables_to_graph = 20
    #if number_of_tables_to_graph > len(tables):
    #    number_of_tables_to_graph = len(tables)

    #tables_to_graph = random.sample(tables,number_of_tables_to_graph)
    tables_to_graph = tables
    graphs = bappenas.make_graphs_for_tableset(table_set=tables_to_graph,start_year=start_year,end_year=end_year,region=region)
    
    for graph in graphs:
        if graph is not None:
            data['graphs'].extend(graph)

    data['graphs'] = [graph for graph in data['graphs'] if graph is not None]
    random.shuffle(data['graphs'])
    #if len(data['graphs']) > 6:
    #    data['graphs'] = random.sample(data['graphs'],6)
    return jsonify(data)

@app.route('/range/<subject_id>', methods=['GET'])
@cache.cached(timeout=360)

def get_range(subject_id):
    subjects = bappenas.get_subjects()
    subject_ids = list([subject['id'] for subject in subjects])
    if subject_id not in subject_ids:
        error = "The subject_id {} doesn't exist".format(str(subject_id))        
        raise InvalidUsage(error, status_code=400)
    data = dict()
    data['subject'] = next(item for item in subjects if item["id"] == str(subject_id))
    tables = bappenas.get_all_tables_for_subject_id(subject_id)
    ranges = bappenas.get_range_for_subject(tables)
    data['regions'] = ranges['regions']
    data['years'] = ranges['years']
    return jsonify(data)

@app.route('/table/<dataset_id>', methods=['GET'])
@cache.cached()
def get_table(dataset_id):
    #Get Bappenas Table
    current_table = bappenas.get_table_for_id(dataset_id)
    tabular_data = bappenas.make_tabular_data(current_table)
    flat_table = bappenas.make_flat_table(tabular_data)
    return flat_table.to_html(index=False)

@app.route('/download/<dataset_id>', methods=['GET'])
@cache.cached()
def download_table(dataset_id):
    #Get Bappenas Table
    current_table = bappenas.get_table_for_id(dataset_id)
    tabular_data = bappenas.make_tabular_data(current_table)
    #flat_table = bappenas.make_flat_table(tabular_data)
    return Response(tabular_data.to_csv(index=False), mimetype='text/csv')
    
if __name__ == '__main__':
    app.run('0.0.0.0',debug=True)


    # graph - return chart for all the datasets in that subject

