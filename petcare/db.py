from petcare import app, db, mongo
from petcare.models import User, Pet
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

with app.app_context():
    # db.drop_all()
    # db.create_all()

    # Update all records with a default value for pet_gender
    # db.session.execute(text('UPDATE Pet SET pet_gender = "Male" WHERE pet_gender IS NULL'))
    # db.session.commit()

    # Close the session
    db.session.close()
    # mongo.db.create_collection("PetReports")
# This will create tables if they do not already exist.
    #
    # u1 = User(username='Shaik', email='shaik@gmail.com', password='123456789')
    #
    # # Add the user to the session and commit to the database
    # db.session.add(u1)
    # db.session.commit()
    #
    # # Print the user to confirm it's added
    # print(u1)
