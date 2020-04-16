from flask import Flask, request, jsonify, Response
from flask_restful import reqparse, Api, Resource
import sys
import os
import random
import requests
from typing import Dict, Tuple, Optional, Any, List, Callable, NamedTuple
from typing_extensions import Literal
import asyncio
import mysql.connector
from mysql.connector import Error
import re
from secrets import token_hex

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

class Auth(NamedTuple):
    username: str
    user_type: str

# Maps tokens to their username and user type
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
    @app.route('/' + procedure, methods=methods, endpoint=procedure)
    def new_api() -> Response:
        nonlocal inputs
        nonlocal get_result

        parser = reqparse.RequestParser()
        for arg_name, arg_params in inputs:
            print(arg_name, arg_params)
            parser.add_argument(arg_name, **arg_params)
        if restrict_by_username or restrict_by_food_truck or procedure.startswith('cus_') or procedure.startswith('mn_') or procedure.startswith('ad_'):
            parser.add_argument('token', type=str, required=True)
        a = parser.parse_args()
        print(list(a.values()))
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
                assert tokens[token].username in (a['username'], a['customer_username'], a['manager_username'])
            if restrict_by_food_truck:
                cursor.execute("SELECT foodTruckName FROM FoodTruck WHERE managerUsername = %s", (a['manager_username']))
                assert a['food_truck_name'] in cursor.fetchall()
        except AssertionError as e:
            print(str(e))

        try:
            cursor.callproc(procedure, args=tuple(a.values()))
            if get_result:
                cursor.execute(f"SELECT * FROM {procedure + '_result'};")
                # The next two lines are from https://stackoverflow.com/a/17534004/5139284 by juandesant, CC-BY-SA 4.0
                fields = map(lambda x: x[0], cursor.description)
                result = [dict(zip(fields, row)) for row in cursor.fetchall()]
                print(result)
                if procedure == 'login' and result:
                    new_token = token_hex(64)
                    tokens[new_token] = Auth(a['username'], result['userType'])
                    result['token'] = new_token
                return jsonify(*result)
            else:
                return jsonify({})
            
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

# Query #1: login [Screen #1: Login]
# Response: {username: str, userType: str}
login = db_api('login', ['POST'], [
    ('username', {'type': str, 'required': True}),
    ('password', {'type': str, 'required': True}),
], get_result=True)

# Query #2: register [Screen #2 Register]
# Response: {}
register = db_api('register', ['POST'], [
    ('username', {'type': str, 'required': True}),
    ('email', {'type': str, 'required': True}),
    ('first_name', {'type': str, 'required': True}),
    ('last_name', {'type': str, 'required': True}),
    ('password', {'type': str, 'required': True}),
    ('balance', {'type': float}),
    ('i_type', {'type': float, 'required': True, 'choices': ('Admin', 'Manager', 'Staff')}),
])

# Query #3: ad_filter_building_station [Screen #4 Admin Manage Building & Station]
# As mentioned above in the definition of `db_api`, endpoints beginning with 'ad_' will be restricted to admins.
# Response: {buildingName: str, tags: str, stationName: str, capacity: int, foodTruckNames: str}
ad_filter_building_station = db_api('ad_filter_building_station', ['GET'], [
    ('building_name', {'type': str, 'required': True}),
    ('building_tag', {'type': str, 'required': True}),
    ('station_name', {'type': str, 'required': True}),
    ('min_capacity', {'type': str, 'required': True}),
    ('max_capacity', {'type': str, 'required': True}),
], True)

# Query #4: ad_delete_building [Screen #4 Admin Manage Building & Station]
# Response: {}
ad_delete_building = db_api('ad_delete_building', ['POST'], [
    ('building_name', {'type': str, 'required': True})
])

# Query #5: ad_delete_station [Screen #4 Admin Manage Building & Station]
# Response: {}
ad_delete_station = db_api('ad_delete_station', ['POST'], [
    ('station_name', {'type': str, 'required': True})
])

# Query #6a: ad_add_building_tag [Screen #5 Admin Add Building Tag]
# Response: {}
ad_add_building_tag = db_api('ad_add_building_tag', ['POST'], [
    ('building_name', {'type': str, 'required': True}),
    ('tag', {'type': str, 'required': True})
])

# Query #6b: ad_remove_building_tag [Screen #5 Admin Remove Building Tag]
# Response: {}
ad_remove_building_tag = db_api('ad_remove_building_tag', ['POST'], [
    ('building_name', {'type': str, 'required': True}),
    ('tag', {'type': str, 'required': True})
])
# query #7 etc.

# Query #22b: mn_update_foodTruck_staff [Screen #13 Manager Update Food Truck]
# Response: {}
mn_update_foodTruck_staff = db_api('mn_update_foodTruck_staff', ['POST'], [
    ('food_truck_name', {'type': str, 'required': True}),
    ('staff_username', {'type': str, 'required': True})
], restrict_by_food_truck=True)

# Query #25: mn_summary_detail [Screen #15 Manager Summary Detail]
# Response: [{ date: str, customerName: str, totalPurchase: decimal, orderCount: int, foodNames: str }]
mn_summary_detail = db_api('mn_summary_detail', ['POST'], [
    ('manager_username', {'type': str, 'required': True}),
    ('food_truck_name', {'type': str, 'required': True})
], get_result=True, restrict_by_username=True)
# no need to do restrict_by_food_truck=True because the query already does a join with the manager's username

def close_connection() -> None:
    connection.close()
    print('MySQL connection closed')