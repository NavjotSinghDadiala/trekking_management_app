# forms.py
#
# DESIGN CHOICE:
# To keep this application beginner-friendly and extremely easy to explain during a viva,
# we are NOT using WTForms or Flask-WTF libraries. 
#
# Instead:
# 1. We write simple HTML forms directly inside the Jinja2 templates (e.g. login.html, register.html).
# 2. We retrieve form values inside Flask routes using the standard 'request.form["field_name"]' dictionary.
# 3. We validate inputs inside the routes using simple python checks (e.g. 'if not username: flash("Username is required")').
#
# This completely eliminates unnecessary code abstractions and makes it very obvious how data flows 
# from the user's browser straight to our database.
