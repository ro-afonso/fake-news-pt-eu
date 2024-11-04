import time
import requests
import numpy as np
import pandas as pd
import tensorflow as tf
import pickle
import torch
from transformers import DistilBertTokenizer, DistilBertModel, TFDistilBertModel, DistilBertTokenizer
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.models import load_model
from keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
import paramiko

print("GPUS found:",tf.config.experimental.list_physical_devices('GPU'))

# Define the custom objects
custom_objects = {
    'TFDistilBertModel': TFDistilBertModel,
}

# Load the respective tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

# Load original dataset and corresponding evaluation results
df = pd.read_csv("Final_dataset_english.csv")
df.fillna('', inplace=True)

# Split data into train and test sets
X = df['text'].values
y = df['label'].values
X_train, X_test, y_train, y_test_original = train_test_split(X, y, test_size=0.2, random_state=42)

with open('X_test_tokenized_DistilBERT_uncased.pkl', 'rb') as f:
    X_test_tokenized = pickle.load(f)

original_loss = 0.106
original_accuracy = 0.958

# Load the pre-trained distilBERT model and tokenizer for text similarity check
model_name = "distilbert-base-uncased"
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertModel.from_pretrained(model_name)

# Load the users' english feedback dataset or create it if it doesn't exist
try:
    # Read the DataFrame from the CSV file
    feedback_en_df = pd.read_csv("Feedback_dataset_en.csv")
    # Convert the string representation back to a list of IPs
    feedback_en_df['user_ips'] = feedback_en_df['user_ips'].apply(lambda ips: ips.split(','))
    print("Feedback dataset loaded!")
except:
    # Initialize an empty dataframe if the dataset doesn't exist
    print("No feedback dataset found! Creating a new one...")
    feedback_en_df = pd.DataFrame(columns=['count', 'label', 'text', 'user_ips'])
    feedback_en_df.to_csv("Feedback_dataset_en.csv", index=False)
    feedback_en_df = pd.read_csv("Feedback_dataset_en.csv")

# Load original portuguese dataset and corresponding evaluation results
df = pd.read_csv("Final_dataset_portuguese.csv")

# Split data into train and test sets
X = df['Text'].values
y = df['Label'].values

X_train_pt, X_test_pt, y_train_pt, y_test_original_pt = train_test_split(X, y, test_size=0.2, random_state=42)

with open('X_test_tokenized_distilBERT_uncased_portuguese.pkl', 'rb') as f:
    X_test_tokenized_pt = pickle.load(f)

original_accuracy_pt = 0.924

# Load the users' portuguese feedback dataset or create it if it doesn't exist
try:
    # Read the DataFrame from the CSV file
    feedback_pt_df = pd.read_csv("Feedback_dataset_pt.csv")
    # Convert the string representation back to a list of IPs
    feedback_pt_df['user_ips'] = feedback_pt_df['user_ips'].apply(lambda ips: ips.split(','))
    print("Portuguese feedback dataset loaded!")
except:
    # Initialize an empty dataframe if the dataset doesn't exist
    print("No Portuguese feedback dataset found! Creating a new one...")
    feedback_pt_df = pd.DataFrame(columns=['count', 'label', 'text', 'user_ips'])
    feedback_pt_df.to_csv("Feedback_dataset_pt.csv", index=False)
    feedback_pt_df = pd.read_csv("Feedback_dataset_pt.csv")

# Identify the entries that best represent the remaining ones based on their similarity
def select_representative_entries(similarity_group):
    grouped_entries = {}
    for entry, similarity in similarity_group:
        text = entry.get('text', None)
        label = entry.get('label', None)
        user_ip = entry.get('user_ip', None)
        if text is not None and label is not None:
            key = (label, text)
            if key not in grouped_entries:
                grouped_entries[key] = {'count': 1, 'label': label, 'text': text, 'user_ips': set()}
                grouped_entries[key]['user_ips'].add(user_ip)
            else:
                grouped_entries[key]['count'] += 1
                grouped_entries[key]['user_ips'].add(user_ip)
                
    # Find the most common entry in the similarity group
    representative_entry = max(grouped_entries.values(), key=lambda x: x['count'])

    # We only consider entries with from more than one user to avoid bias
    if representative_entry['count'] != 1:
        return representative_entry
    else:
        return None

# Define a function to get sentence embeddings
def get_sentence_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return torch.mean(outputs.last_hidden_state, dim=1).squeeze()

# Function to group similar texts based on cosine similarity
def group_similar_texts(feedback_data, similarity_threshold=0.91):
    grouped_texts = []
    embeddings = torch.stack([get_sentence_embedding(feedback['text']) for feedback in feedback_data])
    similarity_matrix = cosine_similarity(embeddings)

    # Initialize a list to keep track of already processed indices
    processed_indices = []

    for i in range(len(similarity_matrix)):
        if i in processed_indices:
            continue

        group = [i]
        for j in range(i + 1, len(similarity_matrix)):
            if similarity_matrix[i, j] >= similarity_threshold:
                group.append(j)
                processed_indices.append(j)

        # Add similarity values to the group
        group_with_similarity = [(feedback_data[index], similarity_matrix[i, index]) for index in group]
        grouped_texts.append(group_with_similarity)

    return grouped_texts

# Select the relevant feedback for the fine-tuning process
def filter_user_feedback(feedback_data, language):
    global feedback_en_df
    global feedback_pt_df

    if language == "english":
        feedback_df = feedback_en_df.copy()
    else:
        feedback_df = feedback_pt_df.copy()

    # Convert feedback_data to a DataFrame
    current_feedback_df = pd.DataFrame(feedback_data)

    # Drop duplicates based on all columns (label, text, and user_ip)
    current_feedback_df = current_feedback_df.drop_duplicates()

    # Convert the DataFrame back to a list of dictionaries
    feedback_data = current_feedback_df.to_dict(orient='records')

    # Group similar texts based on cosine similarity
    grouped_texts = group_similar_texts(feedback_data)

    # Create set of each representative entry's text and label (avoids counting the same entry more than once)
    representative_entry_set = set()

    filtered_feedback = set()
    # Print the grouped texts along with similarity values
    for group in grouped_texts:
        print(group)

        # Identify the representative_entry
        representative_entry = select_representative_entries(group)
        print("Representative entry:", representative_entry)

        # Convert the representative entry to a DataFrame (if it exists)
        if representative_entry and (representative_entry['text'], representative_entry['label']) not in representative_entry_set:
            print("feedback_df")
            print(feedback_df.head())

            # Add the representative_entry's text and label tuple to the set to ignore future groups with it
            representative_entry_set.add((representative_entry['text'], representative_entry['label']))

            # Check if the representative entry exists in the feedback_df
            existing_row = feedback_df.loc[(feedback_df['label'] == int(representative_entry['label'])) & \
                                           (feedback_df['text'] == str(representative_entry['text']))]

            print("existing row")
            print(existing_row)

            if existing_row.empty:
                print("No row found!")
                # Create a new DataFrame with the representative_entry data
                new_data = pd.DataFrame([representative_entry])
                
                # Check if there's already a row with the same text but opposite label
                existing_row = feedback_df.loc[feedback_df['text'] == str(representative_entry['text'])]
                if existing_row.empty:
                    # If the row doesn't exist, we add it to the filtered_feedback  to fine-tune the model
                    filtered_feedback.add((int(representative_entry['label']), representative_entry['text']))
                    print("Now row found! Adding to filtered_feedback...")
                else:
                    print("Row with the same text but different label found! Not added to filtered_feedback...")

                # Create a new DataFrame with the existing data and the representative_entry data
                feedback_df = pd.concat([feedback_df, new_data], ignore_index=True)
                print("Representative entry added as a new row.")

                print("feedback_df before conversion:")
                print(feedback_df)

                # Get the row index of the newly added row
                row_index = feedback_df.index[-1]

                # Convert the 'user_ips' column to a string representation for the newly added row
                existing_row = feedback_df.loc[(feedback_df['label'] == int(representative_entry['label'])) & \
                                        (feedback_df['text'] == str(representative_entry['text']))]

                print("last row:",existing_row)

                representative_entry_user_ips = representative_entry['user_ips']
                print("entry user_ips")
                print(representative_entry_user_ips)

                user_ips_list = set(existing_row['user_ips'].iloc[0])
                print("user_ips_list:",user_ips_list)

                feedback_df.at[row_index, 'user_ips'] = user_ips_list
                print("feedback with user_ips_list")
                print(feedback_df)
            else:
                print("Text and Label already found in dataset!")
                # Check if the user_ips are different and, if so, increase the count for each new user ip
                representative_entry_user_ips = set(representative_entry['user_ips'])
                print("entry user_ips")
                print(representative_entry_user_ips)

                # Convert user_ips of existing_row to set
                existing_row_user_ips = set(existing_row['user_ips'].iloc[0])

                print("existing row user_ips")
                print(existing_row_user_ips)

                final_user_ips = representative_entry_user_ips | existing_row_user_ips
                print("final_user_ips")
                print(final_user_ips)

                # Get the row index of the existing_row
                row_index = existing_row.index[0]

                # Clear the 'user_ips' value of the feedback_df at the specified row_index
                feedback_df.at[row_index, 'user_ips'] = None

                # Add each IP from final_user_ips to the 'user_ips' column of feedback_df individually                    
                feedback_df.at[row_index, 'user_ips'] = final_user_ips
                feedback_df.at[row_index, 'count'] = len(final_user_ips)

                print("Updated DataFrame:")
                print(feedback_df)

    print("feedback_df")
    print(feedback_df)

    if len(filtered_feedback) == 1:
        # Remove the row of the dataset, as it won't be fine-tuned because validation split requires at least 2 entries
        for label, text in filtered_feedback:
            feedback_df = feedback_df.drop(feedback_df[(feedback_df['label'] == label) & (feedback_df['text'] == text)].index)
            print("filtered_feedback had len == 1, so its feedback_df row was removed!")
            print(feedback_df)
        filtered_feedback = None

    # Save the DataFrame to a CSV file
    if language == "english":
        feedback_df.to_csv("Feedback_dataset_en.csv", index=False)
        feedback_en_df = feedback_df.copy()
    else:
        feedback_df.to_csv("Feedback_dataset_pt.csv", index=False)
        feedback_pt_df = feedback_df.copy()

    return filtered_feedback

# Fine-tune the model with relevant data
def improve_model(filtered_feedback, language):
    # Create labels and texts variables
    labels = []
    texts = []

    # Unpack the tuples in the test_set and store the values in labels and texts lists
    for label, text in filtered_feedback:
        labels.append(int(label))
        texts.append(text)

    print("improve texts:",texts)
    print("improve labels",labels)

    # Tokenize the texts with the same tokenizer used during initial training
    max_length = 128  # Max sequence length used during training
    tokenized_texts = tokenizer(texts, max_length=max_length, padding='max_length', truncation=True, return_tensors='tf')

    # Prepare the new training data
    X_train = tokenized_texts['input_ids']
    y_train = np.array(labels) # Convert labels to a NumPy array to avoid validation split error

    # Fine-Tuning Setup
    optimizer = tf.keras.optimizers.Adam(learning_rate=2e-5) # Lower learning rates are often better for fine-tuning transformers
    loss = tf.keras.losses.BinaryCrossentropy(from_logits=False)
    metrics = ['accuracy']

    if language == "english":
        # Load the fine-tuned version if it exists, otherwise, load the original distilBERT model with custom objects
        try:
            distilBERT_model = load_model('dir_fine_tuned_distilBERT_model', custom_objects=custom_objects)
            #distilBERT_model.trainable = False # Set the entire model as untrainable to avoid creating new top layers
            print("English Fine-tuned model loaded!")  # And to ensure that we're fine-tuning the same top layers with each feedback update
        except:
            distilBERT_model = load_model('NEW_dir_model_DistilBERT_96', custom_objects=custom_objects)
            print("Original English model loaded!")
    else:
        # Load the fine-tuned version if it exists, otherwise, load the original distilBERT model with custom objects
        try:
            distilBERT_model = load_model('dir_fine_tuned_distilBERT_model_portuguese', custom_objects=custom_objects)
            #distilBERT_model.trainable = False # Set the entire model as untrainable to avoid creating new top layers
            print("Portuguese Fine-tuned model loaded!")  # And to ensure that we're fine-tuning the same top layers with each feedback update
        except:
            distilBERT_model = load_model('dir_model_DistilBERT_92_portuguese', custom_objects=custom_objects)
            print("Original Portuguese model loaded!")

    # Freeze pre-trained layers
    distilBERT_model.layers[1].trainable = False

    # Compile the model
    distilBERT_model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

    # Fine-Tune the Top Layers (Transfer Learning)
    history = distilBERT_model.fit(
        x=X_train,
        y=y_train,
        validation_split=0.2,  # Use a portion of the user feedback data for validation
        epochs=10,
        batch_size=64
    )

    if language == "english":
        # Use the fine-tuned model to make predictions on the tokenized test data
        y_pred_prob = distilBERT_model.predict(X_test_tokenized['input_ids'])

        # Convert the model's predictions to binary labels using a threshold (e.g., 0.5)
        y_pred = (y_pred_prob >= 0.5).astype(int).flatten()

        # Compare the predicted labels with the ground truth labels to calculate accuracy
        accuracy_fine_tuned = np.mean(y_pred == y_test_original)
        print("fine-tuned accuracy:",accuracy_fine_tuned)
        print("original accuracy:",original_accuracy)
    else:
        # Use the fine-tuned model to make predictions on the tokenized test data
        y_pred_prob = distilBERT_model.predict(X_test_tokenized_pt['input_ids'])

        # Convert the model's predictions to binary labels using a threshold (e.g., 0.5)
        y_pred = (y_pred_prob >= 0.5).astype(int).flatten()
        
        # Compare the predicted labels with the ground truth labels to calculate accuracy
        accuracy_fine_tuned = np.mean(y_pred == y_test_original_pt)
        print("fine-tuned accuracy:",accuracy_fine_tuned)
        print("original accuracy:",original_accuracy_pt)

    if language == "english":
        # Save the Fine-Tuned Model
        distilBERT_model.save('dir_fine_tuned_distilBERT_model')
    else:
        # Save the Fine-Tuned Model
        distilBERT_model.save('dir_fine_tuned_distilBERT_model_portuguese')
    
    print("fine-tuned model created!")

    # Convert the model to TensorFlow Lite format with optimization
    converter = tf.lite.TFLiteConverter.from_keras_model(distilBERT_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    print("fine-tuned model converted to tflite!")

    if language == "english":
        with open('fine_tuned_mobile_distilBERT_optimized.tflite', 'wb') as f:
            f.write(tflite_model)
    else:
        with open('fine_tuned_mobile_portuguese_distilBERT_optimized.tflite', 'wb') as f:
            f.write(tflite_model)

    # Check the fine-tuned models' predictions of the previous feedback data
    for text in texts:
        print("text to predict:",text)
        print("DistilBERT prediction:")

        text_tokens = tokenizer.encode_plus(text, max_length=max_length, padding='max_length', truncation=True, return_tensors='tf')

        # Make the prediction
        prediction = distilBERT_model.predict(text_tokens['input_ids'])[0][0]

        # Convert prediction to a label
        label = 1 if prediction >= 0.5 else 0
        confidence = prediction if prediction >= 0.5 else 1 - prediction

        print(f"Prediction: {label}")
        print(f"Confidence: {confidence:.4f}")

        print("TFlite prediction:")

        if language == "english":
            # Now test with the tflite converted model
            interpreter = tf.lite.Interpreter(model_path='fine_tuned_mobile_distilBERT_optimized.tflite')
        else:
            # Now test with the tflite converted model
            interpreter = tf.lite.Interpreter(model_path='fine_tuned_mobile_portuguese_distilBERT_optimized.tflite')
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        text_tokens = tokenizer.encode_plus(text, max_length=128, padding='max_length', truncation=True, return_tensors='tf')

        # Make a prediction using the TFLite model
        input_data = np.array(text_tokens['input_ids'], dtype=np.int32)
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])

        # Convert prediction to a label
        label = 1 if output_data[0][0] >= 0.5 else 0
        print("prediction:",output_data[0][0])
        print("final prediction:",label)

# Send fine-tuned model to the ec2 instance
def send_model_to_ec2(fine_tuned_model_path):
    # Specify EC2 instance variables for the SSH connection
    ec2_instance_ip = 'ec2-??-???-???-???.eu-north-1.compute.amazonaws.com'
    ec2_user = 'ec2-user'
    pem_file_path = 'fake-news-demo.pem'
    try:
        print("Begin!")
        # Establish an SSH connection to the EC2 instance
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ec2_instance_ip, username=ec2_user, key_filename=pem_file_path)

        print("Connected to ec2 instance!")

        # Transfer the fine-tuned model to the EC2 instance
        sftp = ssh.open_sftp()
        print("After open_sftp!")

        sftp.put(fine_tuned_model_path, '/home/ec2-user/'+fine_tuned_model_path)
        print("After put() method!")

        print("Before closing ssh!")
        # Close the SSH connection
        ssh.close()

        print("Fine-tuned model sent to EC2 instance successfully!")
        return True
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error sending the model to the EC2 instance:", e)
        return False

# Obtain user feedback to fine_tune the model
def fetch_user_feedback_data():
    while True:
        try:
            print("Fetching data...")
            response = requests.get('CLOUD-IP/fetch_feedback') # Replace CLOUD-IP with your full domain (for example, https://01-23-456-789.nip.io)
            if response.status_code == 200:
                data = response.json()
                feedback_data = data['feedback_data']
                feedback_data_portuguese = data['feedback_data_portuguese']
                if feedback_data:
                    filtered_feedback = filter_user_feedback(feedback_data, "english")
                    if filtered_feedback:
                        improve_model(filtered_feedback, "english")
                        fine_tuned_model_path = 'fine_tuned_mobile_distilBERT_optimized.tflite'
                        success = send_model_to_ec2(fine_tuned_model_path)
                        if success:
                            #Send request to flask to load new fine-tuned model
                            response = requests.post('CLOUD-IP/load_fine_tuned_model') # Replace CLOUD-IP with your full domain (for example, https://01-23-456-789.nip.io)
                            print(response.json()['message'])
                        else:
                            print("Failed sending the fine-tuned model to ec2!")
                if feedback_data_portuguese:
                    filtered_feedback = filter_user_feedback(feedback_data_portuguese, "portuguese")
                    if filtered_feedback:
                        print(response.json()['message'])
                        fine_tuned_model_path = 'fine_tuned_mobile_portuguese_distilBERT_optimized.tflite'
                        success = send_model_to_ec2(fine_tuned_model_path)
                        if success:
                            #Send request to flask to load new fine-tuned model
                            response = requests.post('CLOUD-IP/load_improved_portuguese_model') # Replace CLOUD-IP with your full domain (for example, https://01-23-456-789.nip.io)
                            print(response.json()['message'])
                        else:
                            print("Failed sending the fine-tuned model to ec2!")
            else:
                print('Failed to fetch feedback data. Status code:', response.status_code)
        except Exception as e:
            print('Error:', e)

        time.sleep(30) # Realistically, the user feedback data should be fetched once enough data is gathered for better model improvement

if __name__ == '__main__':
    fetch_user_feedback_data()