import streamlit as st
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Top 10 Seoul Attractions (for foreigners)", layout="wide")

st.title("Top 10 Seoul Attractions — Popular with Foreign Visitors")
st.markdown(
    "Interactive Folium map showing **popular Seoul tourist spots** frequently recommended to international visitors. "
    "Click markers for short descriptions. This app is ready to run on Streamlit Cloud."
)

# central map location (Seoul City Hall / central Seoul)
CENTER = (37.5665, 126.9780)

# Top 10 list (name, lat, lon, short description)
places = [
    {
        "name": "Gyeongbokgung Palace",
        "lat": 37.579884,
        "lon": 126.976800,
        "desc": "Main royal palace of the Joseon dynasty; must-see historic site."
    },
    {
        "name": "Changdeokgung Palace (incl. Secret Garden)",
        "lat": 37.57944,
        "lon": 126.99278,
        "desc": "UNESCO World Heritage palace known for its beautiful Secret Garden."
    },
    {
        "name": "Bukchon Hanok Village",
        "lat": 37.5833,
        "lon": 126.9830,
        "desc": "Traditional hanok neighborhood with photogenic alleys and tea houses."
    },
    {
        "name": "N Seoul Tower (Namsan)",
        "lat": 37.551425,
        "lon": 126.988000,
        "desc": "Iconic observation tower with panoramic views of Seoul."
    },
    {
        "name": "Myeongdong",
        "lat": 37.5633,
        "lon": 126.9873,
        "desc": "Major shopping and street-food district popular with visitors."
    },
    {
        "name": "Hongdae (Hongik University area)",
        "lat": 37.55667,
        "lon": 126.92361,
        "desc": "Youthful district known for street performances, nightlife and cafes."
    },
    {
        "name": "Insadong",
        "lat": 37.5744,
        "lon": 126.9850,
        "desc": "Cultural shopping street for crafts, galleries and traditional tea houses."
    },
    {
        "name": "Gwangjang Market",
        "lat": 37.5703,
        "lon": 126.9993,
        "desc": "One of Korea's oldest and largest traditional markets — great street food."
    },
    {
        "name": "Cheonggyecheon Stream (Cheonggye Plaza area)",
        "lat": 37.5690,
        "lon": 126.9779,
        "desc": "Restored urban stream and pedestrian promenade in central Seoul."
    },
    {
        "name": "Lotte World Tower / Seokchon Lake",
        "lat": 37.5130,
        "lon": 127.1025,
        "desc": "Modern skyscraper complex with observation deck, mall and nearby lake."
    },
]

# Sidebar controls
st.sidebar.header("Map options")
show_heat = st.sidebar.checkbox("Show markers (default: on)", value=True)
start_zoom = st.sidebar.slider("Start zoom", min_value=11, max_value=15, value=12)

# Create map
m = folium.Map(location=CENTER, zoom_start=start_zoom)

if show_heat:
    for p in places:
        folium.Marker(
            [p["lat"], p["lon"]],
            popup=f"<b>{p['name']}</b><br>{p['desc']}",
            tooltip=p["name"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

# Add a mini list of places on the map (Layer control)
folium.LayerControl().add_to(m)

# Render map in Streamlit
st.subheader("Map — click a marker to open a popup")
st_folium(m, width="100%", height=650)

# Show the list and quick links
st.subheader("Top 10 (quick list)")
for i, p in enumerate(places, start=1):
    st.markdown(f"**{i}. {p['name']}** — {p['desc']}  \nCoordinates: {p['lat']}, {p['lon']}")

st.markdown("---")
st.caption("Data sources: public tourism guides and official pages. Coordinates are representative points for each area.")
