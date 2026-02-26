# Banana Studio

A Streamlit interface for the Gemini image generation API. Built for anyone who found the Gemini web app too limiting, one generation at a time with no reference images and no real control over what comes out.

Calling the API directly also means no watermarks on your outputs, which turned out to be a useful side effect.

---

## What's inside

**Text to Image** — Full control over the generation: 14 aspect ratios including ultra-wide options like 1:8 and 8:1, resolutions from 512px up to 4K, a thinking level toggle that lets the model reason longer before generating, and optional Google Search grounding so it can pull real-time context or visual references from the web. You can pass up to 14 reference images into a single request.

**Green Screen** — Generates your character in different poses on a solid chroma key green background, ready to key out in Premiere, DaVinci, or any editing tool that supports it.

**Scene Creator** — Takes a reference character and a scene description, rewrites the prompt with variations for each version, and places the character into different environments.

**Compositor** — Merges a character image onto a background. Aspect ratio is detected from the background dimensions and mapped automatically to the closest supported ratio.

---

## Setup

You need Python 3.9 or later.

### 1. Clone the repo and install dependencies

```bash
git clone https://github.com/yourusername/banana-studio.git
cd banana-studio
pip install -r requirements.txt
```

### 2. Get a Gemini API key

Go to [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey), sign in with a Google account, and create a new API key. Copy it.

### 3. Add your API key

The repo includes a `.env.example` file that looks like this:

```
GEMINI_API_KEY=YOUR-API-KEY-HERE
```

Duplicate that file, rename the copy to `.env`, and replace `YOUR-API-KEY-HERE` with the key you copied from AI Studio. The `.env` file is listed in `.gitignore` so it will never be pushed to GitHub — only `.env.example` gets committed, as a template.

**If you've never done this before:** in the `banana-studio` folder, right-click on `.env.example` and duplicate it. Rename the duplicate to `.env` (remove the `.example` part). Then open it in any text editor, replace `YOUR-API-KEY-HERE` with your actual key, and save. On Mac, if TextEdit is adding `.txt` at the end, go to Format → Make Plain Text before saving.

### 4. Run the app

```bash
streamlit run app.py
```

Or if you're on Mac and have the `run.sh` script:

```bash
bash run.sh
```

The app opens in your browser at `http://localhost:8501`. Generated images are saved to the `generated_images/` folder inside the project directory.

---

## Model

Runs on `gemini-3.1-flash-image-preview` (Nano Banana 2). The Scene Creator uses `gemini-2.5-pro-preview-05-06` for prompt rewriting, which requires the `google-genai` SDK. If you skip that dependency, everything else still works and Scene Creator falls back to using the original prompt.

---

## Notes

- Image search grounding is a Nano Banana 2 feature and requires the same API key.
- The compositor maps your background's pixel dimensions to the nearest supported aspect ratio automatically.
- Rate limits depend on your API tier. The app retries with backoff on 429 errors.
