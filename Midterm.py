import streamlit as st
import pandas as pd
import requests
import seaborn as sns
import matplotlib.pyplot as plt

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

# filters

st.header("Filters")

all_sexes = df["sex"].unique().tolist()
selected_sex = st.multiselect("Sex", all_sexes, default=all_sexes)

all_races = df["race"].unique().tolist()
selected_race = st.multiselect("Race", all_races, default=all_races)

year_min = df["year_posted"].min()
year_max = df["year_posted"].max()

selected_years = st.slider("Year Posted", year_min, year_max, (year_min, year_max))
reward_filter = st.selectbox("Has Reward?", ["All", "Yes", "No"])

# apply filters
filtered_df = df[df["sex"].isin(selected_sex)]
filtered_df = filtered_df[filtered_df["race"].isin(selected_race)]
filtered_df = filtered_df[filtered_df["year_posted"] >= selected_years[0]]
filtered_df = filtered_df[filtered_df["year_posted"] <= selected_years[1]]

if reward_filter != "All":
    filtered_df = filtered_df[filtered_df["has_reward"] == reward_filter]

st.write(f"{len(filtered_df)} records match the selected filters")

# summary metrics

total = len(filtered_df)
st.write(f"Total Listings: {total}")

with_reward = filtered_df[filtered_df["has_reward"] == "Yes"]
st.write(f"With Reward: {len(with_reward)}")

unique_crimes = filtered_df["primary_crime"].unique()
num_crimes = len(unique_crimes)
st.write(f"Crime Categories: {num_crimes}")

avg_reward = round(filtered_df["reward_min"].mean(), 2)
st.write(f"Avg Reward: ${avg_reward}")

# tabs

tab1, tab2, tab3, tab4 = st.tabs([
    "Crime Types",
    "Demographics",
    "Rewards",
    "Physical Profile",
])

# tab 1: crime types

with tab1:

    # count how many times each crime appears, keep + plot top 15 categories
    st.subheader("Top Crime Categories on the FBI Wanted List")
    crime_counts = filtered_df["primary_crime"].value_counts()
    crime_counts = crime_counts.head(15)

    fig, ax = plt.subplots()
    sns.barplot(x=crime_counts.values, y=crime_counts.index, ax=ax)
    ax.set_xlabel("Number of Listings")
    ax.set_ylabel("Crime Category")
    st.pyplot(fig)

    st.write("Seeking Information is the largest category, suggesting the FBI uses the list to solicit public tips. Cyber and counterintelligence cases are also prominent.")

    # count how many new listings per year and plot
    st.subheader("Listings Posted Per Year")
    yearly_counts = filtered_df["year_posted"].value_counts()
    yearly_counts = yearly_counts.sort_index()

    fig, ax = plt.subplots()
    sns.lineplot(x=yearly_counts.index, y=yearly_counts.values)
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Listings")
    st.pyplot(fig)

    st.write("Listings have grown steadily, with notable spikes in cybercrime and counterintelligence years.")

    # count how many listings each field office has and plot top 15
    st.subheader("Top 15 FBI Field Offices by Number of Listings")
    office_counts = filtered_df["primary_office"].value_counts().head(15)

    fig, ax = plt.subplots()
    sns.barplot(x=office_counts.values, y=office_counts.index, ax=ax)
    ax.set_xlabel("Number of Listings")
    ax.set_ylabel("Field Office")
    st.pyplot(fig)
    st.write("New York and Washington D.C. dominate the list, which aligns with the prominence of counterintelligence and cyber cases.")

# tab 2: demographics

with tab2:

    # count how many of each sex are on the list + plot
    st.subheader("Sex Distribution of FBI Wanted Individuals")
    sex_counts = filtered_df["sex"].value_counts()
    fig, ax = plt.subplots()
    ax.pie(sex_counts, labels=sex_counts.index, autopct="%1.1f%%", colors=["steelblue", "lightpink", "lightgray", "lightyellow"])
    st.pyplot(fig)
    st.write("The list is overwhelmingly male.")

    # count how many ppl of each race are on the list + plot
    st.subheader("Race Distribution of FBI Wanted Individuals")
    race_counts = filtered_df["race"].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=race_counts.values, y=race_counts.index, ax=ax)
    ax.set_xlabel("Count")
    ax.set_ylabel("Race")
    st.pyplot(fig)
    st.write("White and Hispanic individuals make up the largest share of listings.")

    # count how many ppl from each country, keep top 10
    st.subheader("Top 10 Nationalities on the FBI Wanted List")
    nationality_counts = filtered_df["nationality"].value_counts()
    nationality_counts = nationality_counts.head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=nationality_counts.values, y=nationality_counts.index)
    ax.set_xlabel("Number of Listings")
    ax.set_ylabel("Nationality")
    st.pyplot(fig)
    st.write("Americans are the largest group, but many listings involve foreign nationals, particularly from countries associated with counterintelligence cases like China and Iran.")

# tab 3: rewards

with tab3:

    st.subheader("Share of Listings with Rewards")
    reward_share = filtered_df["has_reward"].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=reward_share.index, y=reward_share.values)
    ax.set_xlabel("Has Reward")
    ax.set_ylabel("Count")
    st.pyplot(fig)
    st.write("Most listings do not include a reward.")

    # only keep rows where a reward is offered
    # calculate average reward for each crime type
    st.subheader("Average Reward by Crime Category")
    reward_df = filtered_df[filtered_df["reward_min"] > 0]
    mean_reward = reward_df.groupby("primary_crime")["reward_min"].mean()
    mean_reward = mean_reward.sort_values()

    fig, ax = plt.subplots()
    sns.barplot(x=mean_reward.values, y=mean_reward.index)
    ax.set_xlabel("Average Reward ($)")
    ax.set_ylabel("Crime Category")
    st.pyplot(fig)
    st.write("Criminal Enterprise and terrorism-related listings average $1M — the maximum reward offered.")

# tab 4: physical profile

with tab4:

    # only keep rows with realistic height and weight
    st.subheader("Height vs. Weight of FBI Wanted Individuals")
    hw_df = filtered_df[filtered_df["height_min"] < 85]
    hw_df = hw_df[hw_df["weight_min"] < 500]
    hw_df = hw_df[hw_df["height_min"].notna()]
    hw_df = hw_df[hw_df["weight_min"].notna()]

    fig, ax = plt.subplots()
    sns.scatterplot(data=hw_df, x="height_min", y="weight_min", hue="has_reward", ax=ax)
    ax.set_xlabel("Height (in)")
    ax.set_ylabel("Weight (lbs)")
    ax.set_title("Height vs. Weight of FBI Wanted Individuals")
    st.pyplot(fig)
    st.write("The cluster between 60-75 inches and 140-220 lbs represents the typical adult male profile. Outliers with very low height/weight likely represent missing children cases.")

# raw data

st.header("Raw Data")
st.dataframe(filtered_df)