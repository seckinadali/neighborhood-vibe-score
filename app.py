import os
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

from src.app_helper_functions import (
    load_data, 
    extract_address_from_path,
    create_base_map,
    add_original_address,
    add_places,
    add_isochrone,
    add_population,
    plot_facility_counts
)

from src.assign_scores import assign_custom_scores, assign_cluster_scores

# Constants
TIME_BOUND = 10  # minutes
DATA_DIRECTORY = "data/google_data_isochrone_pop_cgpt"
PAGE_TITLE = "Comparis Neighborhood Vibe Score"

# Setup
st.set_page_config(page_title=PAGE_TITLE, layout="wide")
st.title(PAGE_TITLE)
st.markdown("<br>", unsafe_allow_html=True)

# Helper functions
def get_file_names(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.json')]

def create_property_map(files):
    return {i+1: {'PROPERTY': file, 'address': extract_address_from_path(file)} for i, file in enumerate(files)}


# Load data
FILES = get_file_names(DATA_DIRECTORY)
property_map = create_property_map(FILES)

# Sidebar
st.sidebar.subheader('Personal interests')

weights = {
    'Balanced': {
        'gym_fitness': 5,
        'public_transportation': 5,
        'schools': 5,
        'kindergarten': 5,
        'bars': 5,
        'restaurants': 5,
        'gas_ev_charging': 5,
        'grocery_stores_supermarkets': 5
    },
    'Infrastructure': {
        'gym_fitness': 3,
        'public_transportation': 8,
        'schools': 7,
        'kindergarten': 6,
        'bars': 2,
        'restaurants': 4,
        'gas_ev_charging': 6,
        'grocery_stores_supermarkets': 8
    },
    'Entertainment': {
        'gym_fitness': 4,
        'public_transportation': 7,
        'schools': 1,
        'kindergarten': 1,
        'bars': 10,
        'restaurants': 10,
        'gas_ev_charging': 6,
        'grocery_stores_supermarkets': 3
    },
    'Services': {
        'gym_fitness': 5,
        'public_transportation': 8,
        'schools': 7,
        'kindergarten': 6,
        'bars': 2,
        'restaurants': 4,
        'gas_ev_charging': 6,
        'grocery_stores_supermarkets': 8
    }
}

weights_preset_id = st.sidebar.selectbox('Choose a preset for facility importance:', list(weights.keys()), key='weights_preset_id')

weights['Custom'] = {key: st.sidebar.slider(key, min_value=0, max_value=10, value=weights[weights_preset_id][key]) for key in weights[weights_preset_id]}

weights_normalized = {key: {k: v / sum(sub_dict.values()) for k, v in sub_dict.items()} for key, sub_dict in weights.items()}

# Layers
st.sidebar.subheader('Layers')
facilities_layer = st.sidebar.checkbox('Facilities', value=True)
isochrones_walking = st.sidebar.checkbox('Walking distances', value=True)
population_layer = st.sidebar.checkbox('Population data points', value=False)

# Main page
col1, col2, _ = st.columns([1, 2, 2])
col1.subheader('Select an address:')
property_id = col2.selectbox('', list(range(1, len(FILES)+1)), format_func=lambda x: property_map[x]['address'], label_visibility="collapsed", key='property_id')

# Load selected property data
selected_property = property_map[property_id]
PROPERTY = load_data(selected_property['PROPERTY'])

# Create map
base_map = create_base_map(PROPERTY, 800, 800, 14)
if isochrones_walking:
    add_isochrone(base_map, PROPERTY)
if population_layer:
    add_population(base_map, PROPERTY)
if facilities_layer:
    add_places(base_map, PROPERTY, 15)
add_original_address(base_map, PROPERTY)

base_map.update_layout(
    margin=dict(r=0, t=0, l=0, b=0),
    showlegend=True,
    legend=dict(
        title=dict(text="Facilities", font=dict(size=17, color='black')),
        yanchor="top", y=0.99, xanchor="left", x=0.01,
        font=dict(size=15, color="black"),
        bgcolor="white"
    )
)

# Display map and neighborhood info
col_map, col_info = st.columns([3, 1])
col_map.plotly_chart(base_map, use_container_width=True)
col_info.subheader('About the neighborhood')
col_info.write(PROPERTY['text_description']['neutral without emphasis']['text'])

# Neighborhood Vibe Score
col_info.subheader('Neighborhood Vibe Score')
neighborhood_score_placeholder = col_info.empty()

# Facility counts and Personal interests score
col_facilities, _, col_personal = st.columns([9, 1, 3])
col_facilities.subheader(f"Facilities within a {TIME_BOUND}-minute walk")
col_facilities.pyplot(plot_facility_counts(PROPERTY), use_container_width=True)

col_personal.subheader('Personal interests score')
personal_score_placeholder = col_personal.empty()

# Calculate scores
scores = assign_cluster_scores(DATA_DIRECTORY)
scores.rename(columns={'cluster_score': 'Neighborhood Vibe Score'}, inplace=True)

for category in weights_normalized:
    if category != 'Balanced':
        category_scores = assign_custom_scores(DATA_DIRECTORY, weights_normalized[category])
        category_scores.rename(columns={'custom_score': category}, inplace=True)
        scores = scores.merge(category_scores, on='address')

scores.rename(columns={'Custom': 'Personal Interests Score'}, inplace=True)

# Plot scores
property_scores = scores.iloc[property_id-1][1:]

def plot_score(score_values, score_index, color, ax):
    bar = sns.barplot(x=score_values.index[score_index:score_index+1], y=score_values.values[score_index:score_index+1], ax=ax, color=color)
    bar.bar_label(bar.containers[0], fontweight='bold')
    ax.set(xlabel='', ylabel='', ylim=(0, 100), xticks=[])
    return fig

# Neighborhood Vibe Score
fig, ax = plt.subplots(figsize=(1.5, 2))
plot_score(property_scores, 0, '#66cc00', ax)
neighborhood_score_placeholder.pyplot(fig, use_container_width=False)

# Personal Interests Score
fig, ax = plt.subplots(figsize=(1, 1.5))
plot_score(property_scores, 4, '#017b4f', ax)
personal_score_placeholder.pyplot(fig, use_container_width=False)

# Data sources
st.divider()
st.subheader('Data sources')
st.markdown('[Isochrones for reachability by foot and travel times](https://openrouteservice.org/dev/#/api-docs/v2/isochrones/{profile}/post)')
st.markdown('[Population data](https://www.geocat.ch/geonetwork/srv/eng/catalog.search#/metadata/4bfbbf20-d90e-4131-8fe2-4c454ad45c16)')
st.markdown('[Travel time with public transports](https://transport.opendata.ch/)')