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
import datetime
import os
import decimal
import flask.json

# Load environment variables from `.env`
with open('.env', 'r') as f:
    env_vars = dict(
        tuple(line.split('='))
        for line in f.readlines()
        if not line.startswith('#')
    )
os.environ.update(env_vars)

app = Flask(__name__)

cors = CORS(app)  # allow CORS on all routes
app.config['JSON_SORT_KEYS'] = False
api = Api(app)
# Fix decimal to string issue
class MyJSONEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            # Convert decimal instances to strings.
            return str(obj)
        return super(MyJSONEncoder, self).default(obj)
app.json_encoder = MyJSONEncoder
try:
    # Check MySQL Workbench > Database > Connect to Database > Test Connection for the host name, etc.
    connection = mysql.connector.connect(
        host=os.environ['host'],
        database=os.environ['database'],
        user=os.environ['user'],
        password=os.environ['password']
    )
    cursor = connection.cursor(buffered=True)
except mysql.connector.Error as error:
    print('Failed to connect to database: ' + repr(error))

class Auth(NamedTuple):
    username: str
    user_type: str

# Maps tokens to their username and user type
# Security warning: please ensure that tokens.txt contains no malicious Python code and is a normal dictionary
try:
    with open('tokens.txt', 'r') as f:
        tokens: Dict[str, Auth] = eval(f.readline())
except IOError as e:
    tokens = {}

def db_api(procedure: str, http_methods: List[str], inputs: List[Tuple[str, Dict[str, Any]]], get_result: int = 0,
           restrict_by_username: bool = False, restrict_by_food_truck: bool = False) -> Callable[[None], Response]:
    """
    Parameters:
    - procedure: name of the MySQL stored procedure which we will call.
        - The URL for the API endpoint is just '/' plus the name of the procedure (e.g., '/login').
        - Access to the API will be restricted to certain user types if `procedure` begins with 'ad_', 'mn_', or 'cus_'. In this case, either a 'token' cookie or a `token` request parameter is expected (or both, the `token` request parameter taking precedence).
        - A procedure named 'login' will create a token for the user and set a cookie for that, and also return that in the response.
    - http_methods: HTTP methods, such as ['GET'] (if the operation is just fetching data and doesn't modify the database), or ['POST']
    - inputs: request parameters, which will be passed into the stored procedure. These arguments should be in the same order as the SQL stored procedure, but can be called anything you like.
        - Example: [('username', {'type': str, 'required': True}), ('balance', {'type': int, 'default': 0})]
        - See reqparse (https://flask-restful.readthedocs.io/en/latest/reqparse.html) for documentation on other keys we can have in the dictionary, besides 'type', 'required', 'default', etc.
        - When contacting the API, the client can pass these parameters in as query parameters or form body parameters.
    - get_result: whether the procedure creates a table named `procedure + '_result'` (e.g., 'login_result'), and if it does, whether it returns one or many rows. If so, we'll make another SELECT query to get that table, after we call the procedure. Then, the response of the API endpoint is the result. Otherwise, the response an empty JSON object [].
        0: the procedure does not create a "_result" table. The API endpoint will return an empty list, [].
        1: the procedure is expected to create a "_result" table with one result
        2: the procedure is expected to create a list of results
    - restrict_by_username: restrict access to this API endpoint to people whose token corresponds to a user with a 'username', 'customerUsername', or 'managerUsername' field in inputs.
    - restrict_by_food_truck: restrict access to this API endpoint to people whose token corresponds to a user with a username 'managerUsername' in inputs that manages the food truck with the 'food_truck_name' in inputs.

    Returns a function that works as a Flask API endpoint.

    Be aware of the potential for SQL injection in the following line:
        cursor.execute(f"SELECT * FROM {procedure + '_result'};")
    Don't let users have access to this function for creating endpoints and pass in arbitrary `procedure` name.
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
            parser.add_argument('token', type=str)
        try:
            a = parser.parse_args()
        except Exception as e:
            print(request.__dict__)
            print(repr(e))
            return {'error': 'Bad request. Expected request arguments: ' + str(parser.args)}, 400
        print('Request: ' + repr(a))
        if restricted:
            if 'token' in a:
                token = a.token
                del a['token']  # don't send token to database stored procedures
            else:
                token = request.cookies.get('token')
        
        try:
            if procedure.startswith('cus_'):
                assert 'Customer' in tokens[token].user_type
            elif procedure.startswith('ad_'):
                assert 'Admin' in tokens[token].user_type
            elif procedure.startswith('mn_'):
                assert 'Manager' in tokens[token].user_type
            
            if restrict_by_username:
                assert tokens[token].username in (a.get('username', ''), a.get('customerUsername', ''), a.get('managerUsername', ''))
            if restrict_by_food_truck:
                cursor.execute("SELECT foodTruckName FROM FoodTruck WHERE managerUsername = '{}' ".format(a['managerUsername']))
                food_trucks = list(map(lambda x: x[0], cursor.fetchall()))
                print(food_trucks)
                assert not a.get('foodTruckName', '') or a['foodTruckName'] in food_trucks
        except AssertionError as e:
            print(repr(e))
            print('Your user type')
            return {'error': "Your user type can't access this page: " + repr(e)}, 403
        except KeyError as e:
            print(repr(e))
            print('Your token doesn''t match a logged in user:')
            return {'error': "Your token doesn't match a logged in user: " + repr(e)}, 403

        try:
            cursor.callproc(procedure, args=tuple(a.values()))
            if get_result:
                cursor.execute(f"SELECT * FROM {procedure + '_result'};")
                # The next two lines are from https://stackoverflow.com/a/17534004/5139284 by juandesant, CC-BY-SA 4.0
                fields = [col[0] for col in cursor.description]
                result = [dict(zip(fields, row)) for row in cursor.fetchall()]
                if len(result) == 1 and get_result == 1:
                    result = result[0]
                else:
                    result = list(filter(lambda x: x != {}, result))
                # Create and send a token upon successful login
                if procedure == 'login' and result:
                    # TODO: don't generate a new token if the user already exists (honestly not very important though)
                    new_token = token_hex(64)
                    tokens[new_token] = Auth(a['username'], result['userType'])
                    result['token'] = new_token
                    response = jsonify(result)
                    response.set_cookie('token', new_token)
                    with open('tokens.txt', 'w+') as f:
                        f.write(str(tokens))
                else:
                    response = jsonify(result)
                print(f'Result: {result}')
                return response
            else:
                return jsonify([])
            
        except ValueError as e:
            message = 'Incorrect parameter types'
            print(message + ' ' + repr(e))
            return {'error': message}, 400
        except mysql.connector.Error as e:
            print(repr(e))
            return {'error': repr(e)}, 400
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
], get_result=1)

# Query #2: register [Screen #2 Register]
# Response: []
register = db_api('register', ['POST'], [
    ('username', {'type': str, 'required': True}),
    ('email', {'type': str, 'required': True}),
    ('firstName', {'type': str, 'required': True}),
    ('lastName', {'type': str, 'required': True}),
    ('password', {'type': str, 'required': True}),
    ('balance', {'type': float}),
    ('type', {'type': str, 'choices': ('Admin', 'Manager', 'Staff')}),
])

# Query #3: ad_filter_building_station [Screen #4 Admin Manage Building & Station]
# As mentioned above in the definition of `db_api`, endpoints beginning with 'ad_' will be restricted to admins.
# The request will need an additional 'token' field which belongs to an admin that has logged in.
# Response: [{buildingName: string, tags: string, stationName: string, capacity: int, foodTruckNames: string}]
ad_filter_building_station = db_api('ad_filter_building_station', ['GET'], [
    ('buildingName', {'type': str}),
    ('buildingTag', {'type': str}),
    ('stationName', {'type': str}),
    ('minCapacity', {'type': str}),
    ('maxCapacity', {'type': str}),
], get_result=2)

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
], get_result=2)

# Query #8b: ad_view_building_tags [Screen #6 Admin Update Building]
# Response: 
ad_view_building_tags  = db_api('ad_view_building_tags', ['GET'], [
    ('buildingName', {'type': str, 'required': True})
], get_result=2)

# Query #9: ad_update_building [Screen #6 Admin Update Building]
# Response: []
ad_update_building = db_api('ad_update_building', ['POST'], [
    ('oldBuildingName', {'type': str, 'required': True}),
    ('newBuildingName', {'type': str, 'required': True}),
    ('description', {'type':str, 'required': True})
])

# Query #10: ad_get_available_building [Screen #7 Admin Create Station]
# Response: 
ad_get_available_building = db_api('ad_get_available_building', ['GET'], [], get_result=2)

# Query #11: ad_create_station [Screen #7 Admin Create Station]
# Response: 
ad_create_station = db_api('ad_create_station', ['POST'], [
    ('stationName', {'type': str, 'required': True}),
    ('buildingName', {'type': str, 'required': True}),
    ('capacity', {'type':int, 'required': True})
])

# Query #12: ad_view_station [Screen #8 Admin Update Station]
# Rresponse:
ad_view_station = db_api('ad_view_station', ['GET'], [
    ('stationName', {'type': str, 'required': True})
], get_result=2)

# Query #13: ad_update_station [Screen #8 Admin Update Station]
# Response:
ad_update_station = db_api('ad_update_station', ['POST'], [
    ('stationName', {'type': str, 'required': True}),
    ('capacity', {'type':int, 'required': True}),
    ('buildingName', {'type': str, 'required': True})
])

# Query #14: ad_filter_food [Screen #9 Admin Manage Food]
# Response: 
ad_filter_food = db_api('ad_filter_food', ['GET'], [
    ('foodName', {'type': str}),
    ('sortedBy', {'type': float, 'required': True, 'choices': ('name', 'menuCount', 'purchaseCount')}),
    ('sortDirection', {'type': float, 'default': 'ASC', 'choices': ('ASC', 'DESC')})
], get_result=2)

# Query #15: ad_delete_food [Screen #9 Admin Manage Food]
# Response:
ad_delete_food = db_api('ad_delete_food', ['POST'], [
    ('foodName', {'type': str, 'required': True})
])

# Query #16: ad_create_food [Screen #10 Admin Create Food]
# Response:
ad_create_food = db_api(' ad_create_food', ['POST'], [
    ('foodName', {'type': str, 'required': True})
])

# Query #17: mn_filter_foodTruck [Screen #11 Manager Manage Food Truck]
# Response: 
mn_filter_foodTruck = db_api('mn_filter_foodTruck', ['GET'], [
    ('managerUsername', {'type': str, 'required': True}),
    ('foodTruckName', {'type': str}),
    ('stationName', {'type': str}),
    ('minStaffCount', {'type': int}),
    ('maxStaffCount', {'type': int}),
    ('hasRemainingCapacity', {'type': bool, 'required': True})
], get_result=2, restrict_by_username=True, restrict_by_food_truck=True)

# Query #18: mn_delete_foodTruck [Screen #11 Manager Manage Food Truck]
# Response :
mn_delete_foodTruck = db_api('mn_delete_foodTruck', ['POST'], [
    ('foodTruckName', {'type': str, 'required': True})
 ], restrict_by_food_truck=True)

# Query #19a: mn_create_foodTruck_add_station [Screen #12 Manager Create Food Truck]
# Response:
mn_create_foodTruck_add_station = db_api('mn_create_foodTruck_add_station', ['POST'], [
    ('foodTruckName', {'type': str, 'required': True}),
    ('stationName', {'type': str, 'required': True}),
    ('managerUsername', {'type': str, 'required': True})
], restrict_by_food_truck=True, restrict_by_username=True)

# Query #19b: mn_create_foodTruck_add_staff [Screen #12 Manager Create Food Truck]
# Response:
mn_create_foodTruck_add_staff = db_api('mn_create_foodTruck_add_staff', ['POST'], [
    ('foodTruckName', {'type': str, 'required': True}),
    ('staffName', {'type': str, 'required': True})
], restrict_by_food_truck=True)

# Query #19c: mn_create_foodTruck_add_MenuItem [Screen #12 Manager Create Food Truck]
# Response:
mn_create_foodTruck_add_MenuItem = db_api('mn_create_foodTruck_add_MenuItem', ['POST'], [
    ('foodTruckName', {'type': str, 'required': True}),
    ('price', {'type': float, 'required': True}),
    ('foodName', {'type': str, 'required': True})
], restrict_by_food_truck=True)

# Query #20a: mn_view_foodTruck_available_staff [Screen #13 Manager Update Food Truck]
# Response:
mn_view_foodTruck_available_staff = db_api('mn_view_foodTruck_available_staff', ['GET'], [
    ('managerUsername', {'type': str, 'required': True}),
    ('foodTruckName', {'type': str, 'required': True})
], get_result=2, restrict_by_food_truck=True, restrict_by_username=True)

# Query #20b: mn_view_foodTruck_staff [Screen #13 Manager Update Food Truck]
# Response: 
mn_view_foodTruck_staff = db_api('mn_view_foodTruck_staff', ['GET'], [
    ('foodTruckName', {'type': str, 'required': True})
 ], get_result=2, restrict_by_food_truck=True)

# Query #21: mn_view_foodTruck_menu [Screen #13 Manager Update Food Truck]
# Response:
mn_view_foodTruck_menu = db_api('mn_view_foodTruck_menu', ['GET'], [
    ('foodTruckName', {'type': str, 'required': True})
 ], get_result=2, restrict_by_food_truck=True)

# Query #22a: mn_update_foodTruck_station [Screen #13 Manager Update Food Truck]
# Response:
mn_update_foodTruck_station = db_api('mn_update_foodTruck_station', ['POST'], [
    ('foodTruckName', {'type': str, 'required': True}),
    ('stationName', {'type': str, 'required': True})
], restrict_by_food_truck=True)

# Query #22b: mn_update_foodTruck_staff [Screen #13 Manager Update Food Truck]
# Response: {}
mn_update_foodTruck_staff = db_api('mn_update_foodTruck_staff', ['POST'], [
    ('foodTruckName', {'type': str, 'required': True}),
    ('staffUsername', {'type': str, 'required': True})
], restrict_by_food_truck=True)

# Query #22c: mn_update_foodTruck_MenuItem [Screen #13 Manager Update Food Truck]
# Response:
mn_update_foodTruck_MenuItem = db_api('mn_update_foodTruck_MenuItem', ['POST'], [
    ('foodTruckName', {'type': str, 'required': True}),
    ('price', {'type': float, 'required': True}),
    ('foodName', {'type': str, 'required': True})
], restrict_by_food_truck=True)

# Query #23: mn_get_station [Screen #14 Manager Food Truck Summary]
# Response:
mn_get_station = db_api('mn_get_station', ['GET'], [
    ('managerUsername', {'type': str, 'required': True}),
], get_result=2, restrict_by_username=False)

# Query #24: mn_filter_summary [Screen #14 Manager Food Truck Summary]
# Response:
mn_filter_summary = db_api('mn_filter_summary', ['GET'], [
    ('managerUsername', {'type': str, 'required': True}),
    ('foodTruckName', {'type': str}),
    ('stationName', {'type': str}),
    ('minDate', {'type': lambda d: datetime.strptime(d, '%Y%m%d').date()}),
    ('maxDate', {'type': lambda d: datetime.strptime(d, '%Y%m%d').date()}),
    ('sortedBy', {'type': str, 'choices': ('foodTruckName', 'totalOrder', 'totalRevenue', 'totalCustomer')}),
    ('sortDirection', {'type': str, 'default': 'ASC', 'choices': ('ASC', 'DESC')})
], get_result=2, restrict_by_username=False)
# no need to do restrict_by_food_truck=True because the query already does a join with the manager's username

# Query #25: mn_summary_detail [Screen #15 Manager Summary Detail]
# Response: [{ date: string, customerName: string, totalPurchase: decimal, orderCount: int, foodNames: string }]
mn_summary_detail = db_api('mn_summary_detail', ['GET'], [
    ('managerUsername', {'type': str, 'required': True}),
    ('foodTruckName', {'type': str, 'required': True})
], get_result=2, restrict_by_username=True)
# no need to do restrict_by_food_truck=True because the query already does a join with the manager's username

# Query #26: cus_filter_explore [Screen #16 Customer Explore]
# Response:
cus_filter_explore = db_api('cus_filter_explore', ['GET'], [
    ('buildingName', {'type': str}),
    ('stationName', {'type': str}),
    ('buildingTag', {'type': str}),
    ('foodTruckName', {'type': str}),
    ('foodName', {'type': str})
], get_result=2, restrict_by_food_truck=True)

# Query #27: cus_select_location [Screen #16 Customer Explore]
# Response:
cus_select_location = db_api('cus_select_location', ['POST'], [
    ('customerUsername', {'type': str, 'required': True}),
    ('stationName', {'type': str, 'required': True})
], restrict_by_username=True)

# Query #28: cus_current_information_basic [Screen #17 Customer Current Information]
# Response:
cus_current_information_basic = db_api('cus_current_information_basic', ['GET'], [
    ('customerUsername', {'type': str, 'required': True})
], get_result=2, restrict_by_username=True)

# Query #29: cus_current_information_foodTruck [Screen #17 Customer Current Information]
# Response:
cus_current_information_foodTruck = db_api('cus_current_information_foodTruck', ['GET'], [
    ('customerUsername', {'type': str, 'required': True})
], get_result=2, restrict_by_username=True)

# Query #30: cus_order [Screen #18 Customer Order]
# Response:
cus_order = db_api('cus_order', ['POST'], [
    ('date', {'type': lambda d: datetime.strptime(d, '%Y%m%d').date(), 'required': True}),
    ('customerUsername', {'type': str, 'required': True})
], restrict_by_username=True)

# Query #31: cus_add_item_to_order [Screen #18 Customer Order]
# Response:
cus_add_item_to_order = db_api('cus_add_item_to_order', ['POST'], [
    ('foodTruckName', {'type': str, 'required': True}),
    ('foodName', {'type': str, 'required': True}),
    ('purchaseQuantity', {'type': int, 'required': True}),
    ('orderID', {'type': int, 'required': True})
], restrict_by_food_truck=True)

# Query #32: cus_order_history [Screen #19 Customer Order History]
# Response:
cus_order_history = db_api('cus_order_history', ['GET'], [
    ('customerUsername', {'type': str, 'required': True})
], get_result=2, restrict_by_username=True)

def close_connection() -> None:
    connection.close()
    print('MySQL connection closed')