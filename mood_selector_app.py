import streamlit as st
from PIL import Image
import io
import requests
import openai
from typing import List, Tuple
import base64
import json

# --- Spotify Integration ---
def get_spotify_token() -> str:
    client_id = st.secrets["spotify"]["client_id"]
    client_secret = st.secrets["spotify"]["client_secret"]
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def search_spotify_tracks_fallback(song: str, artist: str, limit: int = 3) -> list:
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    queries = [
        f"{song} {artist}",
        f"{song}",
        f"{artist}"
    ]
    seen = set()
    results = []
    for query in queries:
        params = {"q": query.lower().strip(), "type": "track", "limit": limit}
        response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
        response.raise_for_status()
        tracks = response.json().get("tracks", {}).get("items", [])
        for track in tracks:
            track_id = track["id"]
            if track_id not in seen:
                seen.add(track_id)
                results.append({
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "album_img": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
                    "preview_url": track.get("preview_url"),
                    "spotify_url": track["external_urls"]["spotify"]
                })
            if len(results) >= limit:
                return results
    return results

# --- Azure Computer Vision Integration ---
def analyze_photo_with_azure_cv(image_bytes: bytes) -> dict:
    endpoint = st.secrets["azure_cv"]["endpoint"]
    api_key = st.secrets["azure_cv"]["api_key"]
    analyze_url = endpoint.rstrip("/") + "/vision/v3.2/analyze"
    headers = {
        'Ocp-Apim-Subscription-Key': api_key,
        'Content-Type': 'application/octet-stream'
    }
    params = {'visualFeatures': 'Description,Tags'}
    response = requests.post(analyze_url, headers=headers, params=params, data=image_bytes)
    response.raise_for_status()
    return response.json()

# --- Placeholder Song Selection ---
def get_placeholder_song(mood: str, genre: str, language: str, activity: str) -> dict:
    try:
        with open("placeholder_songs.json", "r", encoding="utf-8") as f:
            songs = json.load(f)
        for entry in songs:
            if (
                entry["mood"] == mood and
                entry["genre"] == genre and
                entry["language"] == language and
                entry["activity"] == activity
            ):
                return entry
    except Exception:
        pass
    return None

# --- Azure OpenAI for Mood Suggestion ---
def get_mood_azure_openai(tags: List[str], description: str, genre: str, language: str, activity: str) -> str:
    openai.api_type = "azure"
    openai.api_key = st.secrets["azure_openai"]["api_key"]
    openai.azure_endpoint = st.secrets["azure_openai"]["endpoint"]
    openai.api_version = st.secrets["azure_openai"]["api_version"]
    deployment_id = st.secrets["azure_openai"]["deployment_name"]

    prompt = f"""
    Analyze the following image description and tags, and the user's preferences.
    - Tags: {', '.join(tags)}
    - Description: {description}
    - Genre: {genre}
    - Language: {language}
    - Activity: {activity}

    Classify the mood of the image in one of these categories:
    - Bright and Happy
    - Warm and Energetic
    - Cool and Calm
    - Mellow and Relaxed

    Format your response exactly like this:
    MOOD: [mood category]
    """

    try:
        response = openai.chat.completions.create(
            model=deployment_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        response_text = response.choices[0].message.content
        if "MOOD:" in response_text:
            return response_text.split("MOOD:")[1].split("\n")[0].strip()
    except Exception as e:
        st.error(f"AI mood suggestion error: {e}")
    return ""

# --- App Setup ---
st.set_page_config(page_title="MoodMusic Pro", page_icon="🎧", layout="centered")

# --- Compact Header ---
st.markdown("""
<div style='display:flex; align-items:center; margin-bottom:8px;'>
    <div style='font-size:2rem; font-weight:bold; color:#1DB954; margin-right:12px;'>🎛️ MoodMusic Pro</div>
    <div style='color:#888; font-size:1rem;'>Your AI-powered mood-based music companion</div>
</div>
<hr style='margin:0 0 16px 0;'>
""", unsafe_allow_html=True)

# --- Two-Column Layout ---
left, right = st.columns([1,2])

with left:
    st.header("Your Details & Preferences")
    user_name = st.text_input("Your Name (optional)")
    genre = st.selectbox("Genre", ["Pop", "Rock", "Indie", "Electronic", "Hip Hop", "Classical", "Jazz"])
    language = st.selectbox("Language", ["English", "Spanish", "French", "Hindi", "Korean", "Japanese"])
    activity = st.selectbox("Activity Type", ["Relax", "Workout", "Study", "Driving", "Party", "Meditation"])
    st.markdown("<br>", unsafe_allow_html=True)

with right:
    st.header("Step 1: Upload or Take a Photo")
    uploaded_photo = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    camera_photo = st.camera_input("Or take a live photo")
    image_data = uploaded_photo or camera_photo
    process_clicked = st.button("🎶 Process Photo and Get Music", use_container_width=True)
    reset_clicked = st.button("🔄 Reset", use_container_width=True)
    if reset_clicked:
        st.experimental_rerun()

    st.markdown("---")
    st.header("Step 2: Your Mood-Based Music Recommendations")
    if process_clicked and image_data:
        with st.spinner("Analyzing your photo and finding the perfect music..."):
            try:
                image_bytes = image_data.getvalue()
                analysis = analyze_photo_with_azure_cv(image_bytes)
                tags = [t['name'] for t in analysis.get('tags', [])]
                description = analysis.get('description', {}).get('captions', [{}])[0].get('text', '')
                st.markdown(f"**Azure CV Description:** {description if description else 'None'}")
                mood = get_mood_azure_openai(tags, description, genre, language, activity) or "Bright and Happy"
                st.success(f"🧠 Detected Mood: **{mood}**")
                st.markdown("#### Your Photo:")
                st.image(image_data, caption="Your Photo", width=175)  # Reduced size
                placeholder_song = get_placeholder_song(mood, genre, language, activity)
                spotify_tracks = []
                if placeholder_song:
                    spotify_tracks = search_spotify_tracks_fallback(
                        placeholder_song["song"],
                        placeholder_song["artist"],
                        limit=3
                    )
                if not spotify_tracks:
                    st.warning("⚠️ No Spotify preview or results found. Try another image or change preferences.")
                else:
                    st.markdown("### 🎧 Spotify Previews")
                    col1, col2 = st.columns(2)
                    for i, track in enumerate(spotify_tracks):
                        with col1 if i % 2 == 0 else col2:
                            st.markdown(f"""
                            <div style='padding: 16px; border-radius: 12px; background: var(--background-color, #222); box-shadow: 0 2px 8px rgba(0,0,0,0.12); margin: 10px 0; text-align: center;'>
                                <img src='{track['album_img']}' width='120' style='border-radius:10px; margin-bottom:8px;'><br>
                                <b style='font-size:1.1em'>{track['name']}</b><br>
                                <span style='color:#aaa;'>{track['artist']}</span><br>
                                {'<audio controls src="' + track['preview_url'] + '" style="width: 100%; margin-top: 8px;"></audio><br>' if track['preview_url'] else '<span style="color: #888;">No preview available</span><br>'}
                                <a href='{track['spotify_url']}' target='_blank' style='color:#1DB954;font-weight:bold;'>Open in Spotify</a>
                            </div>
                            """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
                mood = ""
                spotify_tracks = []
    elif not image_data:
        st.info("Upload or take a photo, then click 'Process' to continue.")