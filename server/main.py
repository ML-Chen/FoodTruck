from flask import Flask, request, jsonify, Response
from flask_restful import reqparse, Api, Resource
from flask_cors import CORS
import sys
import os
import random
import requests
from typing import Dict, Tuple, Optional, Any, List, Callable, NamedTuple
import asyncio
import mysql.connector
from mysql.connector import Error
import re
from secrets import token_hex

app = Flask(__name__)
cors = CORS(app)  # allow CORS on all routes
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

class Auth(NamedTuple):
    username: str
    user_type: str

# Maps tokens to their username and user type
# TODO: store tokens in and retrieve tokens from database. Not that important. Or, load tokens from a local text file so that whenever I restart the server I don't have to log users back in again.
tokens: Dict[str, Auth] = {}

def db_api(procedure: str, http_methods: List[str], inputs: List[Tuple[str, Dict[str, Any]]], get_result: bool = False,
           restrict_by_username: bool = False, restrict_by_food_truck: bool = False) -> Callable[[None], Response]:
    """
    Parameters:
    - procedure: name of the MySQL stored procedure which we will call.
        - The URL for the API endpoint is just '/' plus the name of the procedure (e.g., '/login').
        - Access to the API will be restricted to certain user types if `procedure` begins with 'ad_', 'mn_', or 'cus_'. In this case, an additional required `token` request parameter is automatically.
        - A procedure named 'login' will create a token for the user and return that.
    - http_methods: HTTP methods, such as ['GET'] (if the operation is just fetching data and doesn't modify the database), or ['POST']
    - inputs: request parameters, which will be passed into the stored procedure. These arguments should be in the same order as the SQL stored procedure, but can be called anything you like.
        - Example: [('username', {'type': str, 'required': True}), ('balance', {'type': int, 'default': 0})]
        - See reqparse (https://flask-restful.readthedocs.io/en/latest/reqparse.html) for documentation on other keys we can have in the dictionary, besides 'type', 'required', 'default', etc.
        - When contacting the API, the client can pass these parameters in as query parameters or form body parameters.
    - get_result: whether the procedure creates a table named `procedure + '_result'` (e.g., 'login_result'). If so, we'll make another SELECT query to get that table, after we call the procedure. Then, the response of the API endpoint is the result. Otherwise, the response an empty JSON object {}.
    - restrict_by_username: restrict access to this API endpoint to people whose token corresponds to a user with a 'username', 'customer_username', or 'manager_username' field in inputs.
    - restrict_by_food_truck: restrict access to this API endpoint to people whose token corresponds to a user with a username 'manager_username' in inputs that manages the food truck with the 'food_truck_name' in inputs.

    Returns a function that works as a Flask API endpoint.

    Be aware of the potential for SQL injection in the following line:
        cursor.execute(f"SELECT * FROM {procedure + '_result'};")
    Don't let users have access to this function and pass in arbitrary `procedure`.
    """
    @app.route('/' + procedure, methods=http_methods, endpoint=procedure)
    def new_api() -> Response:
        nonlocal inputs
        nonlocal get_result

        parser = reqparse.RequestParser()
        for arg_name, arg_params in inputs:
            parser.add_argument(arg_name, **arg_params)
        restricted = restrict_by_username or restrict_by_food_truck or procedure.startswith('cus_') or procedure.startswith('mn_') or procedure.startswith('ad_')
        if restricted:
            parser.add_argument('token', type=str, required=True)
        try:
            a = parser.parse_args()
        except Exception as e:
            print(repr(e))
            return {'error': 'Bad request. Expected request arguments: ' + str(parser.args)}, 400
        print('Request: ' + repr(a))
        if restricted:
            token = a['token']
            del a['token']

        try:
            if procedure.startswith('cus_'):
                assert 'Customer' in tokens[token].user_type
            elif procedure.startswith('ad_'):
                assert 'Admin' in tokens[token].user_type
            elif procedure.startswith('mn_'):
                assert 'Manager' in tokens[token].user_type
            
            if restrict_by_username:
                assert tokens[token].username in (a['username'], a['customerUsername'], a['managerUsername'])
            if restrict_by_food_truck:
                cursor.execute("SELECT foodTruckName FROM FoodTruck WHERE managerUsername = %s", (a['managerUsername']))
                assert a['foodTruckName'] in cursor.fetchall()
        except AssertionError as e:
            print(repr(e))
            return {'error': repr(e)}, 400
        except KeyError as e:
            print(repr(e))
            return {'error': "Your token doesn't match a logged in user: " + repr(e)}, 400

        try:
            cursor.callproc(procedure, args=tuple(a.values()))
            if get_result:
                cursor.execute(f"SELECT * FROM {procedure + '_result'};")
                # The next two lines are from https://stackoverflow.com/a/17534004/5139284 by juandesant, CC-BY-SA 4.0
                fields = map(lambda x: x[0], cursor.description)
                result = [dict(zip(fields, row)) for row in cursor.fetchall()]
                if len(result) == 1:
                    result = result[0]
                if procedure == 'login' and result:
                    # TODO: don't generate a new token if the user already exists (honestly not very important though)
                    new_token = token_hex(64)
                    tokens[new_token] = Auth(a['username'], result['userType'])
                    result['token'] = new_token
                print(f'Response: {result}')
                return jsonify(result)
            else:
                return jsonify({})
            
        except ValueError as e:
            message = 'Incorrect parameter types'
            print(message + ' ' + repr(e))
            return {'error': message}, 405
        except mysql.connector.Error as e:
            print('Failed to register: ' + repr(e))
            return {'error': repr(e)}, 405
        except Exception as e:
            message = 'Unknown error: ' + repr(e)
            print(locals())
            return {'error': repr(e)}, 400

    return new_api

# Query #1: login [Screen #1: Login]
# Response: {username: str, userType: str} or [] if no user found
login = db_api('login', ['POST'], [
    ('username', {'type': str, 'required': True}),
    ('password', {'type': str, 'required': True}),
], get_result=True)

# Query #2: register [Screen #2 Register]
# Response: []
register = db_api('register', ['POST'], [
    ('username', {'type': str, 'required': True}),
    ('email', {'type': str, 'required': True}),
    ('firstName', {'type': str, 'required': True}),
    ('lastName', {'type': str, 'required': True}),
    ('password', {'type': str, 'required': True}),
    ('balance', {'type': float}),
    ('type', {'type': float, 'required': True, 'choices': ('Admin', 'Manager', 'Staff')}),
])

# Query #3: ad_filter_building_station [Screen #4 Admin Manage Building & Station]
# As mentioned above in the definition of `db_api`, endpoints beginning with 'ad_' will be restricted to admins.
# The request will need an additional 'token' field which belongs to an admin that has logged in.
# Response: {buildingName: str, tags: str, stationName: str, capacity: int, foodTruckNames: str}
ad_filter_building_station = db_api('ad_filter_building_station', ['GET'], [
    ('buildingName', {'type': str, 'required': True}),
    ('buildingTag', {'type': str, 'required': True}),
    ('stationName', {'type': str, 'required': True}),
    ('minCapacity', {'type': str, 'required': True}),
    ('maxCapacity', {'type': str, 'required': True}),
], get_result=True)

# Query #4: ad_delete_building [Screen #4 Admin Manage Building & Station]
# Response: []
ad_delete_building = db_api('ad_delete_building', ['POST'], [
    ('buildingName', {'type': str, 'required': True})
])

# Query #5: ad_delete_station [Screen #4 Admin Manage Building & Station]
# Response: []
ad_delete_station = db_api('ad_delete_station', ['POST'], [
    ('stationName', {'type': str, 'required': True})
])

# Query #6a: ad_add_building_tag [Screen #5 Admin Add Building Tag]
# Response: []
ad_add_building_tag = db_api('ad_add_building_tag', ['POST'], [
    ('buildingName', {'type': str, 'required': True}),
    ('tag', {'type': str, 'required': True})
])

# Query #6b: ad_remove_building_tag [Screen #5 Admin Remove Building Tag]
# Response: []
ad_remove_building_tag = db_api('ad_remove_building_tag', ['POST'], [
    ('buildingName', {'type': str, 'required': True}),
    ('tag', {'type': str, 'required': True})
])

# Query #7: ad_create_building [Screen #5 Admin Create Building]
# Response: []
ad_create_building = db_api('ad_create_building', ['POST'], [
    ('buildingName', {'type': str, 'required': True}),
    ('description', {'type':str, 'required': True})
])

# Query #8a: ad_view_building_general [Screen #6 Admin Update Building]
# Response: 
ad_view_building_general = db_api('ad_view_building_general', ['GET'], [
    ('buildingName', {'type': str, 'required': True})
], get_result=True)

# Query #8b: ad_view_building_tags [Screen #6 Admin Update Building]
# Response: 
ad_view_building_tags  = db_api('ad_view_building_tags', ['GET'], [
    ('buildingName', {'type': str, 'required': True})
], get_result=True)

# Query #9: ad_update_building [Screen #6 Admin Update Building]
# Response: []
ad_update_building = db_api('ad_update_building', ['POST'], [
    ('oldBuildingName', {'type': str, 'required': True}),
    ('newBuildingname', {'type': str, 'required': True}),
    ('description', {'type':str, 'required': True})
])

# Query #10: ad_get_available_building [Screen #7 Admin Create Station]

# Query #22b: mn_update_foodTruck_staff [Screen #13 Manager Update Food Truck]
# Response: {}
mn_update_foodTruck_staff = db_api('mn_update_foodTruck_staff', ['POST'], [
    ('foodTruckName', {'type': str, 'required': True}),
    ('staffUsername', {'type': str, 'required': True})
], restrict_by_food_truck=True)

# Query #25: mn_summary_detail [Screen #15 Manager Summary Detail]
# Response: [{ date: str, customerName: str, totalPurchase: decimal, orderCount: int, foodNames: str }]
mn_summary_detail = db_api('mn_summary_detail', ['POST'], [
    ('managerUsername', {'type': str, 'required': True}),
    ('foodTruckName', {'type': str, 'required': True})
], get_result=True, restrict_by_username=True)
# no need to do restrict_by_food_truck=True because the query already does a join with the manager's username

def close_connection() -> None:
    connection.close()
    print('MySQL connection closed')