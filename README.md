# YT-dashboard-streamlit

This project transforms [datasets of YouTube metrics](https://www.kaggle.com/datasets/kenjee/ken-jee-youtube-data?select=Aggregated_Metrics_By_Video.csv) into a web-app dashboard using Python and Streamlit. The web app consists of two features: 

* **Aggregate Metrics** of the whole videos, which includes:
  * Engagement metrics (Views, Comments, Subs, and more) compared to the average (median) numbers for the channel
  * Metrics of performance (Thumbnail, Impressions, CTR) to extract insights of video impressions to users
* **Individual Video Analysis**, which includes:
  * Number of views by Subscribed Users, with addition of top 10 countries watching 
  * View comparison on the first 30 days, compared to views in the 20th, 50th, and 80th percentile
  
![screenshot](https://raw.githubusercontent.com/itsalamhere/YT-dashboard-streamlit/master/images/Aggregate%20Metrics%20(1).png)

![screenshot](https://raw.githubusercontent.com/itsalamhere/YT-dashboard-streamlit/master/images/Aggregate%20Metrics%20(2).png)

![screenshot](https://raw.githubusercontent.com/itsalamhere/YT-dashboard-streamlit/master/images/Individual%20Video%20Analysis%20(1).png)

![screenshot](https://raw.githubusercontent.com/itsalamhere/YT-dashboard-streamlit/master/images/Individual%20Video%20Analysis%20(2).png)
