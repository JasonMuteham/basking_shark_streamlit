import streamlit as st
import pandas as pd
import plotly.express as px
from OSGridConverter import grid2latlong
import pydeck as pdk


st.set_page_config(
    page_title="Basking Sharks Dashboard",
    page_icon="🐋",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/JasonMuteham',
        'Report a bug': "https://github.com/JasonMuteham",
        'About': "# Basking Sharks\n\nNumber crunching!"
    }
)

"""
# Basking Sharks #

## Where to spot them in West Scotland ##

Analysis by [Jason Muteham](https://github.com/JasonMuteham) 
"""
# Create df group by OSGbin
@st.cache_data
def OSGbiner(OSGbin):
  df_tmp = dw.groupby([OSGbin,'Common name'])['Individual count'].sum()
  df_tmp = df_tmp.reset_index()
  df_tmp = df_tmp.pivot_table(index=OSGbin, values='Individual count', columns='Common name')
  df_tmp = df_tmp.fillna(0)
  df_tmp['Total'] = df_tmp.agg('sum', axis=1)
  df_tmp = df_tmp.sort_values(by='Total')
  return df_tmp

import_file = 'data/Basking_Sharks.csv'
name = "Basking Shark"
# Which OS bins to use for the maps
ll_OSGbin = 'OSG 1km'
#"open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner" or "stamen-watercolor"  # noqa: E501
px_map_tiles = 'carto-darkmatter'
#px_map_tiles = 'stamen-terrain'
mg = dict(l=0, r=20, b=20, t=10)

dw = pd.read_csv(import_file, parse_dates=["Date"])

tab1, tab2, tab3 = st.tabs(["About", "Charts", "Maps"])

with tab1:

    st.image('images/basking_shark.jpg')
             
    """
Questions answered in this report 

- How many Basking sharks have been observed by the Hebridean Whale and Dolphin Trust?
- Where is the best location to see Basking sharks?

--- 

[**Hebridean Whale and Dolphin Trust**](https://www.hwdt.org)

Based on the Isle of Mull, in the heart of the Hebrides, HWDT has been leading the way for the conservation of whales, dolphins and porpoises in the waters of western Scotland for over two decades.

We believe evidence is the foundation of effective conservation. Our research has critically advanced the understanding of species that visit seasonally or are resident in the Hebrides. Data are provided to the Scottish Government to inform protection measures for minke whales, Risso’s dolphins, harbour porpoises, and basking sharks across Hebridean seas.

---

Data provided by the following providers:

Records provided by Hebridean Whale and Dolphin Trust, accessed through NBN Atlas website. (2022). For more information: email info@hwdt.org, or https://registry.nbnatlas.org/public/show/dp81

Hebridean Whale and Dolphin Trust (2022). Visual sightings data set 2003-2021. Occurrence dataset on the NBN Atlas (Creative Commons, with Attribution, Non-commercial v4.0 (CC-BY-NC) CC-BY-NC). For more information: email biodiversityofficer@hwdt.org, or https://registry.nbnatlas.org/public/show/dr537

---
    """

with tab2:
    """
    ## Q. How many Basking sharks have been observed by HWDT?
---
    """

    fig = px.bar(dw.query('`Common name` == "Basking Shark"').groupby('Date year')['Individual count'].agg('sum'),
    y='Individual count', title= 'The number of ' + name + "s spotted each year", text_auto=True,)
    fig.update_layout(yaxis_title='Count of ' + name + 's', xaxis_title='', showlegend=False)
    fig.update_traces(hovertemplate=' Year %{x}, %{y} spotted',marker_line_color='darkgreen', marker_line_width=1.0)
    st.plotly_chart(fig, use_container_width=True)

    """
    ---

**A.** A total of **1979** Basking Sharks have been observed by the HWDT between 2003 & 2021.

The peak year for sightings was **2010** there has been a sharp decline in observation since **2016**. As the HWDT collects observation from members of the public COVID-19 restrictions could play a part in the **2020 & 2021** figures. 


---
    """

with tab3:
    """
    ## Q. Where is the best location to see Basking sharks?
    ---
    """
    st.subheader('Heat map of Basking Shark observations between 2003-2021')
    fig = px.density_mapbox(dw, lat='Latitude',lon='Longitude', z='Individual count', 
    radius=20, center=dict(lat=56.5, lon=-6.5), color_continuous_scale='blues_r', zoom=6, mapbox_style=px_map_tiles,
    height=500)
    fig.update_coloraxes(cmax=30, cmin=1, showscale=False)
    fig.update_layout(margin=mg)
    fig.update_traces(hovertemplate='%{z} Basking Sharks') 
    st.plotly_chart(fig, use_container_width=True)

    # Build Low level plot data
    df_bin = OSGbiner(ll_OSGbin)
    dw_plot = df_bin.loc[df_bin[name] > 0][[name]]
    dw_plot.columns = ["Total"]
    max_osgrid = dw_plot.loc[dw_plot['Total'].max()==dw_plot['Total']].reset_index().iloc[0,0]
    lats = []
    longs = []
    for idx in dw_plot.index:
        lalo = grid2latlong(idx)
        lats.append(lalo.latitude)
        longs.append(lalo.longitude)
    dw_plot['Latitude'] = lats
    dw_plot['Longitude'] = longs
    dw_plot_low = dw_plot.copy()

    # Plotly Bubble Map

    st.subheader('Basking Shark hot spots 2003-2021')
    view = pdk.data_utils.compute_view(dw_plot_low[["Longitude", "Latitude"]])
    view.pitch = 70
    view.bearing = 340
    view.zoom = 8.5

    st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state = view,
    tooltip={
        'html': '<b>Total Basking Sharks spotted:</b> {Total}',
        'style': {'color': 'white'}
    },
    layers=[
        pdk.Layer(
           'ColumnLayer',
           data=dw_plot_low,
           get_position=["Longitude", "Latitude"],
           radius=400,
           get_elevation="Total",
           elevation_scale=100,
           get_fill_color=["Total * 10", "100", "100 + (Total * 20)", 200],
           pickable=True,
           autohighlight=True           
        )
    ],))

    """
    ---

**A.** The majority of Basking Shark observations have been made in the waters around the islands of **Col** and **Tiree**, which would suggest that these islands would be a good starting place to encounter Basking Sharks.

---
    """