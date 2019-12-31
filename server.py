import random
import string
import httplib2
import json
import requests
import os
from werkzeug.utils import secure_filename
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    Markup,
    send_from_directory,
    make_response,
    g,
    jsonify,
    session as login_session,
)
from flask_httpauth import HTTPBasicAuth
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from dbsetup import Base, User, Category, Item, Colors
import dbactions as act
import dbsession

item_catalog_app = Flask(__name__, template_folder="templates")

item_catalog_session = dbsession.session(Base, "sqlite:///catalog.db")

__client_id__ = json.load(open("client_secrets.json", "r"))["web"]["client_id"]

token_auth = HTTPBasicAuth()

# Allowed file checker


def allowed_file(filename, allowed_extensions):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )


# Auto images files names generator


def random_filename(extension):
    return secure_filename(
        "%s_%s.%s"
        % (
            "".join(random.choice(string.digits) for i in xrange(16)),
            "".join(random.choice(string.letters) for i in xrange(8)),
            extension,
        )
    )


@item_catalog_session.fetch
def get_user_id(session, email):
    """ fetch user id by passing his email """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id

    except BaseException:
        return None


@item_catalog_app.before_request
def global_variables():
    """ global variables for templates environment """
    item_catalog_app.jinja_env.globals["USER"] = act.user(
        pointer=login_session.get("user_id")
    )
    item_catalog_app.jinja_env.globals["ALL_CATEGORIES"] = act.all_categories()
    g.USER = act.user(pointer=login_session.get("user_id", ""))


def login_required(f):
    """ decorator for checking if user is logged in
    and redirecting it to a login page if not """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.USER is None:
            return redirect(
                url_for("home", force_login=True, next=request.url)
            )

        return f(*args, **kwargs)

    return decorated_function


def login_required_for_token(f):
    """ decorator for checking if user is logged in
    to get an access_token for api server
    and redirecting it to a login page if not """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.USER is None:
            return redirect(url_for("api_v1_login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@item_catalog_app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@item_catalog_app.route("/404")
def notFound():
    return render_template("404.html"), 404


# Login and Logout pages
@item_catalog_app.route("/login", methods=["GET", "POST"])
def login():
    """ login endpoint: it can be accessed only
    from a main login dialog on header or APIs login pages.
    That's mean there's no main login page"""
    if request.method == "GET" and request.query_string == "from=login_dialog":
        state = "".join(
            random.choice(string.ascii_uppercase + string.digits)
            for x in xrange(32)
        )
        login_session["state"] = state
        return state

    if request.method == "POST":
        # Validate state token
        if request.args.get("state") != login_session["state"]:
            response = make_response(
                json.dumps("Invalid state parameter."), 401
            )
            response.headers["Content-Type"] = "application/json"
            return response
        # Obtain authorization code
        code = request.data

        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets(
                "client_secrets.json", scope=""
            )
            oauth_flow.redirect_uri = "postmessage"
            credentials = oauth_flow.step2_exchange(code)

        except FlowExchangeError:
            response = make_response(
                json.dumps("Failed to upgrade the authorization code."), 401
            )
            response.headers["Content-Type"] = "application/json"
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = (
            "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s"
            % access_token
        )
        h = httplib2.Http()
        result = json.loads(h.request(url, "GET")[1])
        # If there was an error in the access token info, abort.
        if result.get("error") is not None:
            response = make_response(json.dumps(result.get("error")), 500)
            response.headers["Content-Type"] = "application/json"
            return response

        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token["sub"]
        if result["user_id"] != gplus_id:
            response = make_response(
                json.dumps("Token's user ID doesn't match given user ID."), 401
            )
            response.headers["Content-Type"] = "application/json"
            return response

        # Verify that the access token is valid for this app.
        if result["issued_to"] != __client_id__:
            response = make_response(
                json.dumps("Token's client ID does not match app's."), 401
            )
            response.headers["Content-Type"] = "application/json"
            return response

        stored_access_token = login_session.get("access_token")
        stored_gplus_id = login_session.get("gplus_id")
        if stored_access_token is not None and gplus_id == stored_gplus_id:
            flash("You're already logged in.")
            return make_response(
                json.dumps({"id": login_session.get("user_id")}), 200
            )

        # Store the access token in the session for later use.
        login_session["access_token"] = credentials.access_token
        login_session["gplus_id"] = gplus_id

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {"access_token": credentials.access_token, "alt": "json"}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        login_session["provider"] = "google"
        login_session["username"] = data["name"]
        login_session["picture"] = data["picture"]
        login_session["email"] = data["email"]

        user_id = get_user_id(email=login_session["email"])
        if not user_id:
            user_id = act.add_user(
                username="".join(
                    random.choice(string.ascii_lowercase) for x in xrange(16)
                ),
                name=login_session["username"],
                email=login_session["email"],
                image=login_session["picture"],
            )

        login_session["user_id"] = user_id
        flash("You are now logged in as %s" % login_session["username"])
        return make_response(
            json.dumps({"id": login_session.get("user_id")}), 200
        )

    return redirect(url_for("notFound"))


@item_catalog_app.route("/logout")
def logout():
    """ logout endpoint: it cleans up the login session
    and revokes the access tokens of oauth providers"""

    access_token = login_session.get("access_token")
    if access_token is None:
        return redirect(url_for("home"))

    url = (
        "https://accounts.google.com/o/oauth2/revoke?token=%s"
        % login_session["access_token"]
    )
    h = httplib2.Http()
    result = h.request(url, "GET")[0]

    if result["status"] == "200":
        login_session.clear()
        del g.USER
        flash("You have been logged out successfully")
        return redirect(url_for("home"))

    else:
        response = make_response(
            json.dumps("Failed to revoke token for given user.", 400)
        )
        response.headers["Content-Type"] = "application/json"
        return response


# Home page


@item_catalog_app.route("/")
@item_catalog_app.route("/catalog")
@item_catalog_app.route("/home")
def home():
    """ home endpoint: it's also used to force login """
    if "force_login" in request.args:
        return render_template(
            "home.html", force_login=True, items=act.latest_items()[:6]
        )
    return render_template("home.html", items=act.latest_items()[:6])


# -> Profiles index
@item_catalog_app.route("/profiles")
def profiles():
    return render_template("profiles_index.html", users=act.all_users())


# -> Categories index
@item_catalog_app.route("/categories")
def categories():
    return render_template(
        "categories_index.html", categories=act.all_categories()
    )


# -> Items index
@item_catalog_app.route("/items")
def items():
    return render_template("items_index.html", items=act.all_items())


# -> Edit
@item_catalog_app.route("/edit/profile/<pointer>")
@login_required
def editProfile(pointer):
    return "Edit profile, pointer=%s" % pointer


@item_catalog_app.route(
    "/edit/category/<int:category_id>", methods=["GET", "POST"]
)
@login_required
def editCategory(category_id):
    try:
        # Fetch the data from database
        category = act.category(id=category_id)

        # Check the authority of the logged-in user
        if category.user_id == g.USER.id:

            if request.method == "GET":
                return render_template(
                    "edit_category.html",
                    category=category,
                    colors=act.all_colors(),
                )

            elif request.method == "POST":

                # Make edit action on database and check if passed correctly
                if act.edit_category(
                    category=category,
                    name=request.form.get("name", ""),
                    colors_id=request.form.get("colors", ""),
                ):

                    flash(
                        Markup(
                            "The category has been edited successfully. "
                            'Go to your <a href="/me">profile</a>.'
                        )
                    )

                else:

                    flash(Markup("An error occurred editing your category."))

                return redirect(request.args.get("next", ""))

    except BaseException:
        pass

    return redirect(url_for("notFound"))


@item_catalog_app.route("/edit/item/<int:item_id>", methods=["GET", "POST"])
@login_required
def editItem(item_id):
    try:
        # Fetch the data from database
        item = act.item(id=item_id)

        # Check the authority of the logged-in user
        if item.user_id == g.USER.id:
            if request.method == "GET":
                return render_template(
                    "edit_item.html",
                    item=item,
                    your_categories=act.categories(user_id=g.USER.id),
                    others_categories=act.all_categories(),
                )

            elif request.method == "POST":
                allowed_image_extension = {"png", "jpg", "jpeg", "gif"}
                item_image = request.files["image"]
                item_image_name = [""]

                # Check if image is in a correct formats and extensions
                if item_image and allowed_file(
                    item_image.filename, allowed_image_extension
                ):

                    # Check if image is already exist
                    # and remove it to replace it with the new one
                    if item.image:
                        try:
                            os.remove(item.image[1:])
                        except BaseException:
                            pass

                    item_image_extension = item_image.filename.split(".")[-1]
                    item_image_name[0] = random_filename(item_image_extension)

                    image_exist = True

                    # Generate a random name for image safely
                    while image_exist:
                        try:
                            image = open(
                                os.path.join(
                                    "resources/image", item_image_name[0]
                                ),
                                "r",
                            )
                            image.close()
                            item_image_name[0] = random_filename(
                                item_image_extension
                            )
                        except BaseException:
                            image_exist = False

                    # Save the new image
                    item_image.save(
                        os.path.join("resources/image", item_image_name[0])
                    )

                # Make edit action on database and check if passed correctly
                if act.edit_item(
                    item=item,
                    name=request.form.get("name", ""),
                    description=request.form.get("description", ""),
                    image=(
                        url_for(
                            "resources",
                            filename="image/%s" % item_image_name[0],
                        )
                        if act.not_empty(item_image_name[0])
                        else ""
                    ),
                    category_id=request.form.get("category", ""),
                ):

                    flash(
                        Markup(
                            """The item has been edited successfully. \
                            Go to your <a href="/me">profile</a>."""
                        )
                    )

                else:

                    flash(Markup("An error occurred editing your item."))

                return redirect(request.args.get("next", ""))

    except BaseException:
        pass

    return redirect(url_for("notFound"))


# -> Delete
@item_catalog_app.route(
    "/delete/category/<int:category_id>", methods=["GET", "POST"]
)
@login_required
def deleteCategory(category_id):
    try:
        # Fetch the data from database
        category = act.category(id=category_id)

        # Check the authority of the logged-in user
        if category.user_id == g.USER.id:
            if request.method == "GET":
                TYPE = "category"
                return render_template(
                    "delete.html", TYPE=TYPE, object=category
                )

            elif request.method == "POST":
                # Make delete action on database and check if passed correctly
                if act.delete_category(category=category) and act.delete_items(
                    items=act.items(For="category", pointer=category_id)
                ):

                    flash(
                        Markup(
                            "The category and its items "
                            "have been deleted successfully. "
                            'Go to your <a href="/me">profile</a>.'
                        )
                    )

                else:

                    flash(Markup("An error occurred during deletion."))

                # Check if the next redirect
                # is not related to the deleted category
                # and redirect to the user profile
                if (
                    request.args.get("next", "")
                    == url_for("category", category_id=category_id)
                    or request.args.get("next", "")
                    == url_for("editCategory", category_id=category_id)
                    or request.args.get("next", "")
                    == url_for("deleteCategory", category_id=category_id)
                ):
                    return redirect(url_for("me"))

                return redirect(request.args.get("next", ""))

    except BaseException:
        pass

    return redirect(url_for("notFound"))


@item_catalog_app.route("/delete/item/<int:item_id>", methods=["GET", "POST"])
@login_required
def deleteItem(item_id):
    try:
        # Fetch the data from database
        item = act.item(id=item_id)

        # Check the authority of the logged-in user
        if item.user_id == g.USER.id:
            if request.method == "GET":
                TYPE = "item"
                return render_template("delete.html", TYPE=TYPE, object=item)

            elif request.method == "POST":

                # Check if image is already exist
                # and remove it
                if item.image:
                    try:
                        os.remove(item.image[1:])
                    except BaseException:
                        pass

                # Make delete action on database and check if passed correctly
                if act.delete_item(item=item):

                    flash(
                        Markup(
                            "The item has been deleted successfully. "
                            'Go to your <a href="/me">profile</a>.'
                        )
                    )

                else:

                    flash(Markup("An error occurred during deletion."))

                # Check if the next redirect is not related to the deleted item
                # and redirect to the user profile
                if (
                    request.args.get("next", "")
                    == url_for("item", item_id=item_id)
                    or request.args.get("next", "")
                    == url_for("editItem", item_id=item_id)
                    or request.args.get("next", "")
                    == url_for("deleteItem", item_id=item_id)
                ):
                    return redirect(url_for("me"))

                return redirect(request.args.get("next", ""))

    except BaseException:
        pass

    return redirect(url_for("notFound"))


# -> ADD
@item_catalog_app.route("/add/category", methods=["GET", "POST"])
@login_required
def addCategory():
    if request.method == "GET":
        return render_template("add_category.html", colors=act.all_colors())

    elif request.method == "POST":
        # Make add action on database and check if passed correctly
        if act.add_category(
            user_id=g.USER.id,
            name=request.form.get("name", ""),
            colors_id=request.form.get("colors", ""),
        ):

            flash(
                Markup(
                    "The category has been added successfully. "
                    'Go to your <a href="/me">profile</a>.'
                )
            )

        else:

            flash(Markup("An error occurred adding the category."))

        return redirect(request.args.get("next", ""))


@item_catalog_app.route("/add/item", methods=["GET", "POST"])
@login_required
def addItem():
    if request.method == "GET":
        return render_template(
            "add_item.html",
            your_categories=act.categories(user_id=g.USER.id),
            others_categories=act.all_categories(),
        )

    elif request.method == "POST":
        allowed_image_extension = {"png", "jpg", "jpeg", "gif"}
        item_image = request.files["image"]
        item_image_name = [""]

        # Check if image is in a correct formats and extensions
        if item_image and allowed_file(
            item_image.filename, allowed_image_extension
        ):
            item_image_extension = item_image.filename.split(".")[-1]
            item_image_name[0] = random_filename(item_image_extension)

            image_exist = True

            # Generate a random name for image safely
            while image_exist:
                try:
                    image = open(
                        os.path.join("resources/image", item_image_name), "r"
                    )
                    image.close()
                    item_image_name[0] = random_filename(item_image_extension)
                except BaseException:
                    image_exist = False

            # Save the new image
            item_image.save(
                os.path.join("resources/image", item_image_name[0])
            )

        # Make add action on database and check if passed correctly
        if act.add_item(
            name=request.form.get("name", ""),
            description=request.form.get("description", ""),
            image=(
                url_for("resources", filename="image/%s" % item_image_name[0])
                if act.not_empty(item_image_name[0])
                else ""
            ),
            category_id=request.form.get("category", ""),
            user_id=g.USER.id,
        ):

            flash(
                Markup(
                    "The item has been added successfully. "
                    'Go to your <a href="/me">profile</a>.'
                )
            )

        else:

            flash(Markup("An error occurred adding the item."))

        return redirect(request.args.get("next", ""))


# Profile page
@item_catalog_app.route("/me")
def me():
    """ endpoint for logged-in user profile """
    if g.USER:
        return redirect(url_for("profile", username=g.USER.username))
    return redirect(url_for("home"))


@item_catalog_app.route("/<username>")
def profile(username):
    try:
        try:
            # Check that it's not a user id
            # to make sure it's only allowed
            # to pass usernames after the root directory
            int(username)
            return redirect(url_for("notFound"))

        except BaseException:
            # Fetch the data from database
            user = act.user(pointer=username)
            return render_template(
                "profile.html",
                categories=act.categories(user_id=user.id),
                items=act.items(For="user", pointer=user.id),
                user=user,
            )

    except BaseException:
        return redirect(url_for("notFound"))


@item_catalog_app.route("/profiles/<pointer>")
def profileNested(pointer):
    try:
        # Fetch the data from database
        user = act.user(pointer=pointer)
        return render_template(
            "profile.html",
            categories=act.categories(user_id=user.id),
            items=act.items(For="user", pointer=user.id),
            user=user,
        )
    except BaseException:
        return redirect(url_for("notFound"))


# Category page
@item_catalog_app.route("/categories/<int:category_id>")
def category(category_id):
    try:
        # Fetch the data from database
        category = act.category(id=category_id)
        return render_template(
            "category.html",
            category=category,
            items=act.items(For="category", pointer=category_id),
        )
    except BaseException:
        return redirect(url_for("notFound"))


# Item page
@item_catalog_app.route("/items/<int:item_id>")
def item(item_id):
    try:
        # Fetch the data from database
        item = act.item(id=item_id)
        return render_template("item.html", item=item)

    except BaseException:
        return redirect(url_for("notFound"))


# Resources endpoint
@item_catalog_app.route("/resources/<path:filename>")
def resources(filename):
    """ endpoint for usable resources """
    return send_from_directory("resources", filename)


# API v1 endpoints
@item_catalog_app.route("/api/v1/login")
def api_v1_login():
    return render_template("api/v1/login.html")


@item_catalog_app.route("/api/v1/get_access_token")
@login_required_for_token
def api_v1_get_access_token():
    access_token = g.USER.generate_auth_token()
    return jsonify({"access_token": access_token.decode("ascii")})


@token_auth.verify_password
def verify_access_token(access_token, password):
    user_id = User.verify_auth_token(access_token)
    if user_id:
        user = act.user(pointer=user_id)
        g.USER = user
        return True


@item_catalog_app.route("/api/v1/colors")
@token_auth.login_required
def api_v1_colors():
    return jsonify(
        category_colors=[color.serialize for color in act.all_colors()]
    )


@item_catalog_app.route("/api/v1/users")
@token_auth.login_required
def api_v1_users():
    user_id = request.args.get("id")
    if user_id:

        if user_id == "me":
            return jsonify(act.user(pointer=g.USER.id).serialize)

        try:
            user = act.user(pointer=user_id)
            return jsonify(user.serialize)

        except BaseException:
            return jsonify(error="NOT FOUND"), 404

    else:
        return jsonify(all_users=[user.serialize for user in act.all_users()])


@item_catalog_app.route("/api/v1/categories")
@token_auth.login_required
def api_v1_categories():
    category_id = request.args.get("id", "")
    view_type = request.args.get("view", "")
    if view_type == "full":
        view_properity = "serialize"
    else:
        view_properity = "mini_serialize"

    if category_id:
        try:
            category = act.category(id=category_id)
            return jsonify(getattr(category, view_properity))

        except BaseException:
            return jsonify(error="NOT FOUND"), 404
    else:
        category_owner = request.args.get("for", "all")
        if category_owner == "all":
            return jsonify(
                all_categories=[
                    getattr(category, view_properity)
                    for category in act.all_categories()
                ]
            )

        elif category_owner == "me":
            return jsonify(
                my_categories=[
                    getattr(category, view_properity)
                    for category in act.categories(user_id=g.USER.id)
                ]
            )

        else:
            try:
                categories = act.categories(user_id=category_owner)
                return jsonify(
                    user_categories=[
                        getattr(category, view_properity)
                        for category in categories
                    ]
                )

            except BaseException:
                return jsonify(error="NOT FOUND"), 404


@item_catalog_app.route("/api/v1/category", methods=["POST", "PUT", "DELETE"])
@token_auth.login_required
def api_v1_category():
    category_id = request.args.get("id", "")
    colors_ids = [str(color.id) for color in act.all_colors()]
    if request.method == "POST":
        colors_id = request.form.get("colors")
        if colors_id not in colors_ids:
            return jsonify(error="An error occurred adding the category"), 404

        if act.add_category(
            user_id=g.USER.id,
            name=request.form.get("name", ""),
            colors_id=colors_id,
        ):

            return jsonify("The category has been added successfully")

        else:

            return jsonify(error="An error occurred adding the category"), 404

    else:
        try:
            category = act.category(id=category_id)
            if request.method == "PUT":
                colors_id = request.form.get("colors")
                if colors_id not in colors_ids:
                    return (
                        jsonify(error="An error occurred adding the category"),
                        404,
                    )

                if category.user_id == g.USER.id:

                    if act.edit_category(
                        category=category,
                        name=request.form.get("name", ""),
                        colors_id=colors_id,
                    ):

                        return jsonify(
                            "The category has been edited successfully"
                        )

                    else:

                        return (
                            jsonify(
                                error="An error occurred editing the category"
                            ),
                            404,
                        )

                else:

                    return (
                        jsonify(
                            error="You are not allowed to modify this category"
                        ),
                        404,
                    )

            elif request.method == "DELETE":

                if category.user_id == g.USER.id:

                    if act.delete_category(
                        category=category
                    ) and act.delete_items(
                        items=act.items(For="category", pointer=category_id)
                    ):

                        return jsonify(
                            "The category and its items "
                            "have been deleted successfully"
                        )

                    else:

                        return (
                            jsonify(
                                error="An error occurred deleting the category"
                            ),
                            404,
                        )

                else:

                    return (
                        jsonify(
                            error="You are not allowed to delete this category"
                        ),
                        404,
                    )

        except BaseException:
            return jsonify(error="NOT FOUND"), 404


@item_catalog_app.route("/api/v1/items")
@token_auth.login_required
def api_v1_items():
    item_id = request.args.get("id", "")
    view_type = request.args.get("view", "")
    if view_type == "full":
        view_properity = "serialize"
    else:
        view_properity = "mini_serialize"

    if item_id:
        try:
            item = act.item(id=item_id)
            return jsonify(getattr(item, view_properity))

        except BaseException:
            return jsonify(error="NOT FOUND"), 404
    else:
        item_owner = request.args.get("for", "all")
        if item_owner == "all":
            return jsonify(
                all_items=[
                    getattr(item, view_properity) for item in act.all_items()
                ]
            )

        elif item_owner == "me":
            return jsonify(
                my_items=[
                    getattr(item, view_properity)
                    for item in act.items(For="user", pointer=g.USER.id)
                ]
            )

        else:
            try:
                items = act.items(For="user", pointer=item_owner)
                return jsonify(
                    user_items=[
                        getattr(item, view_properity) for item in items
                    ]
                )

            except BaseException:
                return jsonify(error="NOT FOUND"), 404


@item_catalog_app.route("/api/v1/item", methods=["POST", "PUT", "DELETE"])
@token_auth.login_required
def api_v1_item():
    item_id = request.args.get("id", "")
    category_id = request.form.get("category", "")

    if request.method == "POST":
        if not act.category(id=category_id):
            return jsonify(error="Category ID is incorrect"), 404

        if act.add_item(
            user_id=g.USER.id,
            category_id=category_id,
            name=request.form.get("name", ""),
            description=request.form.get("description", ""),
            image=request.form.get("image", ""),
        ):

            return jsonify("The item has been added successfully")

        else:

            return jsonify(error="An error occurred adding the item"), 404

    else:
        try:
            item = act.item(id=item_id)
            if request.method == "PUT":
                if not act.category(id=category_id):
                    return jsonify(error="Category ID is incorrect"), 404

                if item.user_id == g.USER.id:

                    if item.image:
                        try:
                            os.remove(item.image[1:])
                        except BaseException:
                            pass

                    if act.edit_item(
                        item=item,
                        category_id=category_id,
                        name=request.form.get("name", ""),
                        description=request.form.get("description", ""),
                        image=request.form.get("image", ""),
                    ):

                        return jsonify("The item has been edited successfully")

                    else:

                        return (
                            jsonify(
                                error="An error occurred editing the item"
                            ),
                            404,
                        )

                else:

                    return (
                        jsonify(
                            error="You are not allowed to modify this item"
                        ),
                        404,
                    )

            elif request.method == "DELETE":

                if item.user_id == g.USER.id:

                    if item.image:
                        try:
                            os.remove(item.image[1:])
                        except BaseException:
                            pass

                    if act.delete_item(item=item):

                        return jsonify(
                            "The item has been deleted successfully"
                        )

                    else:

                        return (
                            jsonify(
                                error="An error occurred deleting the item"
                            ),
                            404,
                        )

                else:

                    return (
                        jsonify(
                            error="You are not allowed to delete this item"
                        ),
                        404,
                    )

        except BaseException:
            return jsonify(error="NOT FOUND"), 404


# Run server on port 8000


if __name__ == "__main__":
    item_catalog_app.secret_key = "".join(
        (
            random.choice(string.ascii_letters + string.digits)
            for i in xrange(32)
        )
    )

    item_catalog_app.debug = True
    item_catalog_app.run(host="0.0.0.0", port="8000")
