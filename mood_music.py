import streamlit as st
from PIL import Image
import io
import requests
from typing import List, Tuple
import json
from openai import AzureOpenAI

st.set_page_config(page_title="MoodMusic Premium", page_icon="🎧", layout="centered")

# --- Azure Computer Vision Helper ---
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

# --- Azure OpenAI Helper ---
def get_mood_azure_openai(tags: List[str], description: str, genre: str, language: str, activity: str) -> Tuple[str, List[dict]]:
    client = AzureOpenAI(
        api_key=st.secrets["azure_openai"]["api_key"],
        api_version=st.secrets["azure_openai"]["api_version"],
        azure_endpoint=st.secrets["azure_openai"]["endpoint"]
    )
    prompt = f"""
    Analyze the following image description and tags, and the user's preferences.
    - Tags: {', '.join(tags)}
    - Description: {description}
    - Genre: {genre}
    - Language: {language}
    - Activity: {activity}

    First, classify the mood of the image in one of these categories:
    - Bright and Happy
    - Warm and Energetic
    - Cool and Calm
    - Mellow and Relaxed

    Then, suggest 3 songs that match this mood, genre, language, and activity.
    For each song, provide:
    - Song name
    - Artist name
    - A brief reason why it matches the mood

    Format your response exactly like this:
    MOOD: [mood category]

    SONG RECOMMENDATIONS:
    1. Song: [song name]
       Artist: [artist name]
       Why: [brief explanation]

    2. Song: [song name]
       Artist: [artist name]
       Why: [brief explanation]

    3. Song: [song name]
       Artist: [artist name]
       Why: [brief explanation]
    """
    try:
        response = client.chat.completions.create(
            model=st.secrets["azure_openai"]["deployment_name"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        response_text = response.choices[0].message.content
        # Parse mood
        mood = ""
        if "MOOD:" in response_text:
            mood = response_text.split("MOOD:")[1].split("\n")[0].strip()
        # Parse song recommendations
        songs = []
        if "SONG RECOMMENDATIONS:" in response_text:
            songs_text = response_text.split("SONG RECOMMENDATIONS:")[1].strip()
            song_entries = songs_text.split("\n\n")
            for entry in song_entries:
                if not entry.strip():
                    continue
                lines = entry.strip().split("\n")
                song_data = {"name": "", "artist": "", "reason": ""}
                for line in lines:
                    line = line.strip().replace('"', '')
                    if "Song:" in line:
                        song_data["name"] = line.split("Song:")[1].strip()
                    elif "Artist:" in line:
                        song_data["artist"] = line.split("Artist:")[1].strip()
                    elif "Why:" in line:
                        song_data["reason"] = line.split("Why:")[1].strip()
                if song_data["name"] and song_data["artist"] and song_data["reason"]:
                    songs.append(song_data)
        return mood, songs
    except Exception as e:
        st.error(f"AI mood suggestion error: {e}")
        return "", []

# --- Deezer Search Helper ---
def search_deezer_track(song: str, artist: str):
    query = f"track:'{song}' artist:'{artist}'"
    url = f"https://api.deezer.com/search?q={query}"
    try:
        resp = requests.get(url)
        data = resp.json()
        for track in data.get("data", []):
            if track.get("preview"):
                return {
                    "title": track["title"],
                    "artist": track["artist"]["name"],
                    "album_img": track["album"]["cover_medium"],
                    "preview_url": track["preview"],
                    "deezer_url": track["link"]
                }
        return None
    except Exception as e:
        return None

# --- UI ---
st.markdown("""
<style>
body {
    background-color: #f6f8fa;
}
.block-container {
    padding-top: 3.5rem;
}
.song-card {
    background: #232a34;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 24px;
    box-shadow: 0 2px 12px rgba(30,185,84,0.10);
    border-left: 6px solid #1DB954;
    min-width: 220px;
}
.song-title {
    font-size: 1.3em;
    color: #1DB954;
    font-weight: bold;
    margin-bottom: 0.2em;
}
.song-artist {
    color: #fff;
    font-size: 1.1em;
    margin-bottom: 0.2em;
}
.song-reason {
    color: #b3b3b3;
    font-size: 1em;
    margin-bottom: 0.2em;
}
.deezer-link {
    color: #ff5500;
    font-weight: bold;
    text-decoration: none;
    margin-top: 8px;
    display: inline-block;
}
.header-premium {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 8px;
    margin-top: 2.5rem;
}
.header-title-premium {
    display: flex;
    align-items: center;
    font-size: 2.2rem;
    font-weight: bold;
    color: #1DB954;
    white-space: nowrap;
}
.header-emoji-premium {
    font-size: 2.2rem;
    margin-right: 12px;
}
.header-sub-premium {
    color: #888;
    font-size: 1.1rem;
    margin-top: 2px;
    text-align: center;
}
</style>
<div class='header-premium'>
    <div class='header-title-premium'>
        <span class='header-emoji-premium'>🎧</span>
        MoodMusic Premium
    </div>
    <div class='header-sub-premium'>Your AI-powered mood-based music companion</div>
</div>
<hr style='margin:0 0 24px 0;'>
""", unsafe_allow_html=True)

left, right = st.columns([1,2])

with left:
    st.header("Your Details & Preferences")
    user_name = st.text_input("Your Name (optional)")
    music_type = st.selectbox("Music Type", [
        "Pop", "Rock", "Hip Hop", "Electronic", "Jazz", "Classical", "R&B", "Country", "Reggae", "Blues", "Folk", "Metal", "Soul", "Dance", "Indie", "K-Pop", "Latin", "World", "Soundtrack"
    ])
    language = st.selectbox("Language", ["English", "Spanish", "French", "Hindi", "Korean", "Japanese", "Chinese", "German", "Italian", "Portuguese", "Russian", "Arabic"])
    mood = st.selectbox("Mood", [
        "Relaxed", "Energetic", "Happy", "Sad", "Romantic", "Chill", "Party", "Focus", "Upbeat", "Melancholic", "Motivational", "Calm", "Aggressive", "Dreamy"
    ])
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
                mood, ai_songs = get_mood_azure_openai(tags, description, music_type, language, mood)
                if not mood:
                    mood = "Bright and Happy"
                st.success(f"🧠 Detected Mood: **{mood}**")
                if ai_songs:
                    st.markdown("### 🎵 AI Song Recommendations")
                    for idx, song in enumerate(ai_songs, 1):
                        deezer_track = search_deezer_track(song["name"], song["artist"])
                        with st.container():
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                if deezer_track and deezer_track.get("album_img"):
                                    st.image(deezer_track["album_img"], width=100)
                                else:
                                    st.image("https://upload.wikimedia.org/wikipedia/commons/6/65/No-Image-Placeholder.svg", width=100)
                            with col2:
                                st.markdown(
                                    f"""
                                    <div class='song-card'>
                                        <div class='song-title'>{song.get('name', 'Unknown Song')}</div>
                                        <div class='song-artist'>{song.get('artist', 'Unknown Artist')}</div>
                                        <div class='song-reason'>{song.get('reason', '')}</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                if deezer_track and deezer_track.get("preview_url"):
                                    st.audio(deezer_track["preview_url"])
                                    st.markdown(f"<a class='deezer-link' href='{deezer_track['deezer_url']}' target='_blank'>🔗 Listen on Deezer</a>", unsafe_allow_html=True)
                                else:
                                    st.info("No preview available for this song on Deezer.")
                        if idx < len(ai_songs):
                            st.markdown("---")
                st.markdown("#### Your Photo:")
                st.image(image_data, caption="Your Photo", width=175)
            except Exception as e:
                st.error(f"Error: {e}")
    elif not image_data:
        st.info("Upload or take a photo, then click 'Process' to continue.") 