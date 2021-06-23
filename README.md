# How to run:
1. Install all of the packages listed in the `requirements.txt` (preferably in a virtual environment).
2. Run the run.py script.
3. Open `localhost` with the port number `5000`.


### Notes:
This was tested on Python 3.8.6 64bit on a Windows machine.

Go to `/admin` route to access the admin section.

The username and password for the admin section is `username` and `password` respectively.

If `/admin` or any other route does not open, it's likely because your browser is forcing a trailing backslash

at the end of the route. You can set `app.url_map.strict_slashes = False` in  `managing_research_papers/__init__.py`

to tell the flask to not care about the url and solve the problem.
