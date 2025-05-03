import streamlit as st
from PIL import Image
from colorthief import ColorThief
import io

# --- Helper Functions ---
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

def recommend_songs(mood, genre, language):
    # Dummy example: Later link with real API or database
    sample_db = {
        ("Bright and Happy", "Pop", "English"): [
            ("Happy - Pharrell Williams", "https://www.youtube.com/watch?v=ZbZSe6N_BXs"),
            ("Good Time - Owl City & Carly Rae Jepsen", "https://www.youtube.com/watch?v=H7HmzwI67ec")
        ],
        ("Cool and Calm", "Indie", "English"): [
            ("Riptide - Vance Joy", "https://www.youtube.com/watch?v=uJ_1HMAGb4k"),
            ("Holocene - Bon Iver", "https://www.youtube.com/watch?v=TWcyIpul8OE")
        ]
    }

    key = (mood, genre, language)
    return sample_db.get(key, [("Let Her Go - Passenger", "https://www.youtube.com/watch?v=RBumgq5yVrA")])

# --- Streamlit UI ---
st.set_page_config(page_title="MoodMusic Pro", page_icon="🎛️", layout="centered")
st.title("🎛️ MoodMusic Pro")
st.subheader("Customize your vibe — choose a mood, genre, language, and image")

# --- Sidebar Preferences ---
st.sidebar.header("Your Preferences")
genre = st.sidebar.selectbox("Select Genre", ["Pop", "Rock", "Indie", "Electronic"])
vibe_option = st.sidebar.selectbox("Preferred Mood/Vibe", ["Detect from Photo", "Bright and Happy", "Warm and Energetic", "Cool and Calm", "Mellow and Relaxed"])
language = st.sidebar.selectbox("Language", ["English", "Spanish", "French"])

# --- Image Input ---
st.markdown("### 📸 Upload or Take a Photo")
uploaded_photo = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
camera_photo = st.camera_input("Or take a live photo")

# --- Determine Image to Use ---
image_data = uploaded_photo if uploaded_photo else camera_photo

if image_data:
    image = Image.open(image_data)
    st.image(image, caption="Your Selected Photo", use_column_width=True)

    # Extract mood if selected
    if vibe_option == "Detect from Photo":
        color_thief = ColorThief(io.BytesIO(image_data.getvalue()))
        dominant_color = color_thief.get_color(quality=1)
        mood = detect_mood(dominant_color)
        st.success(f"Detected Mood: **{mood}** (Dominant color: {dominant_color})")
    else:
        mood = vibe_option
        st.info(f"Using selected mood: **{mood}**")

    # Recommend Songs
    st.markdown("### 🎶 Song Recommendations")
    results = recommend_songs(mood, genre, language)
    for song, link in results:
        st.markdown(f"- [{song}]({link})")
else:
    st.warning(" Upload or take a photo to get started.")
