# Item Catalog Project
A project developed by Mohammed Madbouli.

## About
This application provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit, and delete their own items.

### Features
- CRUD support using Flask with SQLAlchemy.
- RESTful API endpoints.
- Implements OAuth using Google sign-in API.

### Project Structure
```
.
├── add_colors.py
├── catalog.db
├── client_secrets.json
├── colors_table
├── dbactions.py
├── dbactions.pyc
├── dbsession.py
├── dbsession.pyc
├── dbsetup.py
├── dbsetup.pyc
├── README.md
├── resources
│   ├── css
│   │   ├── 404_page_style.css
│   │   ├── normalize.min.css
│   │   └── styles.css
│   ├── image
│   ├── js
│   │   ├── file_uploader.js
│   │   ├── oauth_providers_initializer_for_api.js
│   │   ├── oauth_providers_initializer.js
│   │   └── user_name_update.js
│   └── static_image
│       ├── bg.jpg
│       └── favicon.png
├── server.py
└── templates
    ├── 404.html
    ├── add_category.html
    ├── add_item.html
    ├── api
    │   └── v1
    │       └── login.html
    ├── categories_index.html
    ├── category.html
    ├── delete.html
    ├── edit_category.html
    ├── edit_item.html
    ├── home.html
    ├── item.html
    ├── items_index.html
    ├── portable
    │   ├── item_card.html
    │   └── item_card_in_category.html
    ├── profile.html
    ├── profiles_index.html
    └── static
        ├── flash.html
        ├── head_config.html
        ├── header.html
        └── navigation.html
```

## Run the app

1. Download and install [Vagrant](https://www.vagrantup.com/downloads.html).

2. Download and install [VirtualBox](https://www.virtualbox.org/wiki/Downloads).

3. Open extracted `fullstack-nanodegree-vm.zip` in terminal

4. CD into `/vagrant`.

5. Then type:

   ```bash
   vagrant up
   ```

   This will cause Vagrant to download the Ubuntu operating system and install it. This may take quite a while depending on how fast your Internet connection is.

6. After the above command succeeds, connect to the newly created VM:

   ```bash
   vagrant ssh
   ```

7. Type `cd /vagrant` which is the project directory.

8. Install or upgrade Flask:
    ```bash
    sudo python -m pip install --upgrade flask
    ```
   
9. The project provided with a database called `catalog.db`

10. Set up the category colors table:
    ```bash
    python add_colors.py
    ```
    
11. Finally, run the project:
    ```bash
    python server.py
    ```
    
15. You can access the app from a Web Browser on `http://localhost:8000/`.

## RESTful API
To access the API you should login with google to get an access token for API,
<br> What you will just do is to go to:
`http://localhost:8000/get_access_token` and then copy the access token as a username

To preview this table, I recommend you to open `README.md` with a GitHub flavored MD reader
<table style="undefined;table-layout: fixed; width: 1144px">
<colgroup>
<col>
<col>
<col>
<col>
<col>
<col>
</colgroup>
  <tr>
    <th>Endpoint</th>
    <th>HTTP Methods</th>
    <th colspan="2">Query parameters</th>
    <th colspan="2">Form</th>
  </tr>
  <tr>
    <td>/colors</td>
    <td>GET</td>
    <td colspan="2"></td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>/users</td>
    <td>GET</td>
    <td>id (optional)</td>
    <td>me / &lt;int: user_id&gt;</td>
    <td colspan="2" rowspan="4"></td>
  </tr>
  <tr>
    <td rowspan="3">/categories</td>
    <td rowspan="3">GET</td>
    <td>for (optional)</td>
    <td>me / all / &lt;int: user_id&gt;</td>
  </tr>
  <tr>
    <td>id (optional)</td>
    <td>&lt;int: category_id&gt;</td>
  </tr>
  <tr>
    <td>view (optional)</td>
    <td>full</td>
  </tr>
  <tr>
    <td rowspan="5">/category</td>
    <td rowspan="2">POST</td>
    <td colspan="2" rowspan="2"></td>
    <td>name (required)</td>
    <td>&lt;str: category_name&gt;</td>
  </tr>
  <tr>
    <td>colors (required)</td>
    <td>&lt;int: colors_id&gt;</td>
  </tr>
  <tr>
    <td rowspan="2">PUT</td>
    <td rowspan="2">id (required)</td>
    <td rowspan="2">&lt;int: category_id&gt;</td>
    <td>name (required)</td>
    <td>&lt;str: category_name&gt;</td>
  </tr>
  <tr>
    <td>colors (required)</td>
    <td>&lt;int: colors_id&gt;</td>
  </tr>
  <tr>
    <td>DELETE</td>
    <td>id (required)</td>
    <td>&lt;int: category_id&gt;</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td rowspan="3">/items</td>
    <td rowspan="3">GET</td>
    <td>for (optional)</td>
    <td>me / all / &lt;int: user_id&gt;</td>
    <td colspan="2" rowspan="3"></td>
  </tr>
  <tr>
    <td>id (optional)</td>
    <td>&lt;int: item_id&gt;</td>
  </tr>
  <tr>
    <td>view (optional)</td>
    <td>full</td>
  </tr>
  <tr>
    <td rowspan="9">/item</td>
    <td rowspan="4">POST</td>
    <td colspan="2" rowspan="4"></td>
    <td>category (required)</td>
    <td>&lt;int: category_id&gt;</td>
  </tr>
  <tr>
    <td>name (required)</td>
    <td>&lt;str: item_name&gt;</td>
  </tr>
  <tr>
    <td>description (required)</td>
    <td>&lt;str: item_description&gt;</td>
  </tr>
  <tr>
    <td>image (optional)</td>
    <td>&lt;url: item_image&gt;</td>
  </tr>
  <tr>
    <td rowspan="4">PUT</td>
    <td rowspan="4">id (required)</td>
    <td rowspan="4">&lt;int: item_id&gt;</td>
    <td>category (required)</td>
    <td>&lt;int: category_id&gt;</td>
  </tr>
  <tr>
    <td>name (required)</td>
    <td>&lt;str: item_name&gt;</td>
  </tr>
  <tr>
    <td>description (required)</td>
    <td>&lt;str: item_description&gt;</td>
  </tr>
  <tr>
    <td>image (optional)</td>
    <td>&lt;url: item_image&gt;</td>
  </tr>
  <tr>
    <td>DELETE</td>
    <td>id (required)</td>
    <td>&lt;int: item_id&gt;</td>
    <td></td>
    <td></td>
  </tr>
</table>


## Debugging
In case the app doesn't run, or there's something wrong with forms, make sure to confirm the following points:
- You have run `python add_colors.py` before running the application. This is an essential step.
- The latest version of Flask is installed.

## Known Issue
This app might show an empty username if you sign in with a custom-domain-based Google account (Corporate accounts). For instance, if you use a Google account `johndoe@company.com`, this app might show an empty username.