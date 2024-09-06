# The Neighborhood Vibe Score

## Introduction

The purpose of this project is to develop a method to assign scores to neighborhoods that capture the neighborhood vibe, helping home buyers and renters make informed decisions.

This project was completed as a capstone for Constructor Academy's [data science bootcamp](https://academy.constructor.org/data-science/zurich). It was supervised by [Beate Brockmeier](https://www.linkedin.com/in/beate-brockmeier/), [Antonio Pipino](https://www.linkedin.com/in/antoniopipino/), Emmanouil Efthymio, and Michael Hofman from [Comparis](https://en.comparis.ch/), and mentored by [Ekaterina Butyugina](https://www.linkedin.com/in/ekaterina-butyugina/) and [Kunal Sharma](https://www.linkedin.com/in/drkunalsharma/) from Constructor Academy. The team, consisting of [Dashrath Reddy Kurli](https://www.linkedin.com/in/dashrath-reddy-kurli-520a952a4/), [Philippe Matter](https://www.linkedin.com/in/philippematter68/), and [Seckin Adali](https://www.linkedin.com/in/seckinadali/), created a system that provides free, comparable, and transparent metrics. This system enhances user engagement on Comparis by keeping comprehensive neighborhood information on-site.

A working prototype is available as a Streamlit app via [this link](https://neighborhoodvibescore.streamlit.app/).

![alt text](/docs/ScreenShot_Streamlit_better.jpg)

## Our Approach

To better reflect real-world accessibility, we defined the neighborhood as a 10-minute walking distance from a given real estate property address. Our data collection focused on various types of facilities within this defined area, including facility counts, average ratings, the proximity of the closest facilities and the population of the neighborhood.

Using normalization combined with a weighted sum, we assigned scores to neighborhoods. Our method provides two types of scores:
- **Personal Interests Score:** This score uses user preferences as input to assign weights in the weighted sum, providing a personalized neighborhood rating.
- **Neighborhood Vibe Score:** This score employs k-means clustering combined with descriptive statistics to determine weights, offering an automated and balanced approach to assigning scores.

Additionally, to capture the neighborhood vibe, we fed the collected data, along with the population and the actual location of the neighborhood, to an LLM (ChatGPT 3.5 turbo) to generate summary texts in different styles, for example reminiscent of a “real estate brochure”.

## Data Sources

We evaluated two primary data sources for gathering facility information:

- **OpenStreetMap (OSM):** Free and volunteer-sourced, OSM identified more facilities in urban areas but performed poorly in rural regions.

- **Google Places API:** A paid option that provided more consistent data across various areas, including facility ratings and the number of ratings, which were crucial for our scoring system.

After comparing both sources, we chose Google Places API for our prototype due to its consistency and the additional ratings data. Additionally, we collected population data from Swiss federal sources and integrated it into our dataset.

- The **population data** was sourced from the Swiss federal statistics bureau. Thanks to the very fine mesh of this geographical data, it was possible to estimate the population of the neighborhood (as opposed to the population of a specific administrative unit).

### Data Collection Process

- **Facility Data:** We wrote scripts to gather data from both Google Places API and OpenStreetMap. The Google Places API limited results to 20 per query, which we navigated using a next page token.

- **Data Limitations:** The results depended on the labeling of facilities by the data sources, which were not always consistent (e.g., hotels appearing in searches for kindergartens). For the prototype, we used eight facility types, with potential improvements from increasing this number. Also since no more than five text reviews per facility are available from Google Places API, we decided to focus on the ratings of each facility.

## Scoring Approach

Please refer to [score_calculation.pdf](docs/score_calculation.pdf) for a detailed explanation of the scoring process.

We developed two types of neighborhood scores for a given address. Both scores take into account facility counts, weighted average ratings, and travel times to the closest facilities for eight different facility types, using a weighted sum to determine the score. One method uses user input to decide on the weights, while the other automates the process by considering clusters across the entire dataset of addresses.

### Personal Interests Score
The user can input which facilities are important to them and provide information about their commute to work through a user-friendly interface on the Streamlit app (left sidebar). These preferences are adjusted as weights and used as coefficients in the weighted sum for the score. Additionally, using OpenRouteService and the Swiss Public Transport API, travel times to the specified workplace address, a defined maximum acceptable commute time, and the preferred means of travel are factored into the personal interests score, therefore returning a tailored score based on the user's preferences.

### Neighborhood Vibe Score
K-means clustering is applied to group the pool of all available addresses using all relevant data, including neighborhood population. The median of facility counts, adjusted by standard deviation, is then used to determine the weights for each facility type. These weights are applied in the weighted sum for the neighborhood score, ensuring an automated and balanced comparison between neighborhoods.

## APIs Used

- **Google Places API:** For facility data and ratings from Google.
- **Overpass API:** For facility data from OpenStreetMap.
- **OpenRouteService:** For calculating travel times.
- **Swiss Public Transport API:** For integrating public transportation data.
- **OpenAI (ChatGPT 3.5 turbo):** For generating neighborhood summary texts.

## Future Work and Improvements
- **Increasing Dataset Size:** Due to the expense of using Google APIs, we worked with only 7 addresses (i.e. 7 neighborhoods) within the free trial quota, selecting both urban and rural locations for variety. Increasing the number of addresses in the dataset would improve overall scores, as normalization and clustering benefit from a more varied and extensive dataset.
- **Using More Facility Types:** Expanding the number of facility types included in the scoring system to provide a more comprehensive view of the neighborhood. 
- **Crossing Data Sources:** Integrating data from both Google Places and OpenStreetMap to enhance data accuracy and coverage.
- **Detailed Facility Labels:** Taking advantage of Overpass API's and/or the new Google Places API's more detailed facility labels for more precise data categorization.
- **Integrating other types of data:** Quantitative data such as noise level data and internet coverage e.g. (available from Swiss federal sources) could also be be factored in the scores, allowing the user to further refine the search.
- **Adapted Neighborhood Definitions:** Adjusting the definition of a neighborhood for suburban and rural areas to better reflect realistic accessibility (e.g. 15 minutes by public transportation rather than 10 minutes on foot) .