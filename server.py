import random
import string
from flask import Flask
item_catalog_app = Flask(__name__)

def subpath_checker(subpath, rule):
    subpath = subpath.split("/")
    rule = rule.split("/")
    subpath_length = len(subpath)
    rule_length = len(rule)
    if subpath_length == rule_length:
        steps = 0
        rule_vars = [(i, subpath[i]) for i in range(rule_length) if rule[i] == "<pointer>"]
        try:
            rule_vars_indices = zip(*rule_vars)[0]
        except IndexError:
            rule_vars_indices = ()

        for i in range(subpath_length):
            if subpath[i] == rule[i]:
                steps += 1
            elif i in rule_vars_indices and subpath[i] != "":
                steps += 1

        if steps == rule_length:
            try:
                return zip(*rule_vars)[1]
            except IndexError:
                return True

    return False

def backend_actions_switcher(subpath, dict_list, **kwargs):
    for dict in dict_list:
        rule = dict["rule"]
        rule_vars = subpath_checker(subpath, rule)

        if subpath_checker(subpath, rule):

            def wrapper(*args):
                callback = dict["callback"]
                callback(*args, **kwargs)
            try:
                wrapper(*rule_vars)
            except TypeError:
                wrapper()

# Home page


@item_catalog_app.route('/')
@item_catalog_app.route('/catalog')
@item_catalog_app.route('/home')
def home():
    return "Home Page"


# Objects indexes

# -> Profiles index
@item_catalog_app.route('/profiles')
def profiles():
    return "Profiles Index"


# -> Categories index
@item_catalog_app.route('/categories')
def categories():
    return "Categories Index"


# -> Items index
@item_catalog_app.route('/items')
def items():
    return "Items Index"


# CRUD

# -> Edit
@item_catalog_app.route('/edit/<path:something>')
def edit(something):
    default = ["Page Not Found"]
    def editProfile(pointer, default):
        default[0] = "Edit profile, pointer=%s" % pointer

    def editCategory(pointer, default):
        default[0] = "Edit category, pointer=%s" % pointer

    def editItem(pointer, default):
        default[0] = "Edit item, pointer=%s" % pointer


    backend_actions_switcher(something,[
        {
            "rule": "profile/<pointer>",
            "callback": editProfile
        },
        {
            "rule": "category/<pointer>",
            "callback": editCategory
        },
        {
            "rule": "item/<pointer>",
            "callback": editItem
        }
    ], default=default)

    return default[0], 404


# -> Delete
@item_catalog_app.route('/delete/<path:something>')
def delete(something):
    default = ["Page Not Found"]
    def deleteProfile(pointer, default):
        default[0] = "Delete profile, pointer=%s" % pointer

    def deleteCategory(pointer, default):
        default[0] = "Delete category, pointer=%s" % pointer

    def deleteItem(pointer, default):
        default[0] = "Delete item, pointer=%s" % pointer


    backend_actions_switcher(something,[
        {
            "rule": "profile/<pointer>",
            "callback": deleteProfile
        },
        {
            "rule": "category/<pointer>",
            "callback": deleteCategory
        },
        {
            "rule": "item/<pointer>",
            "callback": deleteItem
        }
    ], default=default)

    return default[0], 404


# -> ADD
@item_catalog_app.route('/add/<path:something>')
def add(something):
    default = ["Page Not Found"]
    def addCategory(default):
        default[0] = "Add Category"

    def addItem(default):
        default[0] = "Add Item"


    backend_actions_switcher(something,[
        {
            "rule": "category",
            "callback": addCategory
        },
        {
            "rule": "item",
            "callback": addItem
        }
    ], default=default)

    return default[0], 404


# Profile page
@item_catalog_app.route('/<path:user_pointer>')
def profile(user_pointer):
    default = ["Page Not Found"]
    def showProfile(pointer, default):
        try:
            int(pointer)
        except ValueError:
            default[0] = "%s profile" % pointer

    def showProfileNested(pointer, default):
        default[0] = "%s profile" % pointer

    backend_actions_switcher(user_pointer,[
        {
            "rule": "<pointer>",
            "callback": showProfile
        },
        {
            "rule": "profiles/<pointer>",
            "callback": showProfileNested
        }
    ], default=default)
    return default[0], 404


# Category page
@item_catalog_app.route('/categories/<path:pointer>')
def category(pointer):
    return "Category %s" % pointer


# Item page
@item_catalog_app.route('/items/<path:pointer>')
def item(pointer):
    return "Item %s" % pointer


# Run server on port 8000


if __name__ == '__main__':

    item_catalog_app.secret_key = ''.join(
        (random.choice(string.ascii_letters + string.digits) for i in xrange(32))
    )

    item_catalog_app.debug = True
    item_catalog_app.run(host='0.0.0.0', port='8000')