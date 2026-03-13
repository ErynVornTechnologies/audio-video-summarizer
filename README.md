# 🎙️ Smart Audio/Video Summarizer Pro (AI-Powered)

Summarize any audio or video content using AI — podcasts, lectures, meetings, interviews, tutorials. One click, structured markdown output.

## 🌟 Features

- **Universal Summarizer**: Works with any audio/video content — not limited to meetings.
- **Multi-Provider LLM**: Choose from Gemini, OpenAI, Anthropic, LM Studio, or OpenRouter.
- **Audio Extraction**: Automatically extracts audio from video files (MP4, MKV, AVI, MOV).
- **Direct Audio Support**: Also accepts MP3, WAV, M4A, OGG, FLAC, WMA, AAC.
- **Multi-Language**: Generate summaries in English, Polish, German, Spanish, or French.
- **Modern GUI**: Professional dark-mode interface built with `customtkinter`.
- **Auto-Open Output**: The output folder opens automatically when done.
- **AI Agent Friendly**: Optimised for autonomous agents (Gemini, Claude, AntiGravity) to set up and run.

## 🛠️ Prerequisites

- Python 3.10+
- **FFmpeg** — required for audio extraction from video files
- An API key for at least one LLM provider

### Installing FFmpeg

**Windows:**
1. Download from [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg\bin\`
3. Add `C:\ffmpeg\bin` to your system `PATH`

**macOS:** `brew install ffmpeg`

**Linux:** `sudo apt update && sudo apt install ffmpeg`

## 🚀 Installation & Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/HappyBirdProduction/audio-video-summarizer.git
   cd audio-video-summarizer
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API Key:**
   - Copy `.env.example` to `.env`
   - Set your preferred `LLM_PROVIDER` and the corresponding API key:

   ```env
   LLM_PROVIDER=gemini
   GOOGLE_API_KEY=your-api-key-here
   ```

### Supported LLM Providers

| Provider | Transcription | Summarization | Notes |
| --- | --- | --- | --- |
| Google Gemini | ✅ Native (multimodal) | ✅ | Best experience — sends audio directly to AI |
| OpenAI | ✅ Whisper API | ✅ GPT | Two-step: Whisper transcribes → GPT summarizes |
| Anthropic | ⚠️ Needs OpenAI key | ✅ Claude | Uses Whisper for transcription, Claude for summary |
| LM Studio | ⚠️ Needs OpenAI key | ✅ Local | Summarization runs locally |
| OpenRouter | ⚠️ Needs OpenAI key | ✅ | Uses Whisper fallback for transcription |

## 🎮 How to Use

1. Run `python summarizer.py`
2. **Select Media File** — pick any audio or video file
3. **Choose Language** — select the language for the summary
4. **Click START SUMMARIZING** — summary saves to `output/` folder and opens automatically

## Troubleshooting

| Problem | Solution |
| --- | --- |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| FFmpeg not found | Install FFmpeg and add to PATH |
| Audio extraction fails | Make sure the media file is not corrupted |
| API error | Check your `.env` file — ensure the correct API key is set |

---
*Brought to you by [aiBlackBox](https://aiblackbox.co.uk/). Follow us on [LinkedIn](https://www.linkedin.com/in/kamil-krzysztof-nagorski/) for more AI toolkits.*
