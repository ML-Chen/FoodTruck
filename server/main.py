from flask import Flask, request, jsonify, Response
from flask_restful import reqparse, Api, Resource
import sys
import os
import random
import requests
from collections import namedtuple
from typing import Dict, Tuple, Optional, Any, List, Callable
import math
from math import ceil
import asyncio
import mysql.connector
from mysql.connector import Error
import re

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
api = Api(app)
try:
    # Check MySQL Workbench > Database > Connect to Database > Test Connection for the host name, etc.
    connection = mysql.connector.connect(
        host='127.0.0.1',
        database='cs4400spring2020',
        user='root',
        password='E55yT^$f&n4Nc&5k'
    )
    cursor = connection.cursor(buffered=True)
except mysql.connector.Error as error:
    print('Failed to connect to database: ' + repr(error))

def db_wrapper(proc_name: str, methods: List[str], args: List[Tuple[str, Dict[str, Any]]], results: bool = False) -> Callable[[None], Response]:
    """
    Be aware of the potential for SQL injection in the following line:
        cursor.execute(f"SELECT * FROM {proc_name + '_result'};")
    Don't let users have access to this function and pass in arbitrary `proc_name`.

    Parameters:
        proc_name
        methods: HTTP methods, such as ['GET'] (if the operation is just fetching data and doesn't modify the database), or ['POST']
        args: e.g., [('username', {'type': str, 'required': True})]. These arguments should be in the same order as the SQL stored procedure, but can be called anything you like.
        results_table: name of the temporary table that results are stored in. If defined, we'll run another query to retrieve these results.

    Returns a function that works as a Flask API endpoint.
    """
    @app.route('/' + proc_name, methods=methods, endpoint=proc_name)
    def new_api() -> Response:
        nonlocal args
        nonlocal results

        parser = reqparse.RequestParser()
        for r in args:
            print(r)
            parser.add_argument(r[0], **(r[1]))
        a = parser.parse_args()
        print(list(a.values()))

        try:
            cursor.callproc(proc_name, args=tuple(a.values()))
            if results:
                cursor.execute(f"SELECT * FROM {proc_name + '_result'};")
                result = cursor.fetchall()
                print(result)
            return jsonify(*result)
        except ValueError as e:
            message = 'Incorrect parameter types'
            print(message + ' ' + str(e))
            return {'error': message}, 405
        except mysql.connector.Error as error:
            print('Failed to register: ' + str(error))
            return {'error': error}, 405
        except Exception as e:
            message = 'Unknown error: ' + str(e)
            print(message)
            return {'error': e}, 400

    return new_api

login = db_wrapper('login', ['POST'], [
    ('username', {'type': str, 'required': True}),
    ('password', {'type': str, 'required': True}),
], True)
register = db_wrapper('register', ['POST'], [
    ('username', {'type': str, 'required': True}),
    ('email', {'type': str, 'required': True}),
    ('first_name', {'type': str, 'required': True}),
    ('last_name', {'type': str, 'required': True}),
    ('password', {'type': str, 'required': True}),
    ('balance', {'type': float}),
    ('i_type', {'type': float, 'required': True, 'choices': ('Admin', 'Manager', 'Staff')}),
])
ad_filter_building_station = db_wrapper('ad_filter_building_station', ['GET'], [
    ('building_name', {'type': str, 'required': True}),
    ('building_tag', {'type': str, 'required': True}),
    ('station_name', {'type': str, 'required': True}),
    ('min_capacity', {'type': str, 'required': True}),
    ('max_capacity', {'type': str, 'required': True}),
], True)
ad_delete_building = db_wrapper('ad_delete_building', ['POST'], [
    ('building_name', {'type': str, 'required': True})
])
ad_add_building_tag = db_wrapper('ad_add_building_tag', ['POST'], [
    ('building_name', {'type': str, 'required': True}),
    ('tag', {'type': str, 'required': True})
])
ad_remove_building_tag = db_wrapper('ad_remove_building_tag', ['POST'], [
    ('building_name', {'type': str, 'required': True}),
    ('tag', {'type': str, 'required': True})
])
# query #7 etc.

def close_connection() -> None:
    connection.close()
    print('MySQL connection closed')