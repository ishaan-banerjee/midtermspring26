import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.title("FBI Wanted List — Exploratory Data Analysis")
st.header("Analysis of 1,138 records pulled from the FBI's public Wanted API.")

# data loading

@st.cache_data # store the data instead of running API call on every interaction
def load_data():
    all_records = []
    for page_number in range(1, 58):
        url = "https://api.fbi.gov/wanted/v1/list"
        params = {"page": page_number}
        response = requests.get(url, params=params)
        data = response.json()
        
        # add the page's 20 records to main list
        all_records.extend(data["items"])

    # convert to dataframe
    df = pd.DataFrame(all_records)

    # grab the first crime per person
    primary_crimes = []
    for value in df["subjects"]:
        if value:
            primary_crimes.append(value[0])
        else:
            primary_crimes.append("Unknown")
    df["primary_crime"] = primary_crimes

    # grab the first field office per person and capitalize it
    primary_offices = []
    for value in df["field_offices"]:
        if value:
            primary_offices.append(value[0].title())
        else:
            primary_offices.append("Unknown")
    df["primary_office"] = primary_offices

    df["primary_office"] = df["primary_office"].replace({
    "Newyork": "New York",
    "Washingtondc": "Washington D.C.",
    "Losangeles": "Los Angeles",
    "Sanfrancisco": "San Francisco",
    "Stlouis": "St. Louis"
    })

    # convert date to datetime
    df["publication"] = pd.to_datetime(df["publication"])

    # pull year into its own column
    df["year_posted"] = df["publication"].dt.year

    # create a yes/no column for whether the listing has a reward
    has_reward = []
    for value in df["reward_min"]:
        if value > 0:
            has_reward.append("Yes")
        else:
            has_reward.append("No")
    df["has_reward"] = has_reward

    # fill missing values with unknown and standardize text
    df["race"] = df["race"].fillna("Unknown")
    df["race"] = df["race"].str.lower()
    df["sex"] = df["sex"].fillna("Unknown")

    return df

df = load_data()

# sidebar filters

st.sidebar.header("Filters")

all_sexes = df["sex"].unique().tolist()
selected_sex = st.sidebar.multiselect("Sex", all_sexes, default=all_sexes)

all_races = df["race"].unique().tolist()
selected_race = st.sidebar.multiselect("Race", all_races, default=all_races)

year_min = int(df["year_posted"].min())
year_max = int(df["year_posted"].max())

selected_years = st.sidebar.slider("Year Posted", year_min, year_max, (year_min, year_max))
reward_filter = st.sidebar.selectbox("Has Reward?", ["All", "Yes", "No"])

# apply filters
filtered_df = df[df["sex"].isin(selected_sex)]
filtered_df = filtered_df[filtered_df["race"].isin(selected_race)]
filtered_df = filtered_df[filtered_df["year_posted"] >= selected_years[0]]
filtered_df = filtered_df[filtered_df["year_posted"] <= selected_years[1]]

if reward_filter != "All":
    filtered_df = filtered_df[filtered_df["has_reward"] == reward_filter]

st.sidebar.write(f"{len(filtered_df)} records match the selected filters")

# overview section

st.header("Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Listings", len(filtered_df))

with col2:
    with_reward_count = len(filtered_df[filtered_df["has_reward"] == "Yes"])
    st.metric("With Reward", with_reward_count)

with col3:
    num_crimes = len(filtered_df["primary_crime"].unique())
    st.metric("Crime Categories", num_crimes)

with col4:
    avg_reward = filtered_df["reward_min"].mean()
    st.metric("Avg Reward", f"${avg_reward:,.2f}")

st.divider()

# tabs

tab1, tab2, tab3, tab4 = st.tabs([
    "Crime Types",
    "Demographics",
    "Rewards",
    "Physical Profile",
])

# tab 1: crime types

with tab1:

    st.subheader("Top Crime Categories on the FBI Wanted List")
    crime_counts = filtered_df["primary_crime"].value_counts().head(15)
    
    fig = px.bar(x=crime_counts.values, y=crime_counts.index, orientation='h', labels={'x': 'Number of Listings', 'y': 'Crime Category'})
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    st.write("Seeking Information is the largest category, suggesting the FBI uses the list to solicit public tips. Cyber and counterintelligence cases are also prominent.")

    st.subheader("Listings Posted Per Year")
    yearly_counts = filtered_df["year_posted"].value_counts().sort_index()

    fig = px.line(x=yearly_counts.index, y=yearly_counts.values, labels={'x': 'Year', 'y': 'Number of Listings'})
    st.plotly_chart(fig, use_container_width=True)

    st.write("Listings have grown steadily, with notable spikes in cybercrime and counterintelligence years.")

    st.subheader("Top 15 FBI Field Offices by Number of Listings")
    office_counts = filtered_df["primary_office"].value_counts().head(15)

    fig = px.bar(x=office_counts.values, y=office_counts.index, orientation='h', labels={'x': 'Number of Listings', 'y': 'Field Office'})
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    st.write("New York and Washington D.C. dominate the list, which aligns with the prominence of counterintelligence and cyber cases.")

# tab 2: demographics

with tab2:

    st.subheader("Sex Distribution of FBI Wanted Individuals")
    sex_counts = filtered_df["sex"].value_counts()
    
    fig = px.pie(values=sex_counts.values, names=sex_counts.index, color_discrete_sequence=["steelblue", "lightpink", "lightgray", "lightyellow"])
    st.plotly_chart(fig, use_container_width=True)
    st.write("The list is overwhelmingly male.")

    st.subheader("Race Distribution of FBI Wanted Individuals")
    race_counts = filtered_df["race"].value_counts()
    
    fig = px.bar(x=race_counts.values, y=race_counts.index, orientation='h', labels={'x': 'Count', 'y': 'Race'})
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    st.write("White and Hispanic individuals make up the largest share of listings.")

    st.subheader("Top 10 Nationalities on the FBI Wanted List")
    nationality_counts = filtered_df["nationality"].value_counts().head(10)
    
    fig = px.bar(x=nationality_counts.values, y=nationality_counts.index, orientation='h', labels={'x': 'Number of Listings', 'y': 'Nationality'})
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    st.write("Americans are the largest group, but many listings involve foreign nationals, particularly from countries associated with counterintelligence cases like China and Iran.")

# tab 3: rewards

with tab3:

    st.subheader("Share of Listings with Rewards")
    reward_share = filtered_df["has_reward"].value_counts()
    
    fig = px.bar(x=reward_share.index, y=reward_share.values, labels={'x': 'Has Reward', 'y': 'Count'})
    st.plotly_chart(fig, use_container_width=True)
    st.write("Most listings do not include a reward.")

    st.subheader("Average Reward by Crime Category")
    reward_df = filtered_df[filtered_df["reward_min"] > 0]
    mean_reward = reward_df.groupby("primary_crime")["reward_min"].mean().sort_values()

    fig = px.bar(x=mean_reward.values, y=mean_reward.index, orientation='h', labels={'x': 'Average Reward ($)', 'y': 'Crime Category'})
    st.plotly_chart(fig, use_container_width=True)
    st.write("Criminal Enterprise and terrorism-related listings average $1M — the maximum reward offered.")

# tab 4: physical profile

with tab4:

    st.subheader("Height vs. Weight of FBI Wanted Individuals")
    hw_df = filtered_df[filtered_df["height_min"] < 85]
    hw_df = hw_df[hw_df["weight_min"] < 500]
    hw_df = hw_df[hw_df["height_min"].notna()]
    hw_df = hw_df[hw_df["weight_min"].notna()]

    fig = px.scatter(hw_df, x="height_min", y="weight_min", color="has_reward", 
                     labels={'height_min': 'Height (in)', 'weight_min': 'Weight (lbs)', 'has_reward': 'Has Reward'},
                     title="Height vs. Weight of FBI Wanted Individuals")
    st.plotly_chart(fig, use_container_width=True)
    st.write("The cluster between 60-75 inches and 140-220 lbs represents the typical adult male profile. Outliers with very low height/weight likely represent missing children cases.")

# raw data

st.header("Raw Data")
st.dataframe(filtered_df)
