#===========================================================
# App Creation and Launch
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db import connect_db
from app.helpers.errors import register_error_handlers, not_found_error


# Create the app
app = Flask(__name__)

# Setup a session for messages, etc.
init_session(app)

# Handle 404 and 500 errors
register_error_handlers(app)


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def placeholder_name():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT * FROM tasks ORDER BY priority DESC"
        result = client.execute(sql)
        tasks = result.rows
        print (tasks)

        # And show them on the page
        return render_template("pages/home.jinja", tasks=tasks)
    
#-----------------------------------------------------------
# Changing the completion
#-----------------------------------------------------------
@app.post("/complete-task")
def complete_task():
    # If form checked then completed
    completed  = 1 if request.form.get("completion") else 0
    # Get hidden id from form
    id = request.form.get("id")

    with connect_db() as client:
        sql = "UPDATE tasks SET completion = ? WHERE id=?;"
        values = [completed, id]
        client.execute(sql, values)

    return redirect("/")

#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_thing(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM tasks WHERE id=?"
        values = [id]
        client.execute(sql, values)
        return redirect("/")

#-----------------------------------------------------------
# Add a new task
#-----------------------------------------------------------
@app.post("/add-task")
def add_task():
    with connect_db() as client:
        name = request.form.get("name")
        priority = request.form.get("priority")
        sql = """
            INSERT INTO tasks (name, priority)
            VALUES (?,?)
        """
        values = [name, priority]
        client.execute(sql, values)
        return redirect("/")


#-----------------------------------------------------------
# About page route
#-----------------------------------------------------------
@app.get("/about/")
def about():
    return render_template("pages/about.jinja")


#-----------------------------------------------------------
# Things page route - Show all the things, and new thing form
#-----------------------------------------------------------
@app.get("/things/")
def show_all_things():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT id, name FROM todo ORDER BY name ASC"
        result = client.execute(sql)
        things = result.rows

        # And show them on the page
        return render_template("pages/things.jinja", things=things)


#-----------------------------------------------------------
# Thing page route - Show details of a single thing
#-----------------------------------------------------------
@app.get("/thing/<int:id>")
def show_one_thing(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT id, name, price FROM things WHERE id=?"
        values = [id]
        result = client.execute(sql, values)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            thing = result.rows[0]
            return render_template("pages/thing.jinja", thing=thing)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for adding a thing, using data posted from a form
#-----------------------------------------------------------
@app.post("/add")
def add_a_thing():
    # Get the data from the form
    name  = request.form.get("name")
    price = request.form.get("price")

    # Sanitise the inputs
    name = html.escape(name)
    price = html.escape(price)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO things (name, price) VALUES (?, ?)"
        values = [name, price]
        client.execute(sql, values)

        # Go back to the home page
        flash(f"Thing '{name}' added", "success")
        return redirect("/things")


