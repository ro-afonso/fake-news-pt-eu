from flask import Flask, request, jsonify
import traceback
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from transformers import DistilBertTokenizer
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
import os
import json
from flask_talisman import Talisman

# Initialize the Flask application
app = Flask(__name__)
Talisman(app, content_security_policy=None)
CORS(app)

# Load the TFLite model or the fine-tuned version if it exists
try:
    interpreter = tf.lite.Interpreter(model_path='fine_tuned_mobile_distilBERT_optimized.tflite')
    interpreter.allocate_tensors()
    print("Fine-tuned model loaded in Flask!")
except:
    interpreter = tf.lite.Interpreter(model_path='NEW_mobile_distilBERT_optimized.tflite')
    interpreter.allocate_tensors()
    print("Normal model loaded in Flask!")

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load the tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

# Load the distilBERT portuguese model or the improved version if it exists
try:
    portuguese_interpreter = tf.lite.Interpreter(model_path='fine_tuned_mobile_distilBERT_portuguese_optimized.tflite')
    portuguese_interpreter.allocate_tensors()
    print("Fine-tuned portuguese model loaded in Flask!")
except:
    # Load both portuguese model and TF-IDF vectorizer
    portuguese_interpreter = tf.lite.Interpreter(model_path='mobile_portuguese_distilBERT_optimized.tflite')
    portuguese_interpreter.allocate_tensors()
    print("Normal portuguese model loaded in Flask!")

portuguese_input_details = portuguese_interpreter.get_input_details()
portuguese_output_details = portuguese_interpreter.get_output_details()

# Store future user feedback data
user_feedback_data = []
user_feedback_data_portuguese = []

@app.route('/')
def home_endpoint():
    return 'Hello World!'

# Receive text data and send prediction
@app.route('/predict', methods=['POST'])
def predict():
    try:
        global interpreter
        global input_details
        global output_details
        global portuguese_interpreter
        global portuguese_input_details
        global portuguese_output_details
        # Extract the data from the request with latin-1 encoding for portuguese words with accents, while still accepting english words
        data_str = request.get_data().decode('latin-1')
        
        # Parse the JSON data manually
        data = json.loads(data_str)
        language = data['language']
        print("language received:", language)

        # Preprocess the text
        text = data['text']
        
        print(text)

        text_tokens = tokenizer.encode_plus(text, max_length=128, padding='max_length', truncation=True, return_tensors='tf')

        if language == 'english':
            print("English prediction request received!")
            # Make a prediction using the TFLite model
            input_data = np.array(text_tokens['input_ids'], dtype=np.int32)
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details[0]['index'])
        else:
            print("Portuguese prediction request received!")
            # Make a prediction using the TFLite model
            input_data = np.array(text_tokens['input_ids'], dtype=np.int32)
            portuguese_interpreter.set_tensor(portuguese_input_details[0]['index'], input_data)
            portuguese_interpreter.invoke()
            output_data = portuguese_interpreter.get_tensor(portuguese_output_details[0]['index'])

        # Convert prediction to a label
        label = 1 if output_data[0][0] >= 0.5 else 0
        print(label)

        response = jsonify({'prediction': label, 'success': True})
        return response

    except KeyError:
        traceback.print_exc()
        return jsonify({'error': 'Bad request. The "text" parameter is missing.'}), 400

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Receive feedback from users
@app.route('/feedback', methods=['POST'])
def receive_feedback():
    try:
        # Extract the data from the request
        data_str = request.get_data().decode('latin-1')

        # Parse the JSON data manually
        data = json.loads(data_str)

        # Preprocess the text, label and user IP of each request
        text = data['text'].strip()
        label = int(data['label'])
        user_ip = request.remote_addr  # Get the user's IP address
        language = data['language'].strip()
        print(language)

        epic_user = 'epic_user'
        epic_user2 = 'epic_user2'
        
        if language == "english":
            print("English feedback received!")
            # Store the user-generated data in the user_feedback_data list
            user_feedback_data.append({'text': text, 'label': label, 'user_ip':user_ip})

            #user_feedback_data.append({'text': text, 'label': label, 'user_ip':epic_user})# REMOVE THIS DON'T FORGET!!!!!!!!!!!!!!!!!!!

            user_feedback_data.append({'text': text, 'label': label, 'user_ip':epic_user2})# REMOVE THIS DON'T FORGET!!!!!!!!!!!!!!!!!!!

            for user_feedback in user_feedback_data:
                print(user_feedback)

            response = jsonify({'message': 'Feedback received successfully!', 'success': True})
        else:
            print("Portuguese feedback received!")
            # Store the user-generated data in the user_feedback_data_portuguese list
            user_feedback_data_portuguese.append({'text': text, 'label': label, 'user_ip':user_ip})

            #user_feedback_data_portuguese.append({'text': text, 'label': label, 'user_ip':epic_user})# REMOVE THIS DON'T FORGET!!!!!!!!!!!!!!!!!!!

            user_feedback_data_portuguese.append({'text': text, 'label': label, 'user_ip':epic_user2})# REMOVE THIS DON'T FORGET!!!!!!!!!!!!!!!!!!!

            for user_feedback in user_feedback_data_portuguese:
                print(user_feedback)

            response = jsonify({'message': 'Feedback received successfully!', 'success': True})
        return response

    except KeyError:
        traceback.print_exc()
        return jsonify({'error': 'Bad request. The "text" or "label" parameter is missing.'}), 400

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Fetch user feedback data to improve the model
@app.route('/fetch_feedback', methods=['GET'])
def fetch_feedback():
    feedback = []
    feedback_portuguese = []
    if user_feedback_data:
        feedback = user_feedback_data.copy()
        user_feedback_data.clear()
    if user_feedback_data_portuguese:
        feedback_portuguese = user_feedback_data_portuguese.copy()
        user_feedback_data_portuguese.clear()
    return jsonify({'feedback_data': feedback, 'feedback_data_portuguese': feedback_portuguese,'success': True})

# Load fine_tuned model for improved predictions based on user feedback
@app.route('/load_fine_tuned_model', methods=['POST'])
def load_fine_tuned_model():
    try:
        global interpreter
        global input_details
        global output_details
        interpreter = tf.lite.Interpreter(model_path='fine_tuned_mobile_distilBERT_optimized.tflite') # Folder in the docker container
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        print("Fine-tuned model loaded in Flask!")
        return jsonify({'message': 'Fine-tuned model loaded successfully!', 'success': True})
    except:
        return jsonify({'message': 'Fine-tuned model not found!', 'success': True})

# Load improved lscv for portuguese predictions
@app.route('/load_improved_portuguese_model', methods=['POST'])
def load_improved_portuguese_model():
    try:
        global portuguese_interpreter
        global portuguese_input_details
        global portuguese_output_details
        portuguese_interpreter = tf.lite.Interpreter(model_path='fine_tuned_mobile_distilBERT_optimized.tflite') # Folder in the docker container
        portuguese_interpreter.allocate_tensors()
        portuguese_input_details = portuguese_interpreter.get_input_details()
        portuguese_output_details = portuguese_interpreter.get_output_details()
        print("Improved portuguese model loaded in Flask!")
        return jsonify({'message': 'Improved portuguese model loaded successfully!', 'success': True})
    except:
        return jsonify({'message': 'Improved portuguese model not found!', 'success': True})