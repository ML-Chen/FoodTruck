from flask import Flask, request, jsonify, Response
from flask_restful import reqparse, Api, Resource
import sys
import os
import random
import requests
from collections import namedtuple
from typing import Dict, Tuple, Optional, Any
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
    connection = mysql.connector.connect(
        host='localhost',
        database='Electronics',
        user='pynative',
        password='pynative@#29'
    )
    cursor = connection.cursor()
except mysql.connector.Error as error:
    print('Failed to connect to database: ' + error)

def db_wrapper(proc_name: str, methods: List[str], args: List[Tuple[str, Dict[str, Any]]], results_table: str = None) -> function:
    """
    Parameters:
        proc_name
        methods: HTTP methods, such as ['GET'] (if the operation is just fetching data and doesn't modify the database), or ['POST']
        args: e.g., [('username', {'type': str, 'required': True})]. These arguments should be in the same order as the SQL stored procedure, but can be called anything you like.
        results_table: name of the temporary table that results are stored in. If defined, we'll run another query to retrieve these results.
    """
    @app.route('/' + proc_name, methods=methods)
    def new_api() -> Response:
        nonlocal args
        nonlocal results_table

        parser = reqparse.RequestParser()
        for r in args:
            parser.add_argument(r[0], **r[1])
        args = parser.parse_args()

        try:
            cursor.callproc(proc_name, args.values())
            if results_table:
                cursor.execute("SELECT * FROM %s", (results_table,))
            result = [r.fetchall() for r in cursor.stored_results()]
            return jsonify(*result)
        except ValueError as e:
            message = 'Incorrect parameter types'
            print(message + ' ' + e)
            return {'error': message}, 405
        except mysql.connector.Error as error:
            print('Failed to register: ' + error)
            return {'error': error}, 405
        except Exception as e:
            message = 'Unknown error: ' + e
            print(message)
            return {'error': e}, 400

    return new_api

login = db_wrapper('login', ['POST'], [
    ('username', {'type': str, 'required': True}),
    ('password', {'type': str, 'required': True}),
])
register = db_wrapper('register', ['POST'], [
    ('username', {'type': str, 'required': True}),
    ('email', {'type': str, 'required': True}),
    ('first_name', {'type': str, 'required': True}),
    ('last_name', {'type': str, 'required': True}),
    ('password', {'type': str, 'required': True}),
    ('balance', {'type': float}),
    ('i_type', {'type': float, 'required': True, 'choices': ('Admin', 'Manager', 'Staff')}),
])
ad_delete_building = db_wrapper('ad_filter_building_station', ['GET'], [
    ('building_name', {'type': str, 'required': True}),
    ('building_tag', {'type': str, 'required': True}),
    ('station_name', {'type': str, 'required': True}),
    ('min_capacity', {'type': str, 'required': True}),
    ('max_capacity', {'type': str, 'required': True}),
])
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
ad_remove_building_tag = db_wrapper('ad_remove_building_tag', ['POST'], [
    ('building_name', {'type': str, 'required': True}),
    ('tag', {'type': str, 'required': True})
])
# etc.

def close_connection() -> None:
    connection.close()
    print('MySQL connection closed')