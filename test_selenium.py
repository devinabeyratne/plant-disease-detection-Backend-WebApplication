from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize Chrome WebDriver
driver = webdriver.Chrome()

# Test Registration
def test_registration():
    driver.get("http://localhost:3000/registerPage")  # Assuming registration page is at this URL

    # Fill out the registration form
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'firstName'))).send_keys("Test3")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'lastName'))).send_keys("User")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys("test3@gmail.com")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys("123")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'confirmPassword'))).send_keys("123")

    submit_button = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div[1]/div/form/button')))
    submit_button.click()

    # Check for alert message or success message
    time.sleep(5)  # Adjust time if needed
    try:
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        if "Registration successful" in alert.text:
            print("Registration successful")
        else:
            print("Registration failed")
        alert.accept()
    except Exception as e:
        print(f"Registration test failed: {str(e)}")


# Test Login
def test_login():
    driver.get("http://localhost:3000")  # Assuming login page is at this URL

    # Fill out the login form
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))).send_keys(
        "devin@gmail.com")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))).send_keys("123")

    submit_button = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
    submit_button.click()

    # Check for login success alert
    time.sleep(5)  # Adjust time if needed
    try:
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        if "Login successful" in alert.text:
            print("Login successful")
        else:
            print("Login unsuccessful")
        alert.accept()
    except Exception as e:
        print(f"Login test failed: {str(e)}")


# Define the function to test the prediction
def test_prediction():
    driver.get("http://localhost:3000/PlantDiseaseDetector")  # URL where the React app is running

    # Upload an image (ensure the image exists in the directory)
    file_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]')))
    file_input.send_keys(
        "/Users/mihindew/Desktop/Plant_Disease_detection_copy/1.JPG")  # Change this path to a real image file on your system

    submit_button = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]')))
    submit_button.click()

    # Wait for the prediction result
    time.sleep(5)  # Consider increasing this if your backend needs more time to respond

    try:
        # Check for the retake message (if present)
        retake_message = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Please re upload the picture")]'))
        )
        print(f"Retake message: {retake_message.text}")

        # Check for prediction result
        prediction_result = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Prediction Result")]'))
        )
        print(f"Prediction result: {prediction_result.text}")

    except Exception as e:
        print(f"Prediction test failed: {str(e)}")




# Run the tests
test_registration()
test_login()
test_prediction()


# Close the browser after testing
driver.quit()
