# midtermspring26
Data Bootcamp Midterm Spring '26

# FBI Wanted List — Exploratory Data Analysis

## Overview

This project conducts an exploratory data analysis of the FBI's public Wanted List, using data pulled directly from the FBI's open Wanted API. The central question guiding this analysis is: **what patterns exist in the demographics, crime types, and reward structures of individuals on the FBI Wanted List?**

The FBI Wanted List is a publicly available database of individuals wanted by the Federal Bureau of Investigation for a wide range of offenses, from violent crime to cybercrime to counterintelligence. While the list is widely known to the public, the patterns within it are less understood. This project uses data science tools to surface those patterns and present them in a clear, reproducible way.

---

## Data Source

Data was pulled directly from the FBI's public API at `https://api.fbi.gov/wanted/v1/list`. The API returns 20 records per page. We looped through all 57 pages to collect all **1,138 available records** at the time of collection.

Each record contains a wide range of fields, including the individual's name, sex, race, nationality, height, weight, field office, subjects (crime categories), publication date, and reward information. For this analysis, we focused on the following features:

| Feature | Description |
|---|---|
| `subjects` | Crime categories associated with each listing |
| `sex` | Sex of the individual |
| `race` | Race of the individual |
| `nationality` | Nationality of the individual |
| `publication` | Date the listing was posted |
| `field_offices` | FBI field office associated with the listing |
| `reward_min` | Minimum reward offered for information |
| `height_min` | Minimum height of the individual (inches) |
| `weight_min` | Minimum weight of the individual (pounds) |

---

## Data Cleaning

Several columns required cleaning before analysis could begin:

- **`subjects` and `field_offices`** — Each contained lists rather than single values, so we extracted the first value from each to create `primary_crime` and `primary_office` columns.
- **Field office names** — Values were capitalized using Python's `.title()` string method, and a known formatting issue (`"Newyork"`) was corrected to `"New York"`, along with other multi-city names that had formatting issues.
- **`publication`** — Stored as a string and converted to a `datetime` object using pandas, allowing us to extract the year each listing was posted into a new `year_posted` column.
- **`has_reward`** — A new binary column was created to flag whether each listing included a reward offering, defined as a `reward_min` value greater than zero.
- **Missing values** — Missing values in the `race` and `sex` columns were filled with `"Unknown"` to avoid dropping rows unnecessarily. Race values were also standardized to lowercase to ensure consistent grouping.

---

## Analysis

### What types of crimes are most represented on the FBI Wanted List?

The most common crime category on the list is "Seeking Information," which accounts for a large share of all listings. This finding is perhaps the most surprising result of the analysis: it suggests that the FBI uses the Wanted List as a public engagement tool to solicit tips from the public on a wide range of cases. This way, the FBI can utilize public awareness to generate leads that would have otherwise been difficult to obtain through traditional investigation. 

Following Seeking Information, the next most common categories are "Cyber's Most Wanted" and "ViCAP Missing Persons." The prominence of cybercrime reflects the FBI's growing focus on digital offenses in recent years. Traditional violent crime categories are present on the list but represent a smaller share than many people might expect. The growing prominence of cybercrime reflects a broader change in the nature of crime, as cyber offenses have much broader reach. They can involve infrastructure and victims across international borders, so this added layer of complexity makes public awareness particularly valuable. 

---

### Who is on the FBI Wanted List?

The list is overwhelmingly male, with female listings representing a very small percentage of the total. A small number of listings have no sex recorded, likely due to incomplete or unknown profiles.

In terms of race, White and Hispanic individuals make up the largest share of listings. It is important to note that race data is missing for a significant portion of records, which limits the conclusions that can be drawn from this analysis.

---

### Where are wanted individuals from?

American nationals represent the largest group on the list by a significant margin. However, a substantial number of listings involve foreign nationals. The growing presence of internationals on the list reflects the increasingly international nature of modern crimes. Numerous crimes investigated by the FBI today (particularly cybercrime and counterintelligence) involve cross border operations and agents operating outside of the United States. 

Countries particularly well represented include China and Iran, which aligns with the prominence of counterintelligence cases on the list. This finding is consistent with publicly known FBI priorities around foreign espionage and economic theft. U.S. officials have frequently raised concerns about cybersecurity, IP theft, and other activities involving foreign intelligence. The presence of these countries reflects wider geopolitical tensions.

---

### Has the FBI Wanted List grown over time?

The number of new listings posted per year has grown steadily since 2010, the earliest year in the dataset. There is a notable increase in listings in more recent years, which likely reflects the FBI's expanded focus on cybercrime and counterintelligence. The spike in early years of the dataset may also reflect the initial digitization of existing cases when the API was first launched, rather than a true increase in new wanted individuals.

---

### What factors are associated with higher rewards?

The majority of listings on the FBI Wanted List do not include any reward. Rewards appear to be reserved for high-priority cases, particularly those related to national security.

| Crime Category | Avg. Reward |
|---|---|
| Criminal Enterprise Investigations | $1,000,000 |
| Seeking Information - Terrorism | $1,000,000 |
| Most Wanted Terrorists | ~$900,000 |
| Counterintelligence | ~$500,000 |
| Violent Crime / Missing Persons | Minimal or none |

Among listings that do include a reward, the average reward varies significantly by crime category. "Criminal Enterprise Investigations" and "Seeking Information - Terrorism" both average the maximum reward of $1,000,000. "Most Wanted Terrorists" follow closely at around $900,000, and "Counterintelligence" cases average around $500,000. By contrast, categories like violent crime and missing persons carry minimal or no rewards, suggesting that reward amounts are tied to national security priority rather than the severity of individual crimes. 

This reflects how the FBI prioritizes different types of investigations. Because rewards are mostly reserved for crimes related to national security, this implies that the FBI may heavily rely on tips from the public sector in these cases. Crimes of this nature, like terrorism or counterintelligence, often involve suspects who are difficult to locate and operate within international networks or other protected environments. These complex situations can be difficult for traditional investigations to penetrate. In such cases, potential witnesses may fear retaliation or may not realize the significance of their information. Thus, by offering large rewards, the FBI is able to increase the likelihood of securing a crucial tip. 

---

### What does a typical wanted individual look like physically?

For listings that include physical profile data, the distribution of height and weight clusters strongly between **60–75 inches tall** and **140–220 pounds**, consistent with the profile of an average adult male. A small number of outliers with very low height and weight values likely represent missing children cases rather than data errors, though some extreme outliers were filtered out as likely data entry mistakes.

---

### Which FBI field offices handle the most wanted listings?

The New York field office accounts for the largest share of listings by a significant margin, with San Diego and Washington D.C. also appearing prominently. This geographic distribution is consistent with the types of cases that dominate the list. Cybercrime and counterintelligence investigations are naturally concentrated in major metropolitan hubs, while border offices like San Diego reflect the prevalence of narcoterrorism and criminal enterprise cases involving cross-border networks. Along with the nationality findings, this reinforces the idea that the FBI Wanted List skews heavily toward cases with international ties.

---

## Limitations

Several limitations should be noted when interpreting these results.

First, missing data is a significant issue across many columns. Race, nationality, height, and weight are all missing for a substantial portion of records. This means that demographic findings in particular should be interpreted with caution, as the patterns observed may not reflect the full picture.

Second, the data represents only the current state of the FBI Wanted List at the time of collection. Individuals who have been apprehended and removed from the list are not included, which means the dataset may skew toward longer-running or harder-to-solve cases.

Third, the primary_crime field used in this analysis is simply the first crime category listed for each individual. Some individuals are associated with multiple categories, and by taking only the first we may be undercounting certain crime types.

Finally, the FBI Wanted List is not a random or representative sample of all criminal activity in the United States. Because it encompasses the crimes that the FBI chooses to publicly highlight, it reflects institutional priorities and is not an objective representation of crime prevalence. Because of this, certain cases may be over or underrepresented. This dataset is a representation of how the FBI chooses to communicate and prioritize investigations, not a representative sample of all criminal activity. This means it should not be used to draw broader conclusions about crime rates or demographics in the general population.

---

## Conclusion


The FBI Wanted List is a richer and more nuanced dataset than it might first appear. Rather than simply being a list of dangerous fugitives, it functions as a broad public engagement tool. The list is dominated by male individuals, with White and Hispanic individuals making up the largest racial groups. Reward amounts are concentrated in national security cases, with terrorism and counterintelligence listings commanding the highest rewards. Physical profile data clusters around a typical adult male range, consistent with the demographic composition of the list. The New York field office handles the most listings, followed by San Diego and Washington D.C.

This analysis demonstrates the value of publicly available government data for understanding institutional priorities and patterns. The code and data used in this project are fully reproducible using the FBI's public API and the steps described in this document.

---

## References

- FBI Wanted API: https://api.fbi.gov/wanted/v1/list
- FBI Wanted List public website: https://www.fbi.gov/wanted
- Python libraries used: `pandas`, `seaborn`, `matplotlib`, `requests`
