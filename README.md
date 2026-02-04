# 🛍️ E-Com Video Insider

A powerful MVP tool for analyzing TikTok/Instagram/YouTube Shorts videos and generating Lazada-optimized remake scripts.

## 🎯 Features

- **Video Metadata Extraction**: Fetch video data (views, likes, comments, shares) via Apify API
- **AI-Powered Analysis**: Analyze video structure using Google Gemini 1.5 Flash API
- **Speech Transcription**: Extract speech from videos with timestamps using OpenAI Whisper API
- **Lazada Optimization**: Generate localized remake scripts for Lazada marketing
- **Export Functionality**: Export analysis results in JSON and Markdown formats
- **Password Protection**: Secure access with password authentication

## 🚀 Tech Stack

- **Frontend**: Streamlit
- **APIs**: Apify (TikTok Scraper), Google Generative AI (Gemini), OpenAI (Whisper)
- **Video Processing**: yt-dlp, ffmpeg
- **Language**: Python 3.11

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ecom-video-insider.git
cd ecom-video-insider
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
APIFY_API_TOKEN=your_apify_token_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional, for better transcription
```

### 4. Run the application

```bash
streamlit run app.py
```

## ☁️ Deploy to Streamlit Cloud

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository and branch
5. Set main file path: `app.py`
6. Click "Advanced settings" → "Secrets"
7. Add the following secrets:

```toml
APIFY_API_TOKEN = "your_apify_token_here"
GEMINI_API_KEY = "your_gemini_api_key_here"
OPENAI_API_KEY = "your_openai_api_key_here"  # Optional, for better transcription
APP_PASSWORD = "your_custom_password"
```

8. Click "Deploy"

### 3. Access your app

Your app will be available at: `https://your-app-name.streamlit.app`

## 🔐 Password Protection

The app is protected by a password. Default password is `admin123` (for local development).

**Important**: When deploying to Streamlit Cloud, set a custom password in Secrets:

```toml
APP_PASSWORD = "your_secure_password"
```

## 📖 Usage

1. Enter the access password
2. Paste a TikTok video URL
3. Click "🚀 Analyze Now"
4. View results in three tabs:
   - **Remake Brief**: High-level adaptation suggestions
   - **Logic Breakdown**: Detailed structure analysis
   - **口播摘录**: Speech transcript with timestamps
5. Export results using the download buttons

## 🛠️ Project Structure

```
ecom-video-insider/
├── app.py                  # Main Streamlit application
├── src/
│   ├── tiktok_fetcher.py  # TikTok metadata fetcher (Apify)
│   ├── video_analyzer.py  # Video analysis (Gemini)
│   └── prompts.py         # System prompts
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 📝 API Keys

### Apify API Token
- Sign up at [Apify Console](https://console.apify.com/)
- Go to Settings → Integrations → API Token

### Google Gemini API Key
- Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
- Create a new API key

### OpenAI API Key (Optional, for better transcription)
- Visit [OpenAI Platform](https://platform.openai.com/api-keys)
- Create a new API key
- See [WHISPER_API_SETUP.md](./WHISPER_API_SETUP.md) for detailed setup guide

## 🤝 Contributing

This is an internal tool for Lazada off-site traffic acquisition and ad content operations.

## 📄 License

Private - Internal Use Only

## 👤 Author

DorisP
