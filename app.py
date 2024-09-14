from flask import Flask, request, jsonify, session, redirect, url_for
import mysql.connector
import bcrypt
import logging
from clean_text import clean_text
from sklearn.feature_extraction.text import CountVectorizer
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import shutil
from tempfile import NamedTemporaryFile
import os

# Initialize Flask app
flask_app = Flask(__name__)
flask_app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(flask_app, supports_credentials=True, methods=["GET", "POST", "DELETE"])

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MySQL Configuration
jdbc_url = "jdbc:mysql://localhost:3306/plantdisease?createDatabaseIfNotExist=true"

# Extract host, port, and database from the JDBC URL
jdbc_parts = jdbc_url.split("/")
host_port_db = jdbc_parts[2]
host, port = host_port_db.split(":")
database_with_params = jdbc_parts[3]
database, _ = database_with_params.split("?")

db = mysql.connector.connect(
    host="localhost",
    port=3306,  # Ensure port is an integer
    user="root",
    password="12345678",
    database="plantdisease"
)

cursor = db.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
		id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        email VARCHAR(255),
        password VARCHAR(255),
        user_type VARCHAR(255)
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS plants (
		id INT AUTO_INCREMENT PRIMARY KEY,
        plant_name VARCHAR(255),
        description TEXT,
        image LONGTEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS plant_disease (
		id INT AUTO_INCREMENT PRIMARY KEY,
        plant_name VARCHAR(255),
        disease_name VARCHAR(255),
        description TEXT,
        image LONGTEXT
    )
""")


# Load the TensorFlow model
model = tf.keras.models.load_model("best_model.keras")

# Class names
class_name = ['Potato___Early_blight',
              'Potato___Late_blight',
              'Potato___healthy',
              'Strawberry___Leaf_scorch',
              'Strawberry___healthy',
              'Tomato___Bacterial_spot',
              'Tomato___Septoria_leaf_spot',
              'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
              'Tomato___healthy']


@flask_app.route('/api/status', methods=['GET'])
def statu():
    return jsonify({"Registration successful"})


@flask_app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    email = data.get('email')
    password = data.get('password')
    userType = data.get('userType', 'USER')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    query = "INSERT INTO users (first_name, last_name, email, password, user_type) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (firstName, lastName, email, hashed_password, userType))
    db.commit()

    logging.info("User registered: {}".format(email))

    return jsonify({"message": "Registration successful"})


@flask_app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        cursor.execute("SELECT id, first_name, last_name, password, user_type FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            logging.info("User logged in: {}".format(email))
            return jsonify({
                "message": "Login successful",
                "id": user[0],
                "firstName": user[1],
                "lastName": user[2],
                "userType": user[4]
            })
        else:
            logging.error("Failed login attempt: {}".format(email))
            return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        logging.error("Error during login: {}".format(str(e)))
        return jsonify({"error": "An unexpected error occurred"}), 500


@flask_app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    logging.info("User logged out")
    return jsonify({"message": "Logout successful"})


@flask_app.route('/api/add_plant', methods=['POST'])
def add_plant():
    data = request.get_json()
    plantName = data.get('plantName')
    description = data.get('description')
    image = data.get('image')  # Assuming image is a base64 encoded string or URL

    # Insert query to add the plant information to the database
    query = "INSERT INTO plants (plant_name, description, image) VALUES (%s, %s, %s)"
    cursor.execute(query, (plantName, description, image))
    db.commit()

    logging.info("Plant added: {}".format(plantName))

    return jsonify({"message": "Plant added successfully"})


@flask_app.route('/api/view_all_plants', methods=['GET'])
def view_all_plants():
    try:
        # Query to retrieve all plant information
        query = "SELECT id, plant_name, description, image FROM plants"
        cursor.execute(query)
        plants = cursor.fetchall()

        if not plants:
            return jsonify({"error": "No plants found"}), 404

        # Transform the result into a list of dictionaries
        plants_data = []
        for plant in plants:
            plants_data.append({
                "id": plant[0],
                "plantName": plant[1],
                "description": plant[2],
                "image": plant[3]  # Assuming this is a Base64 encoded string or URL
            })

        logging.info("All plants retrieved successfully")
        return jsonify(plants_data), 200

    except mysql.connector.Error as err:
        logging.error("MySQL error: {}".format(err))
        return jsonify({"error": "Database error occurred"}), 500

    except Exception as e:
        logging.error("Unexpected error: {}".format(e))
        return jsonify({"error": "An unexpected error occurred"}), 500


@flask_app.route('/api/delete_plants/<int:plant_id>', methods=['DELETE'])
def delete_plants(plant_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    user_id = session['user_id']
    try:
        # Check if the plant exists and if the user has permission to delete it (if applicable)
        cursor.execute("SELECT id FROM plants WHERE id = %s", (plant_id,))
        plants = cursor.fetchone()

        if plants:
            # If the plant exists, delete it
            cursor.execute("DELETE FROM plants WHERE id = %s", (plant_id,))
            db.commit()
            logging.info("Plant deleted for user {}: {}".format(user_id, plant_id))
            return jsonify({"message": "Plant deleted successfully"}), 200
        else:
            return jsonify({"error": "Plant not found"}), 404

    except mysql.connector.Error as err:
        logging.error("MySQL error: {}".format(err))
        return jsonify({"error": "Database error occurred"}), 500

    except Exception as e:
        logging.error("Unexpected error: {}".format(e))
        return jsonify({"error": "An unexpected error occurred while deleting plant"}), 500


@flask_app.route('/api/add_plant_disease', methods=['POST'])
def add_disease():
    data = request.get_json()
    plantName = data.get('plantName')
    diseaseName = data.get('diseaseName')
    description = data.get('description')
    image = data.get('image')  # Assuming image is a base64 encoded string or URL

    # Insert query to add the plant information to the database
    query = "INSERT INTO plant_disease (plant_name, disease_name, description, image) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (plantName, diseaseName, description, image))
    db.commit()

    logging.info("Plant Disease added: {}".format(diseaseName))

    return jsonify({"message": "Plant Disease added successfully"})


@flask_app.route('/api/view_plants_disease', methods=['GET'])
def view_all_disease():
    try:
        # Query to retrieve all plant information
        query = "SELECT id, plant_name, disease_name, description, image FROM plant_disease"
        cursor.execute(query)
        plant_disease = cursor.fetchall()

        if not plant_disease:
            return jsonify({"error": "No plant disease found"}), 404

        # Transform the result into a list of dictionaries
        disease_data = []
        for disease in plant_disease:
            disease_data.append({
                "id": disease[0],
                "plantName": disease[1],
                "diseaseName": disease[2],
                "description": disease[3],
                "image": disease[4]  # Assuming this is a Base64 encoded string or URL
            })

        logging.info("All plant diseases retrieved successfully")
        return jsonify(disease_data), 200

    except mysql.connector.Error as err:
        logging.error("MySQL error: {}".format(err))
        return jsonify({"error": "Database error occurred"}), 500

    except Exception as e:
        logging.error("Unexpected error: {}".format(e))
        return jsonify({"error": "An unexpected error occurred"}), 500



@flask_app.route('/api/delete_plant_disease/<int:disease_id>', methods=['DELETE'])
def delete_plant_disease(disease_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    user_id = session['user_id']
    try:
        # Check if the disease exists and if the user has permission to delete it (if applicable)
        cursor.execute("SELECT id FROM plant_disease WHERE id = %s", (disease_id,))
        plant_disease = cursor.fetchone()

        if plant_disease:
            # If the plant disease exists, delete it
            cursor.execute("DELETE FROM plant_disease WHERE id = %s", (disease_id,))
            db.commit()
            logging.info("Plant disease deleted for user {}: {}".format(user_id, disease_id))
            return jsonify({"message": "Plant disease deleted successfully"}), 200
        else:
            return jsonify({"error": "Plant disease not found"}), 404

    except mysql.connector.Error as err:
        logging.error("MySQL error: {}".format(err))
        return jsonify({"error": "Database error occurred"}), 500

    except Exception as e:
        logging.error("Unexpected error: {}".format(e))
        return jsonify({"error": "An unexpected error occurred while deleting plant disease"}), 500



@flask_app.route('/api/admin/total_users', methods=['GET'])
def get_total_users():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    user_id = session['user_id']

    try:
        cursor.execute("SELECT COUNT(*) FROM users WHERE user_type = 'USER'")
        total_users = cursor.fetchone()[0]

        return jsonify({"total_users": total_users})
    except Exception as e:
        logging.error("Error fetching total users: {}".format(str(e)))
        return jsonify({"error": "An unexpected error occurred while fetching total users"}), 500


@flask_app.route('/api/predict', methods=['POST'])
def predict_image():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    try:
        file = request.files['file']
        with NamedTemporaryFile(delete=False) as tmp_file:
            shutil.copyfileobj(file, tmp_file)
            tmp_file_path = tmp_file.name

        result_index, confidence_score = model_prediction(tmp_file_path)
        os.remove(tmp_file_path)

        # Check confidence score
        if confidence_score < 98:
            return jsonify({
                "message": "Please re upload the picture",
                "confidence_score": f"{confidence_score:.2f}%"
            })
        else:
            return jsonify({
                "prediction": class_name[result_index],
                "confidence_score": f"{confidence_score:.2f}%"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def model_prediction(file_path: str):
    image = tf.keras.preprocessing.image.load_img(file_path, target_size=(128, 128))
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])  # convert single image to batch
    predictions = model.predict(input_arr)
    result_index = np.argmax(predictions)  # return index of max element
    confidence_score = np.max(predictions) * 100  # calculate confidence score as a percentage
    return result_index, confidence_score


if __name__ == "__main__":
    flask_app.run(debug=False, host='0.0.0.0', port=5001)
