# fake-news-pt-eu

This project was developed to contribute to the fight against fake news, with a stronger focus on the European Portuguese language. If you find this repository useful, please cite it in your work, alongside [our paper](https://doi.org/10.1109/TLA.2024.10472958).

The diagram below depicts the project's pipeline, with the two English and European Portuguese approaches:

![Complete Pipeline](https://github.com/ro-afonso/fake-news-pt-eu/assets/93609933/b40a6d84-578d-4bb4-b101-bbf29da21cb2)

## European Portuguese Dataset

Based on the conducted search, this is the first dataset with fake and real news in European Portuguese publicly available.

It contains over 60 000 rows with news articles and statements extracted through Web Scraping. The web scrapers were automated by resorting to Beautiful Soup and Selenium.

The dataset is comprised of 4 columns: Text (news title and body merged together), Label (0 for fake, 1 for real), Source, and URL.

The Source column was added because many fake news websites love to promote articles from other fake news websites, which means not all articles present on a given website belong to it.

All the fact-checks also had the source behind the statement being fact-checked, which varied from individuals like politicians or celebrities to social media as a whole.

The Web Scrapers used to gather the data are also available, alongside many Python notebooks with different classification models and techniques.

## Best Machine Learning and Deep Learning models

Many models were trained using different packages and technologies, including:
  * Scikit-learn for Machine Learning
  * Tensorflow, Keras, Transformers, and PyTorch for Deep Learning
  * NLTK and Spacy for Natural Language Processing
  * Pandas, Numpy, and Matplotlib for Exploratory Data Analysis

However, the best models for the English and European Portuguese approach were BERT (0.96 F1-score) with tokenized text data and XGBoost (0.957 F1-score) with pre-processed text (lemmatization and stopword removal), Sentiment Analysis, POS tagging and TF-IDF, respectively.

The distilled version of the English BERT model is available [here](https://drive.google.com/file/d/1UNbhCPbJk_-mmc-nsf9Ag0a7UIIBaSnu/view?usp=sharing).

The European Portuguese XGBoost model is available [here](https://drive.google.com/file/d/1-9-YE54klQOXPqCfmMQZ2z93QqwfXW0Z/view?usp=sharing). Since the AWS EC2 instance of the Free Tier used in the project only has 1 GB of RAM, this model couldn't be used. To solve this issue, another distilBERT model was trained, this time with the European Portuguese data, with an F1-score of 0.92. The model is available [here](https://drive.google.com/file/d/1mnFrT7LpFtNkxb1SoiuReGGTNmOUMnTJ/view?usp=sharing).

## System Development

To put the ML and DL models into action, the following system was developed:

![App development and deployment diagram github](https://github.com/ro-afonso/fake-news-pt-eu/assets/93609933/9541a82a-d472-4c47-92b2-6da7b1b85909)

A [Chrome extension](https://chromewebstore.google.com/detail/fake-news-detector/ccflafojkdphjeeblbekbfkkihcbobef) and Android application communicate with a Flask app run with Gunicorn on a Docker container inside an AWS EC2 instance, which allows users to check whether a given text is real or fake through POST and GET requests.

Users can also report fake or real news articles, which are then processed in a script run on a local computer with a dedicated Graphical Processing Unit (GPU).

The models are fine-tuned with the feedback data and then sent over to the cloud instance through Secure Shell (SSH) and Secure File Transfer Protocol (SFTP) commands, as well as a POST request which allows the Flask app to replace the old models with the improved ones.

The Chrome extension is available [here](https://chromewebstore.google.com/detail/fake-news-detector/ccflafojkdphjeeblbekbfkkihcbobef).

## Requirements

* [VS Code](https://code.visualstudio.com/) or a similar code editor
* [Anaconda](https://www.anaconda.com/download/success)
* [AWS Account](https://aws.amazon.com/free) (1 Year Free Tier)
* [Android Studio](https://developer.android.com/studio)

## System Setup

Download the repository files and follow the steps below to set up and deploy the system:

### AWS EC2 with Containerised Flask App

  1. After creating your AWS account, navigate to the EC2 dashboard
  2. Create a pem file to use as the key pair, name it "fake-news-demo.pem", and save it in the "Flask Cloud and Local RESTful Script" local folder
  3. Launch a new EC2 instance using the following free tier eligible offers and specifications:
     * Select the "Amazon Linux 2023 AMI" as the AMI
     * Select either "t3.micro" or "t3.nano" as the instance type (varies with region)
     * Select the pem file created earlier as the key pair
     * Allow SSH, HTTP, and HTTPS traffic
     * Select 15 GBs of gp3 storage
  4. After launching the EC2 instance, you need to ensure the key is not publicly viewable. To do this, open PowerShell or CMD on your local pc, set the "Flask Cloud and Local RESTful Script" folder path, and run the following command:
     * `chmod 400 fake-news-demo.pem` 
  5. Connect to your EC2 instance using your Public IPv4 DNS and the command below:
     * `ssh -i fake-news-demo.pem ec2-user@YOUR-EC2-PUBLIC-IPv4-DNS`
  6. Once connected, run the following commands to install Docker in EC2:
     * `sudo yum install docker`
     * `sudo service docker start`
     * `sudo usermod -a -G docker ec2-user`
  7. Disconnect from EC2 with `exit` and reconnect again using the ssh command. Confirm that Docker is installed by running `docker info`
  8. Disconnect from EC2 with `exit` and open the "compose.yml" file
     * This will be used alongside the Dockerfile to mount volumes so that the Flask app can access the ML and DL models within the Docker container
  9. Change the domain used in the first two directories of the "volumes" section. You can either use a paid domain if you own one or create a domain for free with your EC2 IP address and nip.io
      * For example, if your EC2 IP is 01.23.456.789 then your domain would be 01-23-456-789.nip.io (only for testing purposes, not recommended in production)
  10. Send a copy of all Docker, python, and tflite files inside the "Flask Cloud and Local RESTful Script" folder using the following commands:
      * `scp -i fake-news-demo.pem NEW_mobile_distilBERT_optimized.tflite ec2-user@YOUR-EC2-PUBLIC-IPv4-DNS:/home/ec2-user`
      * `scp -i fake-news-demo.pem mobile_portuguese_distilBERT_optimized.tflite ec2-user@YOUR-EC2-PUBLIC-IPv4-DNS:/home/ec2-user`
      * `scp -i fake-news-demo.pem Dockerfile ec2-user@YOUR-EC2-PUBLIC-IPv4-DNS:/home/ec2-user`
      * `scp -i fake-news-demo.pem docker-compose.yml ec2-user@YOUR-EC2-PUBLIC-IPv4-DNS:/home/ec2-user`
      * `scp -i fake-news-demo.pem Flask_app_optimized.py ec2-user@YOUR-EC2-PUBLIC-IPv4-DNS:/home/ec2-user`
  11. Connect to EC2 and run `ls` to confirm that all files were transferred successfully
  12. It is advised to use https instead of the default and less secure http connection in your Flask App. To do this, install certbot by running the command below:
      * `sudo yum install certbot`
  13. Once installed, run the following command to create your free SSL certificate with certbot:
      * `sudo certbot certonly --standalone -d YOUR-DOMAIN`
      * As mentioned before, use a paid domain or your EC2 IP with nip.io (for example, 01-23-456-789.nip.io)
  14. Follow the instructions on the terminal to create your certificate. Once finished, run the following command to check if the certificate was created successfully:
      * `sudo certbot certificates`
  15. The certificate is only valid for 90 days, but it can be renewed. Start by running `sudo yum install cronie` 
  16. Open the editor with vim by running `sudo crontab -e`
  17. Type "i" to enter "insert mode" and paste the following command:
      * `0 */12 * * * certbot renew --quiet --post-hook "docker restart fake-news-cont"`
      * This cron job runs every day at midday and midnight to renew the certificate if its expiration date is close. The Docker container is then restarted automatically to apply the new certificate
  18. Press "Esc", type ":wq" and hit "enter" to save and exit the editor
  19. Install docker-compose by running the following commands:
      * `sudo curl -L "https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-$(uname -s)-$(uname -m)"  -o /usr/local/bin/docker-compose`
      * `sudo mv /usr/local/bin/docker-compose /usr/bin/docker-compose`
      * `sudo chmod +x /usr/bin/docker-compose`
      * Confirm that docker-compose is installed by running `docker-compose version`
  20. Build the Docker image using the "docker-compose.yml" file by running the command below:
      * `docker-compose build`
  21. Create and deploy your Docker container with Gunicorn by running the following command:
      * `docker-compose up -d`
  22. With the container running, the Flask app is ready to use. A message will also be displayed by the Flask app when you visit your domain in a web browser
  23. To get a prediction for a given news article, send a POST request using the following PowerShell command in VS Code:
      * `Invoke-RestMethod -Method POST -Uri "YOUR-FULL-DOMAIN/predict" -Headers @{"Content-Type" = "application/json"} -Body '{"text": "Your news article to predict here", "language" : "english"}'`
      * Adapt the command by changing the text, language, and full domain (for example, https://01-23-456-789.nip.io)
  24. You can also report news articles in the feedback mode by running the following PowerShell command:
      * `Invoke-RestMethod -Method POST -Uri "YOUR-FULL-DOMAIN/feedback" -Headers @{"Content-Type" = "application/json"} -Body '{"text": "Report news article here" , "label" : "0", "language" : "english"}'`
      * Adapt the command by changing the text, language, and full domain (for example, https://01-23-456-789.nip.io)

### Chrome Extension

  1. Open the "script.js" file located inside the "News Detector Chrome Extension" folder and change the IP address to your full domain (for example, https://01-23-456-789.nip.io).
  2. Access extension settings in Google Chrome, click on "Load Unpacked" and select the "News Detector Chrome Extension" folder to load it
  3. Fill in the input fields of the Chrome extension and experiment with both prediction and feedback modes

### Android App

  1. Open the "Fake News Android App" folder using Android Studio and locate the "RetrofitClient.kt" file under "app/java/com/example/fakenewsapp/RetrofitClient.kt"
  2. Change the "BASE_URL" value to your full domain (for example, https://01-23-456-789.nip.io)
  3. Run the app to install and test it on the simulator or your own device connected via USB (the latter requires developer options turned on)

### RESTful Script for Model Improvement

  1. Move the "Final_Dataset_English.csv" and "Final_dataset_portuguese.csv" files to the "Flask Cloud and Local RESTful Script" folder
  2. Download the distilBERT models from [here](https://drive.google.com/file/d/1UNbhCPbJk_-mmc-nsf9Ag0a7UIIBaSnu/view?usp=sharing) and [here](https://drive.google.com/file/d/1mnFrT7LpFtNkxb1SoiuReGGTNmOUMnTJ/view?usp=sharing), and move them to the "Flask Cloud and Local RESTful Script" folder
  3. Open the terminal in Anaconda, set the path to the "Flask Cloud and Local RESTful Script" folder, and create the environment by running the following command:
     * `conda env create -f environment.yml`
  4. Once the "news-feedback-fetch" environment is created, open VS Code using the Anaconda launcher with the new environment
  5. Open the "Flask Cloud and Local RESTful Script" folder and modify the "data_fetch_websocket.py" script as follows:
     * Change the IP address in the "send_model_to_ec2" function to your Public IPv4 DNS
     * Change the IP address in the "fetch_user_feedback_data" function to your full domain (for example, https://01-23-456-789.nip.io)
  6. Run the "data_fetch_websocket.py" script using your Anaconda environment. Make sure "news-feedback-fetch:conda" is shown in the lower right corner of VS Code to use the environment
  7. The script will start fetching the feedback data from the Flask app, with an interval of 30 seconds between each GET request
  8. Test the feedback functionality by reporting news articles that are incorrectly predicted by the models
      * The script requires at least two different news articles to improve the models. If only one article is received, the feedback data is discarded
      * Reporting many similar news articles can trigger the similarity check of the script, which converts them into a single news article
      * This is done to group similar topics or events together, as a way to reduce model bias and decide between contradicting stances
  9. Once the program finishes improving the models with the feedback data, connect to your EC2 instance. Run `ls` to check the new and improved tflite files received over SFTP and SSH
  10. The news articles reported to the Flask App should now return the right predictions, according to the feedback data sent earlier
      * Be aware that the Transfer Learning technique used to improve the models still keeps all the knowledge acquired during the initial training phase with the datasets
      * The most significant aspect in this phase is the complexity of the data patterns, which varies based on how much the reported news articles differ from the ones in the initial datasets
      * As a consequence, reporting just a few news articles might not be enough to improve the predictions of the new models
