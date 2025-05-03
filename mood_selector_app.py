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

def recommend_songs(mood, genre, language, activity):
    key = (mood, genre, language, activity)
    sample_db = {
        ("Bright and Happy", "Pop", "English", "Workout"): [
            ("Can’t Stop the Feeling - Justin Timberlake", "https://www.youtube.com/watch?v=ru0K8uYEZWw"),
            ("Good as Hell - Lizzo", "https://www.youtube.com/watch?v=vuq-VAiW9kw")
        ],
        ("Cool and Calm", "Indie", "English", "Study"): [
            ("Riptide - Vance Joy", "https://www.youtube.com/watch?v=uJ_1HMAGb4k"),
            ("Holocene - Bon Iver", "https://www.youtube.com/watch?v=TWcyIpul8OE")
        ],
        ("Warm and Energetic", "Rock", "English", "Workout"): [
            ("Eye of the Tiger - Survivor", "https://www.youtube.com/watch?v=btPJPFnesV4"),
            ("Seven Nation Army - The White Stripes", "https://www.youtube.com/watch?v=0J2QdDbelmY")
        ],
        ("Mellow and Relaxed", "Electronic", "French", "Relax"): [
            ("La Femme d’Argent - Air", "https://www.youtube.com/watch?v=Fz2ZDeTY9vY"),
            ("Nightcall - Kavinsky", "https://www.youtube.com/watch?v=MV_3Dpw-BRY")
        ]
    }

    return sample_db.get(key, [
        ("Let Her Go - Passenger", "https://www.youtube.com/watch?v=RBumgq5yVrA"),
        ("Budapest - George Ezra", "https://www.youtube.com/watch?v=VHrLPs3_1Fs")
    ])

def extract_dominant_color(image_bytes):
    try:
        color_thief = ColorThief(io.BytesIO(image_bytes))
        return color_thief.get_color(quality=1)
    except Exception as e:
        st.error(f"Failed to extract color: {e}")
        return None

# --- App Setup ---
st.set_page_config(page_title="MoodMusic Pro", page_icon="🎧", layout="centered")
st.title("🎛️ MoodMusic Pro")
st.subheader("Upload a photo to get a mood-based music recommendation 🎵")

# --- Sidebar Preferences ---
with st.sidebar:
    st.header("Your Preferences")
    genre = st.selectbox("Genre", ["Pop", "Rock", "Indie", "Electronic"])
    language = st.selectbox("Language", ["English", "Spanish", "French"])
    activity = st.selectbox("Activity Type", ["Relax", "Workout", "Study", "Driving"])
    vibe_option = st.selectbox("Mood", [
        "Detect from Photo", "Bright and Happy", "Warm and Energetic", "Cool and Calm", "Mellow and Relaxed"
    ])

# --- Image Upload ---
st.markdown("### 📸 Step 1: Upload or Take a Photo")
uploaded_photo = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
camera_photo = st.camera_input("Or take a live photo")

image_data = uploaded_photo or camera_photo

# --- Buttons ---
process_clicked = st.button("🎶 Process Photo and Get Music")
reset_clicked = st.button("🔄 Reset")

# --- State Reset ---
if reset_clicked:
    st.experimental_rerun()

# --- Process Button Logic ---
if process_clicked and image_data:
    image_bytes = image_data.getvalue()

    # Extract mood if selected
    if vibe_option == "Detect from Photo":
        dominant_color = extract_dominant_color(image_bytes)
        if dominant_color:
            mood = detect_mood(dominant_color)
            st.success(f"🧠 Detected Mood: **{mood}** (Dominant Color: {dominant_color})")
        else:
            mood = "Mellow and Relaxed"
            st.warning("Default mood used due to image error.")
    else:
        mood = vibe_option
        st.info(f"🎯 Using selected mood: **{mood}**")

    # --- Song Recommendations ---
    st.markdown("### 🎧 Song Recommendations")
    results = recommend_songs(mood, genre, language, activity)

    if results:
        for song, link in results:
            st.markdown(f"- [{song}]({link})")
        if results[0][0] == "Let Her Go - Passenger":
            st.info("🎵 Showing default fallback tracks. Try different settings!")
else:
    if not image_data:
        st.info("Upload or take a photo, then click 'Process' to continue.")
