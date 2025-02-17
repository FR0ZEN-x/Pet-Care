from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from petcare import mongo

# Registration Form for Normal User
class RegistrationForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = mongo.db.users.find_one({"username": username_to_check.data.title()})
        if user:
            raise ValidationError('Username already registered! Please try a different username.')

    def validate_email(self, email_to_check):
        user = mongo.db.users.find_one({"email": email_to_check.data})
        if user:
            raise ValidationError('Email address already registered! Please try a different email.')

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    submit = SubmitField('Register')


# Login Form for Normal User
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Registration Form for Veterinarians
class VetRegistrationForm(FlaskForm):

    def validate_username(self, username_to_check):
        vet = mongo.db.users.find_one({"username": username_to_check.data.title()})
        if vet:
            raise ValidationError('Username already registered! Please try a different username.')

    def validate_email(self, email_to_check):
        vet = mongo.db.users.find_one({"email": email_to_check.data})
        if vet:
            raise ValidationError('Email address already registered! Please try a different email.')

    def validate_vet_license(self, vet_license_to_check):
        vet = mongo.db.users.find_one({"vet_license": vet_license_to_check.data})
        if vet:
            raise ValidationError('Vet License already registered! Please try a different vet license.')

        vet_l = mongo.db.vetlicenses.find_one({"vet_license": vet_license_to_check.data})
        if not vet_l:
            raise ValidationError('Invalid License! Please try a different vet license.')


    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    vet_license = StringField('Vet Licence', validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField('Register')


# Login Form for Veterinarians
class VetLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    vet_license = StringField('Vet Licence', validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField('Login')


# Form to Add a Pet
class AddPet(FlaskForm):
    pet_name = StringField('Pet Name', validators=[DataRequired()])
    pet_species = StringField('Pet Type', validators=[DataRequired()])
    pet_gender = SelectField("Pet Gender", choices=[("male", "Male"), ("female", "Female")], validators=[DataRequired()])
    submit = SubmitField('Add Pet')


# Form to Add Vet License (Admin only)
class AddVet(FlaskForm):
    vet_license = StringField('Vet Licence', validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField('Add Vet')

class EditUsername(FlaskForm):
    def validate_username(self, username_to_check):
        user = mongo.db.users.find_one({"username": username_to_check.data.title()})
        if user:
            raise ValidationError('Username already registered! Please try a different username.')

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Update Username')

class EditEmail(FlaskForm):
    def validate_email(self, email_to_check):
        user = mongo.db.users.find_one({"email": email_to_check.data})
        if user:
            raise ValidationError('Email address already registered! Please try a different email.')

    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Email')

class EditPassword(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    submit = SubmitField('Update Password')
