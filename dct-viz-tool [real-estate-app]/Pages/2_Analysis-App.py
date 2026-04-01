import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.family'] = 'DejaVu Sans'  # suppress Arial warning

st.set_page_config(page_title="Plotting Demo")
st.title('Analytics')

new_df = pd.read_csv('datasets/data_viz1.csv')
feature_text = pickle.load(open('datasets/feature_text.pkl', 'rb'))

# ── Geomap ──────────────────────────────────────────────────────────────────
group_df = new_df.groupby('sector')[['price', 'price_per_sqft', 'built_up_area', 'latitude', 'longitude']].mean()
group_df = group_df.reset_index()  # only once, keeps 'sector' as a column

# Normalize bubble size to 5–40
group_df['bubble_size'] = (
    (group_df['built_up_area'] - group_df['built_up_area'].min()) /
    (group_df['built_up_area'].max() - group_df['built_up_area'].min())
) * 35 + 5

st.header('Sector Price per Sqft Geomap')

fig = go.Figure(go.Scattermapbox(
    lat=group_df['latitude'],
    lon=group_df['longitude'],
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=group_df['bubble_size'],
        color=group_df['price_per_sqft'],
        colorscale='IceFire',
        showscale=True,
        colorbar=dict(title='Price/sqft'),
        sizemode='diameter',
        opacity=0.8
    ),
    text=group_df['sector'],
    hovertemplate="<b>%{text}</b><br>Price/sqft: %{marker.color:.0f}<extra></extra>"
))

fig.update_layout(
    mapbox=dict(
        style='open-street-map',
        center=dict(lat=group_df['latitude'].mean(), lon=group_df['longitude'].mean()),
        zoom=10
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    width=1200,
    height=700
)

st.plotly_chart(fig, use_container_width=True)

# ── Wordcloud ────────────────────────────────────────────────────────────────
st.header('Features Wordcloud')

wordcloud = WordCloud(
    width=800, height=800,
    background_color='black',
    stopwords=set(['s']),
    min_font_size=10
).generate(feature_text)

fig_wc, ax_wc = plt.subplots(figsize=(8, 8))
ax_wc.imshow(wordcloud, interpolation='bilinear')
ax_wc.axis("off")
plt.tight_layout(pad=0)
st.pyplot(fig_wc)          # pass figure explicitly (avoids deprecation warning)

# ── Area vs Price ────────────────────────────────────────────────────────────
st.header('Area Vs Price')

property_type = st.selectbox('Select Property Type', ['flat', 'house'])

fig1 = px.scatter(
    new_df[new_df['property_type'] == property_type],
    x="built_up_area", y="price",
    color="bedRoom",
    title="Area Vs Price"
)
st.plotly_chart(fig1, use_container_width=True)

# ── BHK Pie Chart ────────────────────────────────────────────────────────────
st.header('BHK Pie Chart')

sector_options = ['overall'] + sorted(new_df['sector'].unique().tolist())
selected_sector = st.selectbox('Select Sector', sector_options)

pie_data = new_df if selected_sector == 'overall' else new_df[new_df['sector'] == selected_sector]
fig2 = px.pie(pie_data, names='bedRoom')
st.plotly_chart(fig2, use_container_width=True)

# ── BHK Box Plot ─────────────────────────────────────────────────────────────
st.header('Side by Side BHK price comparison')

fig3 = px.box(new_df[new_df['bedRoom'] <= 4], x='bedRoom', y='price', title='BHK Price Range')
st.plotly_chart(fig3, use_container_width=True)

# ── Distplot ─────────────────────────────────────────────────────────────────
st.header('Side by Side Distplot for property type')

fig4, ax = plt.subplots(figsize=(10, 4))
sns.histplot(new_df[new_df['property_type'] == 'house']['price'], kde=True, label='House', ax=ax)
sns.histplot(new_df[new_df['property_type'] == 'flat']['price'], kde=True, label='Flat', ax=ax)
ax.set_xlabel('Price')
ax.legend()
st.pyplot(fig4)









