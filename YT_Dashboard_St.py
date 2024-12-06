# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pycountry
import streamlit as st
from datetime import datetime

### Define functions:

## Main: Load the Data
@st.cache_data
def load_data():

    ## df_agg       : Aggregated Metrics by Video
    ## df_agg_sub   : Aggregated Metrics by Country and Subscriber Status
    ## df_comments  : 
    
    df_agg      = pd.read_csv('Aggregated_Metrics_By_Video.csv').iloc[1:, :]
    df_agg_sub  = pd.read_csv('Aggregated_Metrics_By_Country_And_Subscriber_Status.csv')
    
    df_comments = pd.read_csv('All_Comments_Final.csv')
    df_time     = pd.read_csv('Video_Performance_Over_Time.csv')
    
    ## Data Wrangling: df_agg
    df_agg.columns = (df_agg.columns.str.lower()
       .str.replace(" (%)", "").str.replace(" ", "_")
       .str.replace("(", "in_").str.replace(")", "")
       .str.replace("-", "_").str.replace("\xad", ""))
    
    df_agg['video_publish_time']    = pd.to_datetime(df_agg['video_publish_time'], format='%b %d, %Y')
    df_agg['average_view_duration'] = df_agg['average_view_duration'].apply(
        lambda x: datetime.strptime(x, '%H:%M:%S'))
    
    df_agg['average_duration_in_sec']     = df_agg['average_view_duration'].apply(
        lambda x: x.second + x.minute*60 + x.hour*3600)
    df_agg['engagement_ratio']            = (df_agg['comments_added'] + df_agg['shares'] +
        df_agg['likes'] + df_agg['dislikes']) / df_agg['views']
    df_agg['views_per_sub_gained']        = df_agg['views'] / df_agg['subscribers_gained']
    
    df_agg.sort_values('video_publish_time', ascending=False, inplace=True)
    
    ## Data wrangling: Other DataFrames
    df_agg_sub.columns  = (df_agg_sub.columns
        .str.lower().str.replace(' ', '_'))
    
    df_comments.columns = (df_comments.columns
        .str.lower().str.replace('vidid', 'vid_id'))
    
    df_time.columns     = (df_time.columns
        .str.lower().str.replace(' ', '_'))
    df_time['date']     = pd.to_datetime(df_time['date'], format='mixed')

    return df_agg, df_agg_sub, df_comments, df_time

## Main: Changing Column Names to Title for Web Purposes
def column_to_title(string):
    return (string
        .replace('_', ' ')
        .title()
        .replace('Usd', 'USD')
        .replace('Percentage', '%')
        .replace('Average', 'Avg.')
        .replace(' Added', '')
        .replace('Click Through Rate', 'CTR'))

## Aggregate Metrics: Styling the DataFrame
def style_negative(v, props=''):
    """Style negative values in DataFrame"""
    try:    return props if v < 0 else None
    except: pass

def style_positive(v, props=''):
    """Style positive values in DataFrame"""
    try:    return props if v > 0 else None
    except: pass

## Individual Video Analysis: Simplifying views by countries

## Room for improvement: Sorting by top 10 countries, 
## changing format to countries' full names
def audience_simple(country_code, top_10_country):
    """Show representing countries"""
    if   country_code == 'US': return 'USA'
    elif country_code == 'IN': return 'India'
    else: return 'Other' 

def code_to_country(country_code, top_10_list):
    """Show top 10 views by countries"""
    if country_code in top_10_list:
        return pycountry.countries.get(
            alpha_2=country_code).name
    else: return 'Other'    

## Begin!

df_agg, df_agg_sub, df_comments, df_time = load_data()

### Engineer data for dashboard purposes

df_agg_diff = df_agg.copy()

## Take data from recent 12 months
time_window_12months = df_agg_diff['video_publish_time'].max() - pd.DateOffset(months=12)
median_agg           = df_agg_diff[
    df_agg_diff['video_publish_time'] >= time_window_12months].median(numeric_only=True)

## Median standard deviation
numeric_cols = np.array((df_agg_diff.dtypes == 'float64') | (df_agg_diff.dtypes == 'int64'))
df_agg_diff.iloc[:, numeric_cols] = (df_agg_diff.iloc[:, numeric_cols] - median_agg).div(median_agg)

## Performance metrics
performance_cols = ['video', 'video_title', 'video_publish_time',
    'impressions', 'impressions_click_through_rate',
    'average_percentage_viewed', 'average_duration_in_sec', 
    'views', 'likes', 'dislikes', 'comments_added', 'shares',
    'subscribers_gained', 'engagement_ratio', 'views_per_sub_gained']

df_agg_performance = df_agg.copy()
df_agg_performance = df_agg_performance[performance_cols]

df_agg_performance['thumbnail'] = df_agg_performance['video'].apply(
    lambda x : f"https://i.ytimg.com/vi/{x}/hqdefault.jpg")

df_agg_performance['video_publish_time'] = (
    df_agg_performance['video_publish_time'].apply(lambda x: x.date()))

df_agg_performance = df_agg_performance.reindex(
    columns = ['thumbnail'] + df_agg_performance.columns[:-1].to_list())
df_agg_performance = df_agg_performance.drop('video', axis=1)

    

## Merge daily data with publish data to get delta
df_time_diff = pd.merge(df_time, 
    df_agg.loc[:, ['video', 'video_publish_time']],
    left_on = 'external_video_id', right_on = 'video')
df_time_diff['days_published'] = (df_time_diff['date'] - 
    df_time_diff['video_publish_time']).dt.days

## Get last 12 months of data rather than all of them
date_12mths = df_agg['video_publish_time'].max() - pd.DateOffset(months=12)
df_time_diff_yr = df_time_diff[df_time_diff['video_publish_time'] >= date_12mths]

## Get daily view data (first 30), median & percentiles
views_days = pd.pivot_table(df_time_diff_yr,
    index = 'days_published', values = 'views',
    aggfunc = [np.mean, np.median, 
        lambda x: np.percentile(x, 80),
        lambda x: np.percentile(x, 20)]).reset_index()
views_days.columns = ['days_published','mean_views', 'median_views',
                      '80pct_views', '20pct_views']
views_days = views_days[views_days['days_published'].between(0, 30)]

views_cumulative = views_days.loc[:, ['days_published', 'median_views', '80pct_views', '20pct_views']]
views_cumulative.loc[:, ['median_views', '80pct_views', '20pct_views']] = (
    views_cumulative.loc[:, ['median_views', '80pct_views', '20pct_views']]).cumsum()

## Experiment for `code_to_country`: START
test_sub_filtered    = df_agg_sub[df_agg_sub['video_title'] == 
    'How I Would Learn Data Science (If I Had to Start Over)']    
test_sub_filtered    = test_sub_filtered.sort_values(['is_subscribed', 'views'], ascending=False)
top_10_country_test  = test_sub_filtered['country_code'].head(10).to_list()

test_sub_filtered['country'] = (test_sub_filtered['country_code'].apply(
    lambda x: code_to_country(x, top_10_country_test)))

# test_check_sub = test_sub_filtered.groupby(
#     ['is_subscribed']).agg(total_views = ('views', 'sum'))

test_comments = df_comments[df_comments['vid_id'] == '4OZip0cgOho']
test_time     = df_time[df_time['external_video_id'] == '4OZip0cgOho']
## Experiment: END (run smoothly)

## Build the dashboard

add_sidebar = st.sidebar.selectbox(
    'Aggregate or Individual Video', (
        'Aggregate Metrics', 'Individual Video Analysis'))

if add_sidebar == 'Aggregate Metrics':
    
    st.header('Ken Jee YouTube Aggregated Data')
    
    st.subheader('Medians of Metrics')
    
    st.write('The following numbers are explained as follows:')
    st.write('- **Big white numbers**: Median of your metrics over the past 6 months')
    st.write('- **Small colored numbers**: Comparison in median of your metrics in the past 6 months over median in the past 12 months')
    st.divider()
    
    ## Display what matters; 10 of them.
    displayed_cols = ['video_publish_time', 'views', 'likes', 'subscribers',
        'shares', 'comments_added', 'rpm_in_usd', 'average_percentage_viewed',
        'average_duration_in_sec', 'engagement_ratio', 'views_per_sub_gained']     
        
    df_agg_metrics = df_agg[displayed_cols]
    
    metric_date_6mths     = df_agg_metrics['video_publish_time'].max() - pd.DateOffset(months=6)
    metric_date_12mths    = df_agg_metrics['video_publish_time'].max() - pd.DateOffset(months=12)
    
    metric_medians_6mths  = df_agg_metrics[df_agg_metrics['video_publish_time'] >= metric_date_6mths].median(numeric_only=True)
    metric_medians_12mths = df_agg_metrics[df_agg_metrics['video_publish_time'] >= metric_date_12mths].median(numeric_only=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]
    
    count = 0
    for i in metric_medians_6mths.index:
        with columns[count]:
            # Calculate median standard deviation between median prev 6 mths and prev 12 mths
            delta = (metric_medians_6mths[i] - metric_medians_12mths[i]) / metric_medians_12mths[i]
            st.metric(label=column_to_title(i), value=round(metric_medians_6mths[i], 1), delta="{:.2%}".format(delta))
            count += 1
            if count >= 5:
                count = 0
    
    df_agg_diff['publish_date'] = df_agg_diff['video_publish_time'].apply(lambda x: x.date())
    
    displayed_table_cols      = ['video_title', 'publish_date'] + displayed_cols[1:]
    df_agg_diff_final         = df_agg_diff.loc[:, displayed_table_cols]

    df_agg_diff_final.columns = df_agg_diff_final.columns.to_series().apply(lambda x: column_to_title(x))

    df_agg_numeric_lst = df_agg_diff_final.median(numeric_only=True).index.tolist()
    df_to_pct = {}
    for i in df_agg_numeric_lst:
        df_to_pct[i] = '{:.1%}'.format

    st.dataframe(df_agg_diff_final.style
        .applymap(style_negative, props='color: red')
        .applymap(style_positive, props='color: green')
        .format(df_to_pct))

    st.divider()
    
    st.subheader("Top 20 Videos by Performance")
    
    st.write("This section will see how videos first skyrocket--the clicks. \
             This could give insights in numerous areas: titles, thumbnails, intros, \
             early metrics to make your videos perform well and spread more.")
    
    st.write("The performance will be evaluated by displaying data as follows:")
    st.write("**Funneling Metrics**")
    st.write("    * **Thumbnail and Title**: First impression on what the video's about.")
    st.write("    * **Impressions**: How many times videos viewed on YT platform \
             -- suggested video box or homepage/search. *The higher the number, the larger the reach.*")
    st.write("    * **Impressions Click-Through Rate (CTR)**: The percentage of users that \
             see the impressions then clicking it after. *'I'm interested!'*")
    st.write("**Outputs**")
    st.write("    * **Retention**: How long users watch the video, both \
             as a whole (**Average Percentage Viewed**) and in average (**Average Duration in Sec**)")
    st.write("    * **Engagement Ratio**: Any interactions in video (Likes, dislikes, \
             comments, shares) per number of views (along with their individual blocks)")
    st.write("    * **Views per Sub Gained**: Added subscribers as your core audience through the video \
             per total viewers. *'Oh, I wanna see more contents like this!'*")

    df_agg_performance.columns = df_agg_performance.columns.to_series().apply(lambda x: column_to_title(x))
        
    st.data_editor(df_agg_performance, column_config={
        "Thumbnail": st.column_config.ImageColumn(
            "Thumbnail", help='Thumbnails of the Video')})
    
    # st.dataframe(df_agg_performance)
            
if add_sidebar == 'Individual Video Analysis':

    videos = tuple(df_agg['video_title'])    
    selected_video = st.selectbox('Pick A Video:', videos)
    
    agg_filtered        = df_agg[df_agg['video_title'] == selected_video]
    agg_sub_filtered    = df_agg_sub[df_agg_sub['video_title'] == selected_video] 
      
#    agg_sub_filtered['country'] = agg_sub_filtered['country_code'].apply(audience_simple)
#    agg_sub_filtered = agg_sub_filtered.sort_values('is_subscribed')
    
    ## Room for improvement: Take 10 top countries    
    agg_sub_filtered = agg_sub_filtered.sort_values(['is_subscribed', 'views'], ascending=False)
    top_10_country   = agg_sub_filtered['country_code'].head(10).to_list()
    agg_sub_filtered['country'] = (
        agg_sub_filtered['country_code'].apply(
            lambda x: code_to_country(x, top_10_country)))

    agg_sub_filtered = agg_sub_filtered.sort_values(['is_subscribed', 'views'])
    
    fig = px.bar(agg_sub_filtered, x='views', y='is_subscribed',
        color='country', orientation='h')
    st.plotly_chart(fig)
    
    agg_time_filtered = df_time_diff[df_time_diff['video_title'] == selected_video]
    first_30_days = agg_time_filtered[agg_time_filtered['days_published'].between(0, 30)]
    first_30_days = first_30_days.sort_values('days_published')
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x = views_cumulative['days_published'],
        y = views_cumulative['20pct_views'],
        mode = 'lines', name = '20th Percentile',
        line = dict(color='purple', dash='dash')))
    fig2.add_trace(go.Scatter(
        x = views_cumulative['days_published'],
        y = views_cumulative['median_views'],
        mode = 'lines', name = '50th Percentile',
        line = dict(color='lightgray', dash='dash')))
    fig2.add_trace(go.Scatter(
        x = views_cumulative['days_published'],
        y = views_cumulative['80pct_views'],
        mode = 'lines', name = '80th Percentile',
        line = dict(color='royalblue', dash='dash')))
    fig2.add_trace(go.Scatter(
        x = first_30_days['days_published'],
        y = first_30_days['views'].cumsum(),
        mode = 'lines', name = 'Current Video',
        line = dict(color='firebrick', width=8)))
    
    fig2.update_layout(
        title='View Comparison, First 30 Days',
        xaxis_title='Days since Published',
        yaxis_title='Cumulative Views')
    
    st.plotly_chart(fig2)