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

def db_wrapper(proc_name: str, methods: List[str], args: List[Tuple[str, Dict[str, Any]]]) -> function:
    """
    Parameters:
        proc_name
        methods: HTTP methods, such as ['GET'] (if the operation is just fetching data and doesn't modify the database), or ['POST']
        args: e.g., [('username', {'type': str, 'required': True})]. These arguments should be in the same order as the SQL stored procedure, but can be called anything you like.
    """


    @app.route('/' + proc_name, methods=methods)
    def new_api() -> Response:
        nonlocal args

        parser = reqparse.RequestParser()
        for r in args:
            parser.add_argument(r[0], **r[1])
        args = parser.parse_args()

        try:
            cursor.callproc(proc_name, [args.values()])
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

@app.route('/login', methods=['POST'])
def login() -> Response:
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True)
    parser.add_argument('password', type=str, required=True)
    args = parser.parse_args()

    try:
        cursor.callproc('login', [args['username'], args['password']])
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

@app.route('/register', methods=['POST'])
def register() -> Response:
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True)
    parser.add_argument('email', type=str, required=True)
    parser.add_argument('first_name', type=str, required=True)
    parser.add_argument('last_name', type=str, required=True)
    parser.add_argument('password', type=str, required=True)
    parser.add_argument('balance', type=float, required=True)
    parser.add_argument('i_type', type=str, required=True, choices=('Admin', 'Manager', 'Staff'))
    args = parser.parse_args()

    try:
        username: str = args['username']
        email: str = args['email']
        first_name: str = args['first_name']
        last_name: str = args['last_name']
        password: str = args['password']
        balance: float = args['balance']
        i_type: float = args['i_type']
        cursor.callproc('register', [username, email, first_name, last_name, password, balance, i_type])
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

@app.route('/ad_filter_building_station', methods=['GET'])
def ad_filter_building_station() -> Response:
    parser = reqparse.RequestParser()
    parser.add_argument('building_name', type=str, required=True)
    parser.add_argument('building_tag', type=str, required=True)
    parser.add_argument('station_name', type=str, required=True)
    parser.add_argument('min_capacity', type=int, required=True)
    parser.add_argument('max_capacity', type=int, required=True)
    args = parser.parse_args()

    try:
        cursor.callproc('ad_filter_building_station', [args['building_name'], args['building_tag'], args['station_name'], args['min_capacity'], args['max_capacity']])
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

@app.route('/ad_delete_building', methods=['POST'])
def ad_delete_building() -> Response:
    parser = reqparse.RequestParser()
    parser.add_argument('building_name', type=str, required=True)
    args = parser.parse_args()

    try:
        cursor.callproc('ad_delete_building', [args['building_name']])
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

def close_connection() -> None:
    connection.close()
    print('MySQL connection closed')