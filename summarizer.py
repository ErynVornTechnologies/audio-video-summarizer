import os
import threading
import shutil
import requests
from dotenv import load_dotenv
import customtkinter as ctk
from PIL import Image
from tkinter import filedialog, messagebox
import webbrowser
from moviepy import VideoFileClip

# Load environment variables
load_dotenv()

# ===== LLM PROVIDER CONFIGURATION =====
# Set LLM_PROVIDER in your .env file or change here directly.
# Supported: "gemini", "openai", "anthropic", "lmstudio", "openrouter"
# NOTE: For audio transcription, Gemini uses native multimodal input.
#       OpenAI uses the Whisper API. Other providers require a separate
#       transcription step — the app will attempt text-based summarization.
PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

# API Keys — set these in your .env file
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LMSTUDIO_URL = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Model names per provider — customize as needed
MODELS = {
    "gemini": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    "openai": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "anthropic": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
    "lmstudio": os.getenv("LMSTUDIO_MODEL", "local-model"),
    "openrouter": os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash"),
}

LOGO_URL = "https://aiblackbox.co.uk/wp-content/uploads/2025/08/AIBLACKBOX-logonowe_.png"

# Appearance Configuration
ctk.set_appearance_mode("Dark")


def transcribe_and_summarize(audio_path, language, log_fn):
    """Transcribe audio and generate a summary using the configured provider."""
    model_name = MODELS.get(PROVIDER, "")

    summary_prompt = (
        f"Please provide a detailed summary of the following audio/video content in {language}. "
        "Include:\n1. Main Topic / Title\n2. Key Points & Highlights\n3. Important Details & Takeaways\n4. Conclusions (if any)."
    )

    if PROVIDER == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(model_name)
        log_fn(f"Uploading audio to Gemini ({model_name})...")
        audio_file = genai.upload_file(path=audio_path)
        response = model.generate_content([summary_prompt, audio_file])
        return response.text

    elif PROVIDER == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        log_fn("Transcribing audio via Whisper API...")
        with open(audio_path, "rb") as f:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
        log_fn("Generating summary via GPT...")
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": f"{summary_prompt}\n\nTranscript:\n{transcript.text}"}]
        )
        return response.choices[0].message.content

    elif PROVIDER in ("lmstudio", "openrouter"):
        from openai import OpenAI
        if PROVIDER == "lmstudio":
            client = OpenAI(base_url=LMSTUDIO_URL, api_key="lm-studio")
        else:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
        log_fn(f"NOTE: {PROVIDER} does not support audio transcription.")
        log_fn("Attempting Whisper transcription via OpenAI if key available...")
        transcript_text = ""
        if OPENAI_API_KEY:
            whisper_client = OpenAI(api_key=OPENAI_API_KEY)
            with open(audio_path, "rb") as f:
                transcript = whisper_client.audio.transcriptions.create(model="whisper-1", file=f)
            transcript_text = transcript.text
        else:
            transcript_text = "[Transcription not available — set OPENAI_API_KEY for Whisper support]"
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": f"{summary_prompt}\n\nTranscript:\n{transcript_text}"}]
        )
        return response.choices[0].message.content

    elif PROVIDER == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        log_fn("NOTE: Anthropic does not support audio transcription directly.")
        log_fn("Attempting Whisper transcription via OpenAI if key available...")
        transcript_text = ""
        if OPENAI_API_KEY:
            from openai import OpenAI
            whisper_client = OpenAI(api_key=OPENAI_API_KEY)
            with open(audio_path, "rb") as f:
                transcript = whisper_client.audio.transcriptions.create(model="whisper-1", file=f)
            transcript_text = transcript.text
        else:
            transcript_text = "[Transcription not available — set OPENAI_API_KEY for Whisper support]"
        response = client.messages.create(
            model=model_name,
            max_tokens=4096,
            messages=[{"role": "user", "content": f"{summary_prompt}\n\nTranscript:\n{transcript_text}"}]
        )
        return response.content[0].text

    else:
        raise ValueError(f"Unknown LLM provider: {PROVIDER}. Use: gemini, openai, anthropic, lmstudio, openrouter")


class AudioVideoSummarizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Audio/Video Summarizer Pro")
        self.geometry("850x1000")
        self.resizable(False, False)
        
        self.bg_color = "#20212b"
        self.container_color = "#363847"
        self.accent_color = "#34ade1"
        self.text_color = "#ffffff"
        self.gray_text = "#9ea0a9"
        
        self.configure(fg_color=self.bg_color)

        self.input_file = ""
        self.selected_language = "English"
        
        self.create_widgets()

    def create_widgets(self):
        try:
            logo_response = requests.get(LOGO_URL, stream=True)
            img = Image.open(logo_response.raw)
            logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(150, 150))
            self.label_logo = ctk.CTkLabel(self, image=logo_img, text="")
        except Exception:
            self.label_logo = ctk.CTkLabel(self, text="AI BlackBox", font=("Montserrat", 40, "bold"))
            
        self.label_logo.pack(pady=(50, 10))
        self.label_logo.bind("<Button-1>", lambda e: webbrowser.open("https://aiblackbox.co.uk/"))
        self.label_logo.configure(cursor="hand2")

        self.lbl_header = ctk.CTkLabel(
            self, text="AI-Powered Audio/Video Summarizer", 
            font=("Montserrat", 26), text_color=self.text_color
        )
        self.lbl_header.pack(pady=(0, 40))

        self.settings_container = ctk.CTkFrame(self, fg_color=self.container_color, corner_radius=15, width=720, height=220)
        self.settings_container.pack(pady=10, padx=65, fill="x")
        self.settings_container.pack_propagate(False)

        self.file_frame = ctk.CTkFrame(self.settings_container, fg_color="transparent")
        self.file_frame.pack(fill="x", pady=(25, 10), padx=40)
        
        self.btn_input = ctk.CTkButton(
            self.file_frame, text="Select Media File", command=self.select_input, 
            width=220, height=38, font=("Roboto", 18),
            fg_color=self.accent_color, hover_color="#298cb5", corner_radius=8
        )
        self.btn_input.pack(side="left")
        
        self.lbl_input = ctk.CTkLabel(self.file_frame, text="No file selected", font=("Roboto", 18), text_color=self.gray_text)
        self.lbl_input.pack(side="right", padx=10)

        self.lang_frame = ctk.CTkFrame(self.settings_container, fg_color="transparent")
        self.lang_frame.pack(fill="x", pady=10, padx=40)
        
        ctk.CTkLabel(self.lang_frame, text="Summary Language:", font=("Roboto", 18), text_color=self.text_color).pack(side="left")
        
        self.combo_lang = ctk.CTkComboBox(
            self.lang_frame, values=["English", "Polish", "German", "Spanish", "French"],
            font=("Roboto", 16), width=200, command=self.set_language
        )
        self.combo_lang.pack(side="right")
        self.combo_lang.set("English")

        self.progress_bar = ctk.CTkProgressBar(self, width=650, height=10, fg_color="#3d3f4b", progress_color=self.accent_color)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(40, 10))

        self.lbl_status = ctk.CTkLabel(self, text="READY", font=("Montserrat", 24), text_color=self.text_color)
        self.lbl_status.pack(pady=5)

        self.log_box = ctk.CTkTextbox(
            self, width=720, height=130, font=("Consolas", 12), 
            fg_color="#000000", text_color="#4ade80", border_width=0, corner_radius=10
        )
        self.log_box.pack(pady=20, padx=65)
        self.log_box.configure(state="disabled")

        self.btn_start = ctk.CTkButton(
            self, text="START SUMMARIZING", command=self.start_process_thread, 
            width=300, height=60, font=("Montserrat", 24), 
            fg_color=self.accent_color, hover_color="#298cb5", corner_radius=10
        )
        self.btn_start.pack(pady=(10, 50))

        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(side="bottom", pady=20)

        self.lbl_disclaimer = ctk.CTkLabel(
            self.footer_frame, 
            text="Disclaimer: This tool uses AI to transcribe and summarize audio/video content. Results may vary.", 
            font=("Roboto", 10), text_color=self.gray_text
        )
        self.lbl_disclaimer.pack()

        self.links_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.links_frame.pack(pady=(5, 0))

        self.lbl_f1 = ctk.CTkLabel(self.links_frame, text="Brought to you by ", font=("Roboto", 11), text_color=self.gray_text)
        self.lbl_f1.pack(side="left")
        
        self.lbl_link1 = ctk.CTkLabel(self.links_frame, text="AiBlackBox.", font=("Roboto", 11, "bold"), text_color=self.accent_color, cursor="hand2")
        self.lbl_link1.pack(side="left")
        self.lbl_link1.bind("<Button-1>", lambda e: webbrowser.open("https://aiblackbox.co.uk/"))

        self.lbl_f2 = ctk.CTkLabel(self.links_frame, text=" Follow us for more AI toolkits at ", font=("Roboto", 11), text_color=self.gray_text)
        self.lbl_f2.pack(side="left")

        self.lbl_link2 = ctk.CTkLabel(self.links_frame, text="LinkedIn.", font=("Roboto", 11, "bold"), text_color=self.accent_color, cursor="hand2")
        self.lbl_link2.pack(side="left")
        self.lbl_link2.bind("<Button-1>", lambda e: webbrowser.open("https://www.linkedin.com/in/kamil-krzysztof-nagorski/"))

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def set_language(self, lang):
        self.selected_language = lang

    def select_input(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("All media files", "*.mp4 *.mkv *.avi *.mov *.mp3 *.wav *.m4a *.ogg *.flac *.wma *.aac"),
            ("Video files", "*.mp4 *.mkv *.avi *.mov"),
            ("Audio files", "*.mp3 *.wav *.m4a *.ogg *.flac *.wma *.aac"),
        ])
        if file_path:
            self.input_file = file_path
            self.lbl_input.configure(text=os.path.basename(file_path))

    def start_process_thread(self):
        if not self.input_file:
            messagebox.showwarning("Warning", "Please select a file first.")
            return
        self.btn_start.configure(state="disabled", text="PROCESSING...")
        self.progress_bar.set(0)
        threading.Thread(target=self.process_media, daemon=True).start()

    def process_media(self):
        try:
            temp_audio = "temp_audio.mp3"
            
            self.after(0, lambda: (self.progress_bar.set(0.2), self.lbl_status.configure(text="EXTRACTING AUDIO...")))
            self.log("Preparing audio...")
            
            if self.input_file.lower().endswith(('.mp4', '.mkv', '.mov', '.avi')):
                self.log("Extracting audio from video...")
                video = VideoFileClip(self.input_file)
                video.audio.write_audiofile(temp_audio, logger=None)
                video.close()
            else:
                self.log("Audio file detected, using directly...")
                shutil.copy(self.input_file, temp_audio)

            self.after(0, lambda: (self.progress_bar.set(0.5), self.lbl_status.configure(text="ANALYZING VIA AI...")))
            self.log(f"Processing with {PROVIDER} ({MODELS.get(PROVIDER, '')})...")
            
            summary_text = transcribe_and_summarize(temp_audio, self.selected_language, self.log)

            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            output_file = os.path.join(output_dir, f"{base_name}_summary.md")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(summary_text)
            
            self.log(f"SUCCESS: Summary saved to output/{base_name}_summary.md")
            
            if os.path.exists(temp_audio):
                os.remove(temp_audio)

            import subprocess
            subprocess.Popen(f'explorer "{output_dir}"')

            self.after(0, lambda: (
                self.progress_bar.set(1),
                self.lbl_status.configure(text="FINISHED!"),
                self.btn_start.configure(state="normal", text="START SUMMARIZING"),
                messagebox.showinfo("Success", f"Summary saved to:\n{output_file}\n\nOutput folder has been opened.")
            ))

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            self.after(0, lambda e=e: (
                self.btn_start.configure(state="normal", text="START SUMMARIZING"),
                self.lbl_status.configure(text="ERROR"),
                messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            ))

if __name__ == "__main__":
    app = AudioVideoSummarizerApp()
    app.mainloop()
