# MoodMusic Pro

## Overview
MoodMusic Pro is an AI-powered web app that recommends music based on your mood, detected from a photo, and your preferences (genre, language, activity). The app uses Azure Computer Vision and Azure OpenAI for mood detection, and integrates with the Spotify API to provide real song previews. The UI/UX is modern, compact, and responsive.

---

## 🏆 Milestone 2 Rubric Checklist

### 1. Feature Completion
- [x] **Photo-based mood detection** using Azure Computer Vision and Azure OpenAI
- [x] **User preferences**: genre, language, activity
- [x] **Spotify integration**: real-time search and 30s preview for recommended songs
- [x] **Modern UI/UX**: compact, two-column layout, responsive, dark mode ready
- [x] **Placeholder fallback**: demo mode with curated song list if AI quota is unavailable

### 2. Bug Fixes & Feedback Handling
- [x] Addressed all major client feedback:
  - Removed duplicate photo display
  - Removed mood color swatch and animations
  - Moved photo upload to right column, results below
  - Reduced scrolling and improved layout
  - Improved Spotify fallback and error handling
- [x] Fixed Spotify API search and preview issues
- [x] Waiting for quota approval on AzureAI


### 3. Client Code Review
- [x] Client reviewed and approved all major UI/UX and backend changes
- [x] Client feedback incorporated iteratively throughout development

### 4. README – Setup & Usage

#### **Setup**
1. Clone the repository and navigate to the project folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your API keys to `.streamlit/secrets.toml`:
   ```toml
   [azure_cv]
   api_key = "YOUR_AZURE_CV_KEY"
   endpoint = "YOUR_AZURE_CV_ENDPOINT"

   [azure_openai]
   api_key = "YOUR_AZURE_OPENAI_KEY"
   endpoint = "YOUR_AZURE_OPENAI_ENDPOINT"
   deployment_name = "YOUR_DEPLOYMENT_NAME"
   api_version = "2024-02-15-preview"

   [spotify]
   client_id = "YOUR_SPOTIFY_CLIENT_ID"
   client_secret = "YOUR_SPOTIFY_CLIENT_SECRET"
   ```
4. (Optional) Enable dark mode by adding to `.streamlit/config.toml`:
   ```toml
   [theme]
   base="dark"
   ```
5. Run the app:
   ```bash
   streamlit run mood_selector_app.py
   ```

#### **Usage**
- Enter your name and select your music preferences (genre, language, activity) on the left.
- Upload or take a photo on the right.
- Click "Process Photo and Get Music" to receive mood-based music recommendations with Spotify previews.

---

### 5. README – Progress & Issues

#### **Progress**
- All planned features for Milestone 2 are implemented and functional.
- UI/UX has been overhauled for clarity, compactness, and responsiveness.
- Azure and Spotify integrations are robust, with fallback for demo mode.
- All major client feedback and bug reports have been addressed.

#### **Known Issues**
- Some Spotify tracks may not have a preview available due to API limitations.
- Azure OpenAI quota or deployment issues may require fallback to placeholder/demo mode.
- If you encounter API errors, double-check your credentials and deployment names.

---

## Contact & Feedback
For questions, feedback, or issues, please open an issue or contact the developer.

# Installation Instructions

Follow these simple steps to set up and run MoodMusic locally:

## Setup Instructions

### 1. Clone the repository:
```bash
git clone https://github.com/Anshul391/mood_music.git
cd mood_music
```

### 2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 4. Add your API keys:
Store your secrets in `.streamlit/secrets.toml`. Example:
```toml
[azure_openai]
api_key = "your-azure-openai-key"
endpoint = "https://your-openai-endpoint.openai.azure.com/"
deployment_name = "gpt35-mood"
api_version = "2024-02-15-preview"

[azure_cv]
api_key = "your-cv-api-key"
endpoint = "https://your-cv-endpoint.cognitiveservices.azure.com/"

[spotify]
client_id = "your-spotify-client-id"
client_secret = "your-spotify-client-secret"
```

### 5. Run the app:
```bash
python -m streamlit run moodmusic_azure_spotify_app.py
```

# Expected Outcome

The goal of this project is to create a seamless, intelligent tool that enhances content creation by automatically recommending background music that matches the mood and context of the user's media. By the end of development, the app should:

## Core Outcomes/Features

### Effortless Song Discovery
- Users can upload media and receive instant, relevant background music suggestions without manual searching.

### Mood-Matching Recommendations
- The app accurately analyzes the media to detect mood, tone, or tempo and recommends music that enhances the overall feel.

### Intelligence & Relevance
- Suggestions are personalized to the media's emotional or aesthetic characteristics.
- Songs are pulled from a curated or API-connected library (e.g., Spotify Preview API).

## Target Users & Their Needs

- **Social Media Creators**
- **Students / Hobbyists**
- **Content Designers / Marketers**

## User Impact

- Speeds up the creative process for social media posts, reels, and promotional content.
- Improves the emotional engagement of content through well-matched background music.
- Helps creators stay on-trend with music choices that resonate with their audience.

---

## Screen:
![Mood Music UI](https://raw.githubusercontent.com/Anshul391/mood_music/main/MoodMusic1.png)

## User Flow

1. User uploads an image  
2. Selects options like theme, language, genre, etc.  
3. Image is analyzed with preferences  
4. Music mood is generated using Azure OpenAI  
5. Spotify Preview API fetches top matching tracks  
6. Music previews are embedded and linked to Spotify  

---

# Timeline

| Week | Focus Area                | Key Tasks                                                                 |
|------|---------------------------|---------------------------------------------------------------------------|
| 1    | Planning & Research       | Finalize MVP features, research music APIs, choose tech stack             |
| 2    | Architecture & UI/UX     | Design wireframes, plan backend/database, map user flow                   |
| 3    | Media Upload & Handling  | Build upload UI, set up backend media storage, implement validation, display preview |
| 4    | Media Analysis Engine (1) | Analyze image for mood (visual), integrate ML libraries or mood-detection models |
| 5    | Media Analysis Engine (2) | Add audio/scene analysis, map mood to music genres                        |
| 6    | Music Recommendation      | Integrate music API or dataset, match media to songs, display suggestions |
| 7    | Preview System            | Enable audio-overlay previews, sync music with video, let users choose preferred track |
| 8    | Testing and Feedback      | Internal QA, limited beta test, gather user feedback, fix bugs, and test with users |
| 9    | Launch                    | Final UI polish, build landing page, prep launch content, go live on platforms |

---

# Challenges

| Challenge                | Details                                                                 |
|-------------------------|-------------------------------------------------------------------------|
| Mood Detection Accuracy | Interpreting mood from visuals/audio is subjective and depends on high-quality training data and models. |
| Handling Diverse Media  | Users may upload anything from vibrant reels to grayscale photos — accurate analysis across formats might be tricky. |
| Feature Implementation  | Real-time music playing with full or part audio and volume control.     |
| Scene Understanding     | Automatically identifying "what's happening" in an image (e.g., beach scene vs. party) will require advanced ML/AI techniques. |

# Contact Info
- Developer: Rishabh Kumar  
  Email: rkumar23@uw.edu  
  GitHub: [rishabhk22](https://github.com/rishabhk22)

- Client: Anshul Prakash  
  Email: anshul39@uw.edu  
  GitHub: [anshul391](https://github.com/anshul391)

---

## Next Steps

- **Spotify Integration:**
  - Continue to test and ensure Spotify API search and preview are working for a wide range of songs and user preferences.
  - Monitor for any API rate limits or credential issues.

- **Azure OpenAI Quota:**
  - Await quota approval for Azure OpenAI to enable full AI-powered mood detection for all users.
  - Once approved, remove or reduce reliance on placeholder/demo mode.

- **User Feedback:**
  - Gather more user feedback on UI/UX and music recommendation quality.
  - Iterate on design and features based on real user testing.

- **Further Enhancements:**
  - Add more personalization, playlist saving, or sharing features.
  - Explore additional music APIs or expand to video content.