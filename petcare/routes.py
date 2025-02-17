from petcare import app, mongo, bcrypt
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from petcare.forms import EditUsername, EditEmail, EditPassword, RegistrationForm, AddPet, LoginForm, AddVet, VetRegistrationForm, VetLoginForm
from flask_login import login_user, logout_user, login_required, current_user
from petcare.models import User, VetLicense, ObjectId
from datetime import datetime
import pandas as pd
from models.predict import predict_health_risk

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = mongo.db.users.find_one({"username": form.username.data.title()})
        if attempted_user and bcrypt.check_password_hash(attempted_user['password'], form.password.data):
            # Pass the user_data as a dictionary directly
            user_obj = User(attempted_user)  # No ** unpacking
            login_user(user_obj)
            flash(f'Success! You are logged in as: {attempted_user["username"]}', category='success')
            return redirect(url_for('main_page'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field.capitalize()}: {error}', category='danger')
    return render_template('login.html', form=form)



@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user_data = {
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password,
            "is_vet": False
        }
        mongo.db.users.insert_one(user_data)

        # Pass the user_data as a dictionary directly
        user_obj = User(user_data)  # No ** unpacking
        login_user(user_obj)

        flash(f'Account created successfully! You are now logged in as {user_data["username"]}', category='success')
        return redirect(url_for('main_page'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.capitalize()}: {error}', category='danger')
    return render_template('register.html', form=form)


@app.route('/vet_login', methods=['GET', 'POST'])
def vet_login_page():
    form = VetLoginForm()
    if form.validate_on_submit():
        # Attempt to find the vet based on username
        attempted_vet = mongo.db.users.find_one({"username": form.username.data.title()})

        if attempted_vet and bcrypt.check_password_hash(attempted_vet['password'], form.password.data):
            # Verify that the vet license matches
            if attempted_vet.get("vet_license") == form.vet_license.data:
                vet_obj = User(attempted_vet)
                login_user(vet_obj)
                flash(f'Success! You are logged in as: {attempted_vet["username"]}', category='success')
                return redirect(url_for('main_page'))
            else:
                flash('Vet license is incorrect!', category='danger')
        else:
            flash('Username or password is incorrect!', category='danger')
    return render_template('vet_login.html', form=form)


@app.route('/vet_register', methods=['GET', 'POST'])
def vet_register_page():
    form = VetRegistrationForm()
    if form.validate_on_submit():
        # Vet License is valid and verified, proceed with registration
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        vet_data = {
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password,
            "vet_license": form.vet_license.data,
            "is_vet": True
        }
        mongo.db.users.insert_one(vet_data)  # Insert vet data into the database
        vet_obj = User(vet_data)  # Create User object from vet data
        login_user(vet_obj)  # Log the vet in automatically after registration
        flash(f'Vet Account created successfully! You are now logged in as {vet_data["username"]}',
                category='success')
        return redirect(url_for('main_page'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.capitalize()}: {error}', category='danger')
    return render_template('vet_register.html', form=form)


@app.route('/add_vet', methods=['GET', 'POST'])
def add_vet_page():
    form = AddVet()
    if form.validate_on_submit():
        # Here, admin can add the vet license to the database
        vet_license = form.vet_license.data
        if not VetLicense.get(vet_license):
            mongo.db.vetlicenses.insert_one({"vet_license": vet_license})
            flash('Vet Licence added successfully!', category='success')
        else:
            flash('Vet Licence already exists!', category='danger')
        return redirect(url_for('add_vet_page'))
    return render_template('add_vet.html', form=form)


@app.route('/add_pet', methods=['GET', 'POST'])
@login_required
def add_pet_page():
    form = AddPet()
    if form.validate_on_submit():
        pet_data = {
            "_id": ObjectId(),  # Generate a unique ID for the pet
            "name": form.pet_name.data.title(),
            "species": form.pet_species.data.title(),
            "gender": form.pet_gender.data.title(),
            "owner_id": ObjectId(current_user.id)
        }

        # Update the user document to include the new pet
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$push": {"pets": pet_data}}  # Only store in the user's pets array
        )

        flash('Pet added successfully!', category='success')
        return redirect(url_for('add_pet_page'))

    return render_template('add_pet.html', form=form)


@app.route('/remove_pet/<pet_id>', methods=['POST'])
@login_required
def remove_pet_page(pet_id):

    pet_obj_id = ObjectId(pet_id)
    user = mongo.db.users.find_one({"_id": ObjectId(current_user.id), "pets._id": pet_obj_id}) # Find the user and check if the pet exists in their embedded array
    if user:
        # Remove the pet from the user's pets array
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$pull": {"pets": {"_id": pet_obj_id}}}
        )
        flash('Pet has been removed successfully!', category='success')
    else:
        flash('Pet not found or you do not have permission to delete it!', category='danger')

    return redirect(url_for('profile_page'))

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    return redirect(url_for('home_page'))


@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile_page():
    user_pets = list(mongo.db.pets.find({"owner_id": current_user.id}))
    return render_template('profile.html', pets=user_pets)


@app.route('/consult_veterinarian')
def consult_veterinarian_page():
    return render_template('consult_veterinarian.html')


@app.route('/analyze_pet_health/<pet_id>', methods=['GET', 'POST'])
@login_required
def analyze_pet_health_page(pet_id):
    # Fetch all users and get their pets
    all_pets = []
    for user in mongo.db.users.find():  # Iterate through all users
        all_pets.extend(user.get('pets', []))  # Add each pet from the user's pets list
    selected_pet = next((pet for pet in all_pets if str(pet['_id']) == str(pet_id)), None)

    if request.method == 'POST':
        user_id = session["_id"]
        pet_id = request.form.get("pet_id")

        input_data = {
            "Age": float(request.form.get("age")),
            "Weight (kg)": float(request.form.get("weight")),
            "Symptoms": request.form.getlist("general_symptoms"),
            "Previous Health Issues": request.form.get("prev_issues", ""),
            "Hydration (%)": float(request.form.get("hydration", 50)),
            "Heart Rate (bpm)": float(request.form.get("heart_rate", 0)),
            "Respiratory Rate (bpm)": float(request.form.get("respiratory_rate", 0)),
            "Temperature (°C)": float(request.form.get("temperature")),
            "Environmental Exposure": request.form.get("environmental_exposure", "Indoor")
        }

        prediction = predict_health_risk(input_data)
        report = {
            "date": pd.Timestamp.now(),
            "input_data": input_data,
            "prediction": prediction
        }

        mongo.db.users.update_one(
            {"_id": ObjectId(user_id), "pets._id": ObjectId(pet_id)},
            {"$push": {"pets.$.health_reports": report}}
        )

        return jsonify(prediction)

    return render_template('analyze_pet_health.html', selected_pet=selected_pet)

@app.route('/select_pet')
@login_required
def select_pet_page():
    if current_user.is_vet:
        # Fetch all pets for vet users
        all_users = mongo.db.users.find()
        pets = []
        for user in all_users:
            pets.extend(user.get('pets', []))
    else:
        pets = current_user.pets if hasattr(current_user, 'pets') else []

    return render_template('select_pet.html', pets=pets)

@app.route('/edit_user_info', methods=['GET', 'POST'])
@login_required
def edit_user_info_page():
    form1 = EditUsername()
    form2 = EditEmail()
    form3 = EditPassword()

    # Prepare a dictionary to store updated user data
    updated_data = {}

    # Handle Username form
    if form1.validate_on_submit():
        try:
            # Check if the new username already exists
            existing_user = mongo.db.users.find_one({"username": form1.username.data.title()})
            if existing_user:
                flash('Username already registered! Please try a different username.', category='danger')
            else:
                updated_data['username'] = form1.username.data
                flash('Username updated successfully!', category='success')
        except Exception as e:
            flash(f"An error occurred while updating username: {str(e)}", category='danger')

    # Handle Email form
    if form2.validate_on_submit():
        try:
            # Check if the new email already exists
            existing_email = mongo.db.users.find_one({"email": form2.email.data})
            if existing_email:
                flash('Email address already registered! Please try a different email.', category='danger')
            else:
                updated_data['email'] = form2.email.data
                flash('Email updated successfully!', category='success')
        except Exception as e:
            flash(f"An error occurred while updating email: {str(e)}", category='danger')

    # Handle Password form
    if form3.validate_on_submit():
        try:
            if form3.password.data != form3.confirm_password.data:
                flash('Passwords do not match. Please try again.', category='danger')
            else:
                hashed_password = bcrypt.generate_password_hash(form3.password.data).decode('utf-8')
                updated_data['password'] = hashed_password
                flash('Password updated successfully!', category='success')
        except Exception as e:
            flash(f"An error occurred while updating password: {str(e)}", category='danger')

    # If any data was updated, apply changes to the user
    if updated_data:
        try:
            mongo.db.users.update_one({"_id": ObjectId(current_user.id)}, {"$set": updated_data})
        except Exception as e:
            flash(f"An error occurred while updating your information: {str(e)}", category='danger')

    return render_template('edit_user_info.html', form1=form1, form2=form2, form3=form3)

@app.route('/main')
@login_required
def main_page():
    return render_template('main.html')


