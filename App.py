import asyncio
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import streamlit as st
import geopandas as gpd
import folium
from shapely.geometry import LineString
from streamlit_folium import st_folium

st.set_page_config(page_title="Tourism Route Planner", layout="centered")
st.title("🗺️ Tourism Route Planner")

# --- User Inputs ---
st.subheader("Trip Preferences")

selected_categories = st.multiselect(
    "Select site categories",
    options=['Adventure', 'Culture', 'Nature', 'Services', 'Sustainability']
)

start_city = st.selectbox(
    "Select starting city",
    options=[
        'Jeddah', 'Rabigh', 'Khulays', 'Al-Kamil', 'Al-Madinah', 'Yanbu Al-Bahr',
        'Al-Ula', 'Al-Mahd', 'Badr', 'Khaybar', 'Al-Hinakiyah', "Wadi Al Fare'",
        'Al Ais', 'Al-Wajh', 'Umluj', "Al Ha'et"
    ]
)

end_city = st.selectbox(
    "Select destination city",
    options=[
        'Jeddah', 'Rabigh', 'Khulays', 'Al-Kamil', 'Al-Madinah', 'Yanbu Al-Bahr',
        'Al-Ula', 'Al-Mahd', 'Badr', 'Khaybar', 'Al-Hinakiyah', "Wadi Al Fare'",
        'Al Ais', 'Al-Wajh', 'Umluj', "Al Ha'et"
    ]
)

num_days = st.number_input("Number of trip days", min_value=1, max_value=10, value=3)
sites_per_day = st.number_input("Number of sites per day", min_value=1, max_value=20, value=5)
include_rest_stop = st.checkbox("Include a rest stop in the middle of each day?")

if st.button("Generate Route"):
    st.success("✔️ Inputs received. Ready to show the route on map.")
    st.write("**Selected Categories:**", selected_categories)
    st.write("**Start City:**", start_city)
    st.write("**End City:**", end_city)
    st.write(f"**Trip Duration:** {num_days} day(s), {sites_per_day} site(s) per day")
    st.write("**Rest Stop Included:**", "Yes" if include_rest_stop else "No")

    # --- ROUTE MAPPING ---
    try:
        tourism_gdf = gpd.read_file("data/Site_Torism.shp", encoding='cp1256')
    except:
        tourism_gdf = gpd.read_file("data/Site_Torism.shp", encoding='latin1')

    cities_gdf = gpd.read_file("data/Site.shp")

    filtered_sites = tourism_gdf[tourism_gdf["Category_c"].isin(selected_categories)]

    if start_city not in cities_gdf["NAME"].values or end_city not in cities_gdf["NAME"].values:
        st.error("❌ Start or End city not found in city layer.")
        st.stop()

    start_geom = cities_gdf[cities_gdf["NAME"] == start_city].geometry.iloc[0].centroid
    end_geom = cities_gdf[cities_gdf["NAME"] == end_city].geometry.iloc[0].centroid

    line = LineString([start_geom, end_geom])
    buffer = gpd.GeoSeries([line.buffer(0.25)])

    filtered_sites = filtered_sites[filtered_sites.geometry.within(buffer.iloc[0])]

    m = folium.Map(location=[start_geom.y, start_geom.x], zoom_start=7, tiles="CartoDB Positron")

    folium.Marker([start_geom.y, start_geom.x], tooltip="Start City", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([end_geom.y, end_geom.x], tooltip="End City", icon=folium.Icon(color="red")).add_to(m)

    for _, row in filtered_sites.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=5, color="blue", fill=True,
            fill_opacity=0.7, tooltip=row["name"]
        ).add_to(m)

    folium.PolyLine(locations=[[pt[1], pt[0]] for pt in line.coords], color="black", weight=2.5).add_to(m)

    st.subheader("📍 Filtered Tourism Sites and Route")
    st_data = st_folium(m, width=900, height=600, returned_objects=["all"])
    st.write("🧪 Debug Output:", st_data)
