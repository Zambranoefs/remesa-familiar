import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from datetime import timedelta
import locale

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///remesa_familiar.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.route("/confirmation", methods=["GET", "POST"])
@login_required
def confirmation():

    customer_id = session["user_id"]

    order = db.execute ("SELECT * FROM helper;")
    customer = db.execute ("SELECT * FROM clientes WHERE cedula = :cedula", cedula=customer_id)
    phone = db.execute ("SELECT telefono FROM cuentas WHERE cuenta = :cuenta", cuenta=order[0]["cuenta"])
    bs = order[0]["bs"]
    bank = order[0]["banco"]
    account = order[0]["cuenta"]
    euros = order[0]["euros"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        db.execute("INSERT INTO pedidos (fecha, bs, banco, cuenta, euros, cedula) VALUES(:fecha, :bs, :banco, :cuenta, :euros, :cedula);",
                    fecha=datetime.now() + timedelta(hours=1), bs=bs, banco=bank, cuenta=account, euros=euros, cedula=customer_id)

        history_extract = db.execute("SELECT * FROM pedidos WHERE cedula = :cedula", cedula = session["user_id"])

        return render_template("history.html", history=history_extract,
                                registered="¡Pedido registrado! Serás contactado por nuestro equipo para su procesamiento")

    else:
        return render_template("confirmation.html", bs=bs, bank=bank, account=account, euros=euros,
                                name=customer[0]["nombre"], customer_id=customer[0]["cedula"], phone=phone[0]["telefono"])


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """ remittance, rate of the day and remittance calculator"""

    customer_id = session["user_id"]

    accounts = db.execute("SELECT banco, cuenta FROM cuentas WHERE cedula = :cedula ORDER BY banco;", cedula=customer_id)
    bs = request.form.get("bs")
    account = request.form.get("account")
    bank = db.execute("SELECT banco FROM cuentas WHERE cuenta = :cuenta", cuenta=account)
    euros = request.form.get("euros")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        db.execute("DELETE FROM helper;")
        db.execute("INSERT INTO helper VALUES (:bs, :bank, :account, :euros)", bs=bs, bank=bank[0]["banco"],
                    account=account, euros=euros)

        return redirect("/confirmation")

    else:
        return render_template("index.html", accounts=accounts, rate=227470.61)

@app.route("/recover", methods=["GET", "POST"])
def recover():
    """Security questions for password password forgotten"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        customer_id = request.form.get("id")
        vehicle = request.form.get("vehicle")
        pet = request.form.get("pet")

        # Query the database for customer id
        check_customer = db.execute("SELECT * FROM clientes WHERE cedula = :cedula", cedula=customer_id)

        # Query the database for the answer to first security question
        check_vehicle = db.execute("SELECT * FROM respuestas WHERE cedula = :cedula AND vehiculo = :vehiculo",
                                    cedula=customer_id, vehiculo=vehicle)

        # Query the database for the answer to second security question
        check_pet = db.execute("SELECT * FROM respuestas WHERE cedula = :cedula AND mascota = :mascota",
                                cedula=customer_id, mascota=pet)

        # Ensure customer exists
        if len(check_customer) != 1:
            return render_template("recover.html", invalidId="Nº de cédula inválido")

        # Ensure first answer is correct
        if len(check_vehicle) != 1:
            return render_template("recover.html", invalidVehicle="Modelo de vehículo incorrecto")

        # Ensure second answer is correct
        if len(check_pet) != 1:
            return render_template("recover.html", invalidPet="Nombre de mascota incorrecto")

        return redirect("/new_password")

    else:
        return render_template("recover.html")


@app.route("/new_password", methods=["GET", "POST"])
def new_password():
    """Allow customer to set a new password when it was forgotten"""

    customer_id = request.form.get("id")
    newPass = request.form.get("newPass")
    confirmation = request.form.get("confirmation")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query the database for customer_id
        check_id = db.execute("SELECT * FROM clientes WHERE cedula = :cedula", cedula=customer_id)

        # Ensure customer exists
        if len(check_id) != 1:
            return render_template("new_password.html", invalidId="Nº de cédula inválido")

        # Ensure new password and confirmation match
        if newPass != confirmation:
            return render_template("new_password.html", invalidConfirm="Las contraseñas no coinciden")

        password_hash = generate_password_hash(newPass)

        # Update customer's password: https://stackoverflow.com/a/4732865/13485188
        db.execute("UPDATE clientes SET hash = :hash WHERE cedula = :cedula;", hash=password_hash, cedula=customer_id)

        return render_template("login.html", success="La nueva contraseña ha sido registrada")

    else:
        return render_template("new_password.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM clientes WHERE cedula = :cedula", cedula=request.form.get("id"))

        # Ensure username exists and password is correct
        if len(rows) != 1:
            return render_template("login.html", invalid="Nº de cédula inválido")

        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", invalid="Contraseña incorrecta")

        # Remember which user has logged in
        session["user_id"] = rows[0]["cedula"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/accounts", methods=["GET", "POST"])
@login_required
def new_bank_account():
    """Show and register customer's bank accounts"""

    customer_id = session["user_id"]

    accounts = db.execute("SELECT banco, cuenta, telefono FROM cuentas WHERE cedula = :cedula;", cedula=customer_id)

    newBank = request.form.get("newBank")
    newAccount = request.form.get("newAccount")
    newPhone = request.form.get("newPhone")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        db.execute("INSERT INTO cuentas VALUES (:cuenta, :banco, :telefono, :cedula);",
                    cuenta=newAccount, banco=newBank, telefono=newPhone, cedula=customer_id)

        return redirect("/accounts")

    else:

        return render_template("accounts.html",accounts=accounts)

@app.route("/delete_accounts", methods=["POST"])
@login_required
def delete_account():
    """Delete bank accounts and orders related to those accounts"""

    deleteAccount = request.form.get("deleteAccount")

    db.execute("DELETE FROM cuentas WHERE cuenta = :cuenta", cuenta=deleteAccount)

    return redirect ("/accounts")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        customer_id = request.form.get("id")
        name = request.form.get("name")
        phone = request.form.get("phone")
        bank = request.form.get("bank")
        account = request.form.get("account")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        vehicle = request.form.get("vehicle")
        pet = request.form.get("pet")

        # Query database for customer_id
        id_check = db.execute("SELECT * FROM clientes WHERE cedula = :cedula;", cedula=customer_id)

        # Query database for account
        account_check = db.execute("SELECT * FROM cuentas WHERE cuenta = :cuenta;", cuenta=account)

        # Check if customer_id exists
        if len(id_check) == 1:
            return render_template("register.html", error=f"Ya existe un registro con este número de cédula: {customer_id}")

        # Check if account exists
        if len(account_check) == 1:
            return render_template("register.html", error=f"Ya existe un registro con este número de cuenta: {account}")

        # Ensure that both password and confirmation match
        if password != confirmation:
            return render_template("register.html", error="La contraseña y su confirmación no coinciden")

        # Hash the password
        password_hash = generate_password_hash(password)

        # Register new customer
        db.execute("INSERT INTO clientes VALUES (:cedula, :nombre, :hash)",
                    cedula=customer_id, nombre=name, hash=password_hash)

        # Register customer's account
        db.execute("INSERT INTO cuentas VALUES (:cuenta, :banco, :telefono, :cedula)",
                    cuenta=account, banco=bank, telefono=phone, cedula=customer_id)

        # Register the answers to security questions
        db.execute("INSERT INTO respuestas VALUES (:cedula, :vehiculo, :mascota)",
                    cedula=customer_id, vehiculo=vehicle, mascota=pet)



        # Redirect user to home page
        return render_template("login.html", registered="¡Registro exitoso! Puedes iniciar sesión")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Show history of remittances"""

    history_extract = db.execute("SELECT * FROM pedidos WHERE cedula = :cedula", cedula = session["user_id"])

    if request.method == "POST":

        order = request.form.get("order")

        db.execute("DELETE FROM pedidos WHERE nro = :order;", order=order)

        return redirect("/history")

    else:
        return render_template("history.html", history=history_extract)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Allow customer to update their current password"""

    customer_id = session["user_id"]
    password= request.form.get("password")
    newPass = request.form.get("newPass")
    confirmation = request.form.get("confirmation")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query the database for current password
        rows = db.execute("SELECT * FROM clientes WHERE cedula = :cedula", cedula=customer_id)

        # Ensure current password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("profile.html", invalid="Contraseña actual incorrecta")

        # Ensure new password and confirmation match
        if newPass != confirmation:
            return render_template("profile.html", invalidConfirm="Las contraseñas no coinciden")

        password_hash = generate_password_hash(newPass)

        # Update customer's password: https://stackoverflow.com/a/4732865/13485188
        db.execute("UPDATE clientes SET hash = :hash WHERE cedula = :cedula;", hash=password_hash, cedula=customer_id)

        return render_template("profile.html", success="La nueva contraseña ha sido registrada")

    else:
        return render_template("profile.html")


@app.route("/delete_customer", methods=["POST"])
@login_required
def delete_customer():
    """Delete a customer"""

    # Delete current customer
    db.execute("DELETE FROM clientes WHERE cedula= :cedula", cedula=session["user_id"])

    logout()

    return render_template("login.html", deleted="Lamentamos verte partir =(")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)