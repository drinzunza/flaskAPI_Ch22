import bson
from flask import Flask, abort, render_template, request
from pymongo.uri_parser import parse_host
from mock_data import mock_data
from flask_cors import CORS # pip intall flask-cors
from config import db, json_parse
from bson import ObjectId

app = Flask(__name__)
CORS(app) # allow anyone to call the server (**DANGER**)



coupon_codes = [ 
    {
        "code": "qwerty",
        "discount": 10
    }
]


me = {
    "name": "Sergio",
    "last": "Inzunza",
    "age": 35,
    "hobbies": [],
    "address": {
        "street": "Evergreen",
        "city": "Springfield"
    }
}


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/test")
def simple_test():
    return "Hello there!"


@app.route("/about")
def about():
    # return full name
    return me["name"] + " " + me["last"]






#################################################
########## API Methods
#################################################

@app.route("/api/catalog", methods=["get"])
def get_catalog():
    # returns the catalog as JSON string
    cursor = db.products.find({}) # find with no filter = get all data in the collection
    catalog = []
    for prod in cursor:
        catalog.append(prod)

    # inv homework: Python list comprehension

    print( len(catalog), "Records obtained from db" )

    return json_parse(catalog) 


@app.route("/api/catalog", methods=["post"])
def save_product():
    # get request payload (body)
    product = request.get_json()

    ## validate that title exist in the dict, if not abort(400) 
    if not 'title' in product or len(product["title"]) < 5:
        return abort(400, "Title is required, and should contains at least 5 chars")  # 400 = bad request

    ## validate that price exist and is greater than 0
    if not 'price' in product:
        return abort(400, "Price is required")

    if not isinstance(product["price"], float) and not isinstance(product["price"], int):
        return abort(400, "Price should a valid number")

    if product['price'] <= 0:
        return abort(400,"Price should be greater than 0")


    # save the product
    db.products.insert_one(product)

    # return the saved object
    return json_parse(product)


@app.route("/api/categories")
def get_categories():
    # return the list (string) of UNIQUE categories
    categories = []    
    cursor = db.products.find({})    
    for prod in cursor:
        if not prod["category"] in categories:
            categories.append(prod["category"])

    # logic 
    return json_parse(categories)
        



@app.route("/api/product/<id>")
def get_product(id):    
    result = db.products.find_one({"_id": ObjectId(id)})
    if not result:
        return abort(404) # 404 = Not Found
    
    return json_parse(result)        



@app.route("/api/catalog/<category>")
def get_by_category(category):    
    # mongo to search case insensitive we use Regular Expressions
    cursor = db.products.find({"category": category})
    list = []
    for prod in cursor:
        list.append(prod)
    
    return json_parse(list)



@app.route("/api/cheapest")
def get_cheapest():
    cursor = db.products.find({})
    pivot = cursor[0]
    for prod in cursor:        
        if prod["price"] < pivot["price"]:
            pivot = prod

    return json_parse(pivot)


#################################
########     Orders     #########
#################################


@app.route("/api/order", methods=["POST"])
def save_order():
    # get the order object from the request
    order = request.get_json()
    if order is None:
        return abort(400, "Nothing to save")

    # validations
    

    # save the object in the database (orders collection)
    db.orders.insert_one(order)


    # return the stored object
    return json_parse(order)


#################################
########  Coupon Codes  #########
#################################

# POST to /api/couponCodes
@app.route("/api/couponCodes", methods=["POST"])
def save_coupon():
    coupon = request.get_json()

    # save
    db.couponCodes.insert_one(coupon)
    return json_parse(coupon)


# GET to /api/couponCodes
@app.route("/api/couponCodes", methods=["GET"])
def get_coupons():
    # read the coupons from db into a cursor
    cursor = db.couponCodes.find({})
    # parse the cursor into a list
    all_coupons = []
    for cp in cursor:
        all_coupons.append(cp)
    
    return json_parse(all_coupons)


# get coupon by its code or 404 if not found
@app.route("/api/couponCodes/<code>")
def get_coupon_by_code(code):    
    coupon = db.couponCodes.find_one({"code": code})
    if coupon is None:
        return abort(404, "Invalid coupon code")
    
    return json_parse(coupon)



@app.route("/test/onetime/filldb")
def fill_db():    
    # iterate the mock_data list
    for prod in mock_data:
        # save every object to db.products  
        prod.pop("_id") # remove the _id from the dict/product
        db.products.insert_one(prod)

    return "Done!"


# start the server
# debug true will restart the server automatically
app.run(debug=True)




