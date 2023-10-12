# fake-news-pt-eu
Dataset with fake and real news in European Portuguese

Up to my knowledge, this is the first dataset with fake and real news in European Portuguese publicly available ever.

It has over 60 000 rows with news articles and statements extracted through Web Scraping.

The dataset is comprised of 4 columns: Text (news title and body merged together), Label (0 for fake, 1 for real), Source and URL.

The Source column was added because many fake news websites love to promote articles from other fake news websites, which means not all news present on a given website belong to it.

All the fact-checks also had the source behind the statement being fact-checked, which varied from individuals like politicians or celebrities to social media as a whole.

The Web Scrapers used to gather the data are also available, alongside many python notebooks with different classification models and techniques.
