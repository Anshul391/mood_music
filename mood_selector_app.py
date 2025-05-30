import streamlit as st
from PIL import Image
import io
import requests
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
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
    
    # Try to find the exact track first
    query = f'track:"{song}" artist:"{artist}"'
    params = {
        "q": query,
        "type": "track",
        "limit": 1,
        "market": "US"
    }
    
    try:
        response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
        response.raise_for_status()
        tracks = response.json().get("tracks", {}).get("items", [])
        
        if tracks:
            track = tracks[0]
            # Get full track details
            track_id = track["id"]
            track_response = requests.get(
                f"https://api.spotify.com/v1/tracks/{track_id}",
                headers=headers,
                params={"market": "US"}
            )
            track_response.raise_for_status()
            track_details = track_response.json()
            
            if track_details.get("preview_url"):
                return [{
                    "name": track_details["name"],
                    "artist": track_details["artists"][0]["name"],
                    "album_img": track_details["album"]["images"][0]["url"] if track_details["album"]["images"] else None,
                    "preview_url": track_details["preview_url"],
                    "spotify_url": track_details["external_urls"]["spotify"]
                }]
    except Exception:
        pass
    
    # If no preview URL found, try alternative search
    try:
        # Try searching with just the song name
        params = {
            "q": f'track:"{song}"',
            "type": "track",
            "limit": 5,
            "market": "US"
        }
        response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
        response.raise_for_status()
        tracks = response.json().get("tracks", {}).get("items", [])
        
        for track in tracks:
            if track.get("preview_url"):
                return [{
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "album_img": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
                    "preview_url": track["preview_url"],
                    "spotify_url": track["external_urls"]["spotify"]
                }]
    except Exception:
        pass
    
    return []

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
            
            # Split by numbered entries
            song_entries = songs_text.split("\n\n")
            
            for entry in song_entries:
                if not entry.strip():
                    continue
                    
                lines = entry.strip().split("\n")
                song_data = {"name": "", "artist": "", "reason": ""}
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Remove quotes and clean up
                    line = line.replace('"', '').strip()
                    
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
    language = st.selectbox("Language", ["English", "Spanish", "French", "Hindi", "Korean", "Japanese", "Chinese"])
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
                mood, ai_songs = get_mood_azure_openai(tags, description, genre, language, activity)
                if not mood:
                    mood = "Bright and Happy"
                st.success(f"🧠 Detected Mood: **{mood}**")
                
                # Display AI Song Recommendations
                if ai_songs:
                    st.markdown("### 🎵 AI Song Recommendations")
                    
                    # Get Spotify tracks for the AI recommendations
                    spotify_tracks = []
                    for song in ai_songs:
                        tracks = search_spotify_tracks_fallback(
                            song["name"],
                            song["artist"],
                            limit=1
                        )
                        if tracks:
                            spotify_tracks.extend(tracks)
                    
                    # Create a mapping of song names to Spotify tracks
                    spotify_map = {track["name"].lower(): track for track in spotify_tracks}
                    
                    for song in ai_songs:
                        spotify_track = spotify_map.get(song["name"].lower())
                        # Start a horizontal container for image + info
                        st.markdown(
                            "<div style='display: flex; align-items: center; margin-bottom: 24px;'>",
                            unsafe_allow_html=True
                        )
                        # Album image
                        if spotify_track and spotify_track.get("album_img"):
                            st.markdown(
                                f"<img src='{spotify_track['album_img']}' width='70' height='70' style='border-radius:8px; margin-right:18px; box-shadow:0 2px 8px rgba(30,185,84,0.10);'>",
                                unsafe_allow_html=True
                            )
                        # Song info card
                        st.markdown(
                            f"""
                            <div style='background: #232a34; border-radius: 10px; padding: 16px 18px; box-shadow: 0 2px 8px rgba(30,185,84,0.10); border-left: 5px solid #1DB954; min-width: 220px;'>
                                <span style='font-size:1.15em; color:#1DB954; font-weight:bold;'>{song.get('name', 'Unknown Song')}</span><br>
                                <span style='color:#fff; font-size:1em;'>{song.get('artist', 'Unknown Artist')}</span>
                            </div>
                            """, unsafe_allow_html=True
                        )
                        st.markdown("</div>", unsafe_allow_html=True)  # Close flex container

                        # Audio or YouTube
                        if spotify_track and spotify_track.get("preview_url"):
                            st.audio(spotify_track["preview_url"], format="audio/mp3")
                        else:
                            yt_query = f"{song.get('name', '')} {song.get('artist', '')}".replace(' ', '+')
                            st.markdown(
                                f"<a href='https://www.youtube.com/results?search_query={yt_query}' target='_blank' style='color:#FF0000; font-size:1em; font-weight:bold; display:inline-block; margin-bottom:4px;'>🔗 Listen on YouTube</a>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                "<span style='color:#b3b3b3; margin-bottom:16px; display:inline-block;'>No Spotify preview available for this track.</span>",
                                unsafe_allow_html=True
                            )
                
                st.markdown("#### Your Photo:")
                st.image(image_data, caption="Your Photo", width=175)  # Reduced size
            except Exception as e:
                st.error(f"Error: {e}")
                mood = ""
                spotify_tracks = []
    elif not image_data:
        st.info("Upload or take a photo, then click 'Process' to continue.")