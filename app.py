import streamlit as st
from PIL import Image
from colorthief import ColorThief
import io

# ---------- Helper Functions ----------
def detect_mood(dominant_color):
    r, g, b = dominant_color
    if r > 200 and g > 200 and b > 200:
        return "Bright and Happy"
    elif r > 150 and b < 100:
        return "Warm and Energetic"
    elif b > 150:
        return "Cool and Calm"
    else:
        return "Mellow and Relaxed"

def recommend_songs(mood, theme, genre, language):
    # Later this can be API connected. Right now: sample song list.
    song_db = {
        "Bright and Happy": [
            ("Happy - Pharrell Williams", "https://www.youtube.com/watch?v=ZbZSe6N_BXs"),
            ("Can't Stop the Feeling - Justin Timberlake", "https://www.youtube.com/watch?v=ru0K8uYEZWw"),
            ("Best Day of My Life - American Authors", "https://www.youtube.com/watch?v=Y66j_BUCBMY"),
            ("Walking on Sunshine - Katrina & The Waves", "https://www.youtube.com/watch?v=iPUmE-tne5U")
        ],
        "Warm and Energetic": [
            ("Blinding Lights - The Weeknd", "https://www.youtube.com/watch?v=4NRXx6U8ABQ"),
            ("Levitating - Dua Lipa", "https://www.youtube.com/watch?v=TUVcZfQe-Kw"),
            ("Uptown Funk - Bruno Mars", "https://www.youtube.com/watch?v=OPf0YbXqDm0"),
            ("On Top of the World - Imagine Dragons", "https://www.youtube.com/watch?v=w5tWYmIOWGk")
        ],
        "Cool and Calm": [
            ("Someone Like You - Adele", "https://www.youtube.com/watch?v=hLQl3WQQoQ0"),
            ("Let It Go - James Bay", "https://www.youtube.com/watch?v=GsPq9mzFNGY"),
            ("Stay With Me - Sam Smith", "https://www.youtube.com/watch?v=pB-5XG-DbAA"),
            ("The A Team - Ed Sheeran", "https://www.youtube.com/watch?v=UAWcs5H-qgQ")
        ],
        "Mellow and Relaxed": [
            ("Let Her Go - Passenger", "https://www.youtube.com/watch?v=RBumgq5yVrA"),
            ("Fix You - Coldplay", "https://www.youtube.com/watch?v=k4V3Mo61fJM"),
            ("Skinny Love - Birdy", "https://www.youtube.com/watch?v=aNzCDt2eidg"),
            ("I Will Follow You Into The Dark - Death Cab for Cutie", "https://www.youtube.com/watch?v=NDHY1D0tKRA")
        ]
    }

    # Later you can refine suggestions based on theme, genre, language!
    return song_db.get(mood, [])

# ---------- Streamlit App ----------
st.set_page_config(page_title="MoodMusic", page_icon="🎵", layout="centered")
st.title("🎵 MoodMusic")
st.subheader("Find the perfect background music for your photo!")

# Upload image
uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

# User preferences
st.sidebar.header("Customize Your MoodMusic 🎶")
theme = st.sidebar.selectbox("Select a Theme", ["Any", "Love", "Adventure", "Party", "Chill"])
genre = st.sidebar.selectbox("Select Genre", ["Any", "Pop", "Rock", "Indie", "Electronic"])
language = st.sidebar.selectbox("Select Language", ["Any", "English", "Spanish", "French", "Korean"])

if uploaded_file is not None:
    # Show image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Analyze image for dominant color
    color_thief = ColorThief(io.BytesIO(uploaded_file.read()))
    dominant_color = color_thief.get_color(quality=1)
    st.markdown(f"**Detected Dominant Color:** `{dominant_color}`")

    # Detect mood
    mood = detect_mood(dominant_color)
    st.success(f"Detected Mood: {mood}")

    # Recommend songs
    st.header("🎼 Recommended Songs for You")
    songs = recommend_songs(mood, theme, genre, language)

    for song, link in songs:
        st.markdown(f"- [{song}]({link}) 🔗")

else:
    st.info("👆 Please upload an image to get started!")

