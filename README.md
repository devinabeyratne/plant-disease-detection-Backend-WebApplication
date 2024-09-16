# Plant Disease Detection Web Application - Backend

## Overview
This repository contains the backend code for a plant disease detection web application built using Flask and Python. The app uses Convolutional Neural Networks (CNNs) to analyze plant images and identify diseases. It provides APIs for user management, plant and disease information, and real-time predictions.

## Technologies Used
- **Flask**: Web framework for creating the REST API.
- **MySQL**: Database for storing user, plant, and disease data.
- **TensorFlow**: Machine learning framework for plant disease prediction using a pre-trained CNN model.
- **bcrypt**: Library for password hashing and security.
- **Flask-CORS**: To handle Cross-Origin Resource Sharing.
- **Logging**: For tracking activities such as user registration, login, and errors.

## Installation
1. **Clone the repository**:
    ```bash
    git clone https://https://github.com/devinabeyratne/plant-disease-detection-Backend-WebApplication.git
    cd plant-disease-detection-backend
    ```

2. **Create a virtual environment** (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the MySQL Database**:
    - Create a MySQL database named `plantdisease`.
    - Update the `db = mysql.connector.connect()` section in `app.py` with your database credentials if needed.

5. **TensorFlow Model**:
    - Ensure you have the pre-trained TensorFlow model (`best_model.keras`) in the root folder.

6. **Run the Flask Application**:
    ```bash
    python app.py
    ```

## Endpoints

### User Management
- **POST** `/api/register`: Register a new user.
- **POST** `/api/login`: User login.
- **POST** `/api/logout`: User logout.
- **GET** `/api/admin/total_users`: Fetch the total number of registered users (Admin only).

### Plant and Disease Management
- **POST** `/api/add_plant`: Add plant information.
- **GET** `/api/view_all_plants`: View all plants.
- **DELETE** `/api/delete_plants/<int:plant_id>`: Delete plant by ID.
- **POST** `/api/add_plant_disease`: Add plant disease information.
- **GET** `/api/view_plants_disease`: View all plant diseases.
- **DELETE** `/api/delete_plant_disease/<int:disease_id>`: Delete plant disease by ID.

### Disease Prediction
- **POST** `/api/predict`: Upload a plant image for disease prediction. The image should be sent as a form file, and the response will contain the predicted disease and confidence score.

## Logs
- Log file is generated in the root folder named `app.log`, which tracks user activities and errors.

## Notes
- The Flask app is set to run on `0.0.0.0` at port `5001` by default.
- Make sure to configure your database and environment settings correctly before running the application.# plant-disease-detection-Backend-WebApplication
