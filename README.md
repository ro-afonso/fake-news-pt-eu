# fake-news-pt-eu
This project was developed to contribute to the fight against fake news, with a stronger focus on the European Portuguese language.

Based on the coducted search, this is the first dataset with fake and real news in European Portuguese publicly available ever.

The diagram below depicts the project's pipeline, with the two English and European Portuguese approaches:

![Complete Pipeline](https://github.com/ro-afonso/fake-news-pt-eu/assets/93609933/4d48f6b2-0ecc-4fcd-a233-c2a9b585ce65)

## European Portuguese Dataset

It has over 60 000 rows with news articles and statements extracted through Web Scraping.

The dataset is comprised of 4 columns: Text (news title and body merged together), Label (0 for fake, 1 for real), Source and URL.

The Source column was added because many fake news websites love to promote articles from other fake news websites, which means not all news present on a given website belong to it.

All the fact-checks also had the source behind the statement being fact-checked, which varied from individuals like politicians or celebrities to social media as a whole.

The Web Scrapers used to gather the data are also available, alongside many python notebooks with different classification models and techniques. The best models for the English and European Portuguese approach were BERT (0.96 F1-score) with tokenized text data and XGBoost (0.957 F1-score) with pre-processed text (lemmatization and stopword removal), Sentiment Analysis, POS tagging and TF-IDF, respectively.

## Applications Development and Deployment

To put the ML and DL models into action, the system shown below was developed:

![App development and deployment diagram](https://github.com/ro-afonso/fake-news-pt-eu/assets/93609933/aade6d7c-3b5f-4cb9-95e6-d69dbea40f75)

A Chrome extension and Android application communicate with a Flask app ran on a docker container inside an AWS EC2 instance, which allows users to check whether a given text is real or fake through POST and GET requests.

Users can also report fake or real news, which are then processed in a script ran on a local computer with a dedicated Graphical Processing Unit (GPU).

The models are fine-tuned with the feedback data and then sent over to the cloud instance through Secure Shell (SSH) and Secure File Transfer Protocol (SFTP) commands, as well as a POST request which allows the Flask app to replace the old models with the improved ones.
