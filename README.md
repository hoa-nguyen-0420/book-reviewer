# Project 1

Web Programming with Python and JavaScript

https://youtu.be/P5Czc-QexeQ

* Fix Werkzeug module error:
    -install Werkzeug version 1.0.0: pip install werkzeug==1.0.0
    -install -U cachelib pip install
    -locate to sesion.py file by directory: venv\Lib\site-packages\flask_session
    -Replace : "from werkzeug.contrib.cache import FileSystemCache" by "from cachelib.file import FileSystemCache"

*import.py:
    Create 3 tables: books, users and reviews in datatbase. After created, data in "books.csv" file will be inported into books table.

*application.py: 
    main application

*html files:
    -resgister.html for registration page
    -login.html for login page
    -index.html for homepage
    -book.html for  bookpage
    -error.html for  404 error code page
    -api.json for  render api data

*css files:
    2 files: register-logion.css and homepage.css

*how it work:
    -enter route /registration to create an account
    -after created an account, click on Sign in link to redirect to login page and login by your account
    -after login, you will be redirect to homepage, where you can search for a book 
    -if you click on a title, the bookpage of this book will be showed and you can leave a review, view rating from goodread and rate for this book
    -go to the link /api/<isbn> to view api data in json file
    -hover your username and click Logout to logout
    
    
    