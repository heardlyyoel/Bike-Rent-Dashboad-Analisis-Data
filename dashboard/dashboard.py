import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# Load data, using preprocessed data downloaded from notebook
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/heardlyyoel/Bike-Rent-Dashboad-Analisis-Data/master/dashboard/main_data.csv"
    df = pd.read_csv(url)
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df

df = load_data()


# Display logo
logo_url = "https://raw.githubusercontent.com//github.com/heardlyyoel/Bike-Rent-Dashboad-Analisis-Data/blob/master/dashboard/logo.jpeg"
st.sidebar.image(logo_url, width=150)

# Sidebar
st.sidebar.title("Filter Data")
year_filter = st.sidebar.multiselect("Select Year", options=[2011, 2012], default=[2011, 2012])
weather_filter = st.sidebar.multiselect("Select Weather Condition", options=df['weathersit'].unique(), default=df['weathersit'].unique())

# Filter dataframe (only for relevant visualizations)
filtered_df = df[(df['yr'].isin(year_filter)) & (df['weathersit'].isin(weather_filter))]

# Title
st.title("Bike Sharing Dashboard")
st.markdown("**Bike Rental Analysis (2011-2012)**")

# Introduction
st.markdown("""
    Welcome to the Bike Sharing Dashboard! This dashboard presents an analysis of bike rentals based on hourly data from 2011-2012.  
    You can explore the impact of weather, peak times, user type comparisons, and temperature categories on bike rentals.  
    Use the sidebar filters to customize the data in some visualizations. Enjoy exploring!
""")

# Tabs following the order of business questions
tab1, tab2, tab3, tab4 = st.tabs([
    "Weather Condition Impact", 
    "Peak and Low Rental Times", 
    "Casual vs Registered on Saturday in Fall", 
    "Temperature Category Impact"
])


with tab1:
    st.header("1. How does weather condition affect daily bike rentals in 2011 and 2012?")
    weather_group = filtered_df.groupby(['weathersit', 'yr'])['cnt'].agg(['mean']).reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='weathersit', y='mean', hue='yr', data=weather_group, palette=['skyblue', 'salmon'], ax=ax)
    ax.set_title('Average Bike Rentals by Weather Condition (2011 vs 2012)')
    ax.set_xlabel('Weather Condition')
    ax.set_ylabel('Average Rentals')
    ax.set_ylim(0, 350)
    ax.legend(title='Year')
    st.pyplot(fig)
    st.write(weather_group[['weathersit', 'yr', 'mean']])
    
    st.subheader("Insight:")
    max_weather = weather_group.loc[weather_group['mean'].idxmax()]
    min_weather = weather_group.loc[weather_group['mean'].idxmin()]
    years = weather_group['yr'].unique()
    trend = "upward" if len(years) > 1 and weather_group[weather_group['yr'] == years[-1]]['mean'].mean() > weather_group[weather_group['yr'] == years[0]]['mean'].mean() else "stable or downward"
    st.write(f"- The '{max_weather['weathersit']}' condition yields the highest rentals ({max_weather['mean']:.0f} in {max_weather['yr']}), "
             f"while '{min_weather['weathersit']}' has the lowest ({min_weather['mean']:.0f} in {min_weather['yr']}), "
             f"with an {trend} trend across all conditions based on the selected years.")

with tab2:
    st.header("2. At what hour (hr) and month (mnth) do bike rentals peak and drop the most?")
    pivot = filtered_df.pivot_table(index='hr', columns='mnth', values='cnt', aggfunc='mean')
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(pivot, cmap='YlGnBu', annot=True, fmt='.0f', linewidths=0.5, ax=ax)
    ax.set_title('Heatmap of Bike Rentals by Hour and Month')
    ax.set_xlabel('Month')
    ax.set_ylabel('Hour')
    st.pyplot(fig)
    max_hour_month = pivot.stack().idxmax()
    min_hour_month = pivot.stack().idxmin()
    
    st.subheader("Insight:")
    max_value = pivot.loc[max_hour_month[0], max_hour_month[1]]
    min_value = pivot.loc[min_hour_month[0], min_hour_month[1]]
    st.write(f"- Highest Rentals: Hour {max_hour_month[0]} in Month {max_hour_month[1]} ({max_value:.0f} rentals)")
    st.write(f"- Lowest Rentals: Hour {min_hour_month[0]} in Month {min_hour_month[1]} ({min_value:.0f} rentals)")
    st.write(f"- The highest rentals occur at {max_hour_month[0]}:00 in Month {max_hour_month[1]}, while the lowest are at {min_hour_month[0]}:00 in Month {min_hour_month[1]} based on the filtered data.")

with tab3:
    st.header("3. How do casual and registered user rentals compare on Saturdays in the Fall season of 2011 and 2012?")
    fall_sat_2011 = df[(df['season'] == 'Fall') & (df['weekday'] == 'Sat') & (df['yr'] == 2011)]  # No additional filtering
    fall_sat_2012 = df[(df['season'] == 'Fall') & (df['weekday'] == 'Sat') & (df['yr'] == 2012)]
    avg_2011 = [fall_sat_2011['casual'].mean(), fall_sat_2011['registered'].mean()]
    avg_2012 = [fall_sat_2012['casual'].mean(), fall_sat_2012['registered'].mean()]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(['Casual 2011', 'Registered 2011'], avg_2011, label='2011', color='skyblue')
    ax.bar(['Casual 2012', 'Registered 2012'], avg_2012, label='2012', color='salmon', alpha=0.7)
    ax.set_title('Average Rentals on Saturdays in Fall Season (2011 vs 2012)')
    ax.set_ylabel('Average Rentals')
    ax.set_ylim(0, 350)
    ax.legend(title='Year')
    st.pyplot(fig)
    
    st.subheader("Insight:")
    st.write(f"- Average Casual Rentals 2011: {avg_2011[0]:.2f}")
    st.write(f"- Average Registered Rentals 2011: {avg_2011[1]:.2f}")
    st.write(f"- Average Casual Rentals 2012: {avg_2012[0]:.2f}")
    st.write(f"- Average Registered Rentals 2012: {avg_2012[1]:.2f}")
    trend_2011_2012 = "significant increase" if avg_2012[1] > avg_2011[1] and avg_2012[0] > avg_2011[0] else "stable or decrease"
    dominance = "Registered users dominate" if avg_2011[1] > avg_2011[0] and avg_2012[1] > avg_2012[0] else "Casual users dominate"
    st.write(f"- {dominance} rentals on Saturdays in Fall, with a {trend_2011_2012} from 2011 to 2012.")

with tab4:
    st.header("4. How do temperature categories (Low, Medium, High) affect bike rentals in 2011 and 2012?")
    temp_group = filtered_df.groupby(['temp_category', 'yr'])['cnt'].agg(['mean']).reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='temp_category', y='mean', hue='yr', data=temp_group, palette=['skyblue', 'salmon'], ax=ax)
    ax.set_title('Average Bike Rentals by Temperature Category (2011 vs 2012)')
    ax.set_xlabel('Temperature Category')
    ax.set_ylabel('Average Rentals')
    ax.legend(title='Year')
    st.pyplot(fig)
    st.write(temp_group[['temp_category', 'yr', 'mean']])
    
    st.subheader("Insight:")
    max_temp = temp_group.loc[temp_group['mean'].idxmax()]
    min_temp = temp_group.loc[temp_group['mean'].idxmin()]
    years = temp_group['yr'].unique()
    trend = "increase" if len(years) > 1 and temp_group[temp_group['yr'] == years[-1]]['mean'].mean() > temp_group[temp_group['yr'] == years[0]]['mean'].mean() else "stable or decrease"
    st.write(f"- The '{max_temp['temp_category']}' temperature category has the highest rentals ({max_temp['mean']:.0f} in {max_temp['yr']}), "
             f"followed by 'Medium' and 'Low', with the lowest at '{min_temp['temp_category']}' ({min_temp['mean']:.0f} in {min_temp['yr']}), "
             f"and a trend of {trend} across all categories based on the selected years.")

st.markdown("""
---
**Created by Yoel Heardly Sirait**  
Email: yoelsirait05@gmail.com  
ID Dicoding: mc306d5y0653  
""")