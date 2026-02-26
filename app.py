import streamlit as st
from PIL import Image
import os
import io
import datetime
import time
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

# ============================================
# CONFIGURATION
# ============================================
API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL = "gemini-3.1-flash-image-preview"  # Nano Banana 2
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

TEXT_MODEL = "gemini-2.5-pro-preview-05-06"
try:
    from google import genai
    client = genai.Client(api_key=API_KEY)
    HAS_SDK = True
except:
    HAS_SDK = False
    client = None

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(page_title="Banana Studio", page_icon="🍌", layout="wide")

# ============================================
# THEME & CSS
# ============================================
# st.html() (Streamlit 1.37+) properly injects <style> tags globally.
# st.markdown(unsafe_allow_html=True) strips <style> in newer versions,
# causing CSS to render as visible text — hence the fallback.
_CSS_BLOCK = """
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,400&display=swap" rel="stylesheet">
<style>

:root {
    --bg:         #0a0a0d;
    --surface:    #111116;
    --surface-2:  #18181f;
    --border:     rgba(255,255,255,0.06);
    --border-hover: rgba(255,255,255,0.14);
    --accent:     #f0b429;
    --accent-dark:#c48f1f;
    --text:       #dddde8;
    --text-muted: #60607a;
    --success:    #34d399;
    --error:      #f87171;
}

/* ---- Base ---- */
.stApp {
    background-color: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
}

.main .block-container {
    padding: 2.5rem 3rem 4rem 3rem;
    max-width: 1100px;
}

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background-color: #0d0d12 !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] > div {
    padding-top: 2rem;
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown span {
    color: var(--text-muted) !important;
    font-size: 0.78rem;
}

/* ---- Typography ---- */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
    letter-spacing: -0.02em;
}

h1 { font-weight: 700 !important; font-size: 1.8rem !important; margin-bottom: 0.25rem !important; }
h2 { font-weight: 600 !important; font-size: 1.2rem !important; }
h3 { font-weight: 600 !important; font-size: 1rem !important; }

p, li, span, label { color: var(--text) !important; }

.stCaption, [data-testid="stCaptionContainer"] p {
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
}

/* ---- Sidebar nav radio ---- */
[data-testid="stSidebar"] .stRadio > label {
    display: none;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    gap: 0.1rem;
    display: flex;
    flex-direction: column;
}

[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    transition: background 0.15s;
    cursor: pointer;
}

[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
    background: var(--surface-2) !important;
}

[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] span {
    color: var(--text-muted) !important;
    font-size: 0.88rem;
}

/* ---- Buttons ---- */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    padding: 0.45rem 1.1rem !important;
    transition: all 0.15s !important;
    font-size: 0.88rem !important;
}

.stButton > button[kind="primary"] {
    background-color: var(--accent) !important;
    color: #0a0a0d !important;
    border: none !important;
}

.stButton > button[kind="primary"]:hover {
    background-color: var(--accent-dark) !important;
    color: #0a0a0d !important;
}

.stButton > button:not([kind="primary"]) {
    background-color: var(--surface-2) !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border) !important;
}

.stButton > button:not([kind="primary"]):hover {
    border-color: var(--border-hover) !important;
    color: var(--text) !important;
}

/* ---- Inputs ---- */
.stTextInput input,
.stTextArea textarea {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(240,180,41,0.12) !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: var(--text-muted) !important;
}

/* ---- Selectbox ---- */
.stSelectbox [data-baseweb="select"] > div {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
}

.stSelectbox [data-baseweb="select"] > div:hover {
    border-color: var(--border-hover) !important;
}

/* Selectbox dropdown menu */
[data-baseweb="popover"] [data-baseweb="menu"] {
    background-color: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}

[data-baseweb="popover"] li {
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-baseweb="popover"] li:hover {
    background-color: var(--surface) !important;
}

/* ---- Labels ---- */
.stTextInput > label,
.stTextArea > label,
.stSelectbox > label,
.stSlider > label,
.stFileUploader > label,
.stCheckbox > label span,
.stRadio > label {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    font-weight: 400 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ---- Slider ---- */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background-color: var(--accent) !important;
    border-color: var(--accent) !important;
}

.stSlider [data-baseweb="slider"] div[data-baseweb="slider-track-fill"] {
    background-color: var(--accent) !important;
}

/* ---- Checkboxes ---- */
.stCheckbox [data-baseweb="checkbox"] div {
    background-color: var(--surface) !important;
    border-color: var(--border-hover) !important;
}

.stCheckbox [data-baseweb="checkbox"][aria-checked="true"] div {
    background-color: var(--accent) !important;
    border-color: var(--accent) !important;
}

/* ---- File uploader ---- */
[data-testid="stFileUploader"] {
    background-color: var(--surface) !important;
    border: 1px dashed var(--border-hover) !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
}

[data-testid="stFileUploader"] section {
    border: none !important;
    background: transparent !important;
}

[data-testid="stFileUploader"] button {
    background-color: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
}

/* ---- Alerts ---- */
[data-testid="stAlert"] {
    border-radius: 6px !important;
    font-size: 0.88rem !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stSuccess [data-testid="stAlert"] {
    background-color: rgba(52,211,153,0.07) !important;
    border: 1px solid rgba(52,211,153,0.2) !important;
}

.stError [data-testid="stAlert"] {
    background-color: rgba(248,113,113,0.07) !important;
    border: 1px solid rgba(248,113,113,0.2) !important;
}

.stWarning [data-testid="stAlert"] {
    background-color: rgba(251,191,36,0.07) !important;
    border: 1px solid rgba(251,191,36,0.2) !important;
}

.stInfo [data-testid="stAlert"] {
    background-color: rgba(255,255,255,0.03) !important;
    border: 1px solid var(--border) !important;
}

/* ---- Dividers ---- */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.75rem 0 !important;
}

/* ---- Images ---- */
[data-testid="stImage"] img {
    border-radius: 8px !important;
}

/* ---- Spinner ---- */
.stSpinner > div {
    border-top-color: var(--accent) !important;
}

/* ---- Tables ---- */
table { border-collapse: collapse; width: 100%; }
thead tr { border-bottom: 1px solid var(--border); }
th {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 0.6rem 0.8rem;
    font-weight: 400 !important;
}
td {
    color: var(--text) !important;
    padding: 0.6rem 0.8rem;
    font-size: 0.88rem;
    border-bottom: 1px solid var(--border);
}

/* ---- Sidebar title ---- */
[data-testid="stSidebar"] h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    letter-spacing: 0.01em;
    margin-bottom: 1.5rem !important;
}

/* ---- Code blocks ---- */
code {
    background-color: var(--surface-2) !important;
    color: var(--accent) !important;
    border-radius: 4px !important;
    padding: 0.1em 0.4em !important;
    font-size: 0.82rem !important;
}

</style>
"""

try:
    st.html(_CSS_BLOCK)          # Streamlit 1.37+ — proper global style injection
except AttributeError:
    st.markdown(_CSS_BLOCK, unsafe_allow_html=True)  # fallback for older versions

# ============================================
# SESSION STATE
# ============================================
if 'stop_generation' not in st.session_state:
    st.session_state.stop_generation = False

def stop_clicked():
    st.session_state.stop_generation = True

def reset_stop():
    st.session_state.stop_generation = False

# ============================================
# API FUNCTIONS
# ============================================
def encode_image(image: Image.Image) -> dict:
    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return {
        "inlineData": {
            "mimeType": "image/png",
            "data": base64.b64encode(buffer.getvalue()).decode('utf-8')
        }
    }

def generate_image_raw(
    prompt: str,
    reference_images: list = None,
    aspect_ratio: str = "1:1",
    resolution: str = "2K",
    thinking_level: str = "minimal",
    use_web_search: bool = False,
    use_image_search: bool = False,
    max_retries: int = 3
) -> tuple[Image.Image, str]:

    contents = []
    if reference_images:
        for img in reference_images:
            contents.append(encode_image(img))
    contents.append({"text": prompt})

    generation_config = {
        "responseModalities": ["TEXT", "IMAGE"],
        "imageConfig": {
            "aspectRatio": aspect_ratio,
            "imageSize": resolution
        },
        "thinkingConfig": {
            "thinkingLevel": thinking_level
        }
    }

    payload = {
        "contents": [{"parts": contents}],
        "generationConfig": generation_config
    }

    tools = []
    if use_web_search and use_image_search:
        tools.append({"google_search": {"searchTypes": {"webSearch": {}, "imageSearch": {}}}})
    elif use_web_search:
        tools.append({"google_search": {}})
    elif use_image_search:
        tools.append({"google_search": {"searchTypes": {"imageSearch": {}}}})
    if tools:
        payload["tools"] = tools

    last_error = ""

    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{API_URL}?key={API_KEY}",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=120
            )

            if response.status_code == 429:
                wait_time = 2 ** attempt
                last_error = f"Rate limited. Retrying in {wait_time}s..."
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
                else:
                    return None, "Rate limit hit. Wait a moment and try again."

            response.raise_for_status()
            data = response.json()

            if "error" in data:
                last_error = f"API error: {data['error']}"
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return None, last_error

            if "candidates" in data and data["candidates"]:
                candidate = data["candidates"][0]
                finish_reason = candidate.get("finishReason", "")
                if finish_reason and finish_reason != "STOP":
                    last_error = f"Generation stopped: {finish_reason}"

                parts = candidate.get("content", {}).get("parts", [])
                for part in parts:
                    if "inlineData" in part:
                        image_data = base64.b64decode(part["inlineData"]["data"])
                        return Image.open(io.BytesIO(image_data)), ""
                    if "text" in part:
                        text = part["text"]
                        if "blocked" in text.lower() or "error" in text.lower():
                            last_error = f"API returned: {text[:100]}"

                if not parts:
                    last_error = "Empty response"
            else:
                last_error = "No candidates in response"

        except requests.exceptions.Timeout:
            last_error = "Request timed out"
        except requests.exceptions.RequestException as e:
            last_error = f"Request failed: {str(e)[:100]}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get('error', {}).get('message', e.response.text[:200])
                    last_error += f" — {error_detail}"
                except:
                    last_error += f" — {e.response.text[:200]}"
        except Exception as e:
            last_error = f"Unexpected error: {str(e)[:100]}"

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)

    return None, last_error

def generate_with_reference_raw(prompt: str, reference_image: Image.Image, aspect_ratio: str = None, resolution: str = None, thinking_level: str = "minimal") -> tuple[Image.Image, str]:
    kwargs = {"prompt": prompt, "reference_images": [reference_image], "thinking_level": thinking_level}
    if aspect_ratio:
        kwargs["aspect_ratio"] = aspect_ratio
    if resolution:
        kwargs["resolution"] = resolution
    return generate_image_raw(**kwargs)

def save_generated_image(image: Image.Image, prefix: str = "generated"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"{prefix}_{timestamp}.png")
    image.save(filename)
    return filename

def rewrite_prompt(original_prompt, variation_number):
    if not HAS_SDK:
        return original_prompt + f" (variation {variation_number})"
    rewrite_request = (
        "You are a creative prompt engineer for AI image generation. "
        f"Create variation #{variation_number} of this scene concept. "
        "COMPLETELY REWRITE with fresh interpretation. "
        "Change at least 3 elements: camera angle, lighting, character action/pose, environment, or mood. "
        "Return ONLY the new prompt, no explanations.\n\n"
        f"Original: {original_prompt}"
    )
    try:
        response = client.models.generate_content(model=TEXT_MODEL, contents=[rewrite_request])
        return response.text.strip()
    except:
        return original_prompt + f" (variation {variation_number})"

# ============================================
# SIDEBAR
# ============================================
st.sidebar.title("Banana Studio")

app_mode = st.sidebar.radio(
    "",
    [
        "Home",
        "Text to Image",
        "Green Screen",
        "Scene Creator",
        "Compositor",
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Nano Banana 2 · gemini-3.1-flash-image-preview")
st.sidebar.caption(f"Outputs → `generated_images/`")
if not HAS_SDK:
    st.sidebar.warning("SDK unavailable. Running on raw HTTP.")

# ============================================
# HOME
# ============================================
if app_mode == "Home":
    st.title("Banana Studio")
    st.caption("Nano Banana 2 — gemini-3.1-flash-image-preview")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Tools")
        st.markdown("""
| | |
|---|---|
| Text to Image | Generate from a prompt. Full control over resolution, aspect ratio, thinking level, and search grounding. |
| Green Screen | Generate your character in different poses on a chroma key background. |
| Scene Creator | Place a character in a custom scene. The prompt gets rewritten for each version. |
| Compositor | Drop a character onto any background. Aspect ratio is mapped automatically. |
""")

    with col_b:
        st.markdown("#### Model")
        st.markdown("""
| | |
|---|---|
| Resolutions | 512px · 1K · 2K · 4K |
| Aspect ratios | 14 options incl. 1:4, 4:1, 1:8, 8:1 |
| Thinking | minimal (fast) or High (better) |
| Grounding | web search + image search |
| Reference images | up to 14 per request |
""")

    st.markdown("---")
    st.markdown("#### Recent")

    try:
        files = sorted(os.listdir(OUTPUT_DIR), key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)
        image_files = [f for f in files if f.endswith(('.png', '.jpg', '.jpeg'))][:6]
        if image_files:
            cols = st.columns(min(len(image_files), 3))
            for i, img_file in enumerate(image_files):
                with cols[i % 3]:
                    st.image(os.path.join(OUTPUT_DIR, img_file), use_container_width=True)
                    st.caption(img_file)
        else:
            st.caption("Nothing here yet.")
    except Exception as e:
        st.error(f"Could not load images: {e}")

# ============================================
# TEXT TO IMAGE
# ============================================
elif app_mode == "Text to Image":
    st.title("Text to Image")

    ASPECT_RATIOS = ["1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9"]
    RESOLUTIONS = ["512px", "1K", "2K", "4K"]
    THINKING_LEVELS = ["minimal", "High"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        aspect_ratio = st.selectbox("Aspect ratio", ASPECT_RATIOS, index=0)
    with col2:
        resolution = st.selectbox("Resolution", RESOLUTIONS, index=2)
    with col3:
        thinking_level = st.selectbox("Thinking", THINKING_LEVELS, index=0,
                                      help="minimal = faster, High = more reasoning before generating")
    with col4:
        num_versions = st.slider("Versions", min_value=1, max_value=4, value=1)

    gcol1, gcol2 = st.columns(2)
    with gcol1:
        use_web_search = st.checkbox("Web search", help="Pull real-time info from Google Search")
    with gcol2:
        use_image_search = st.checkbox("Image search", help="Pull visual references from Google Image Search (Nano Banana 2 only)")

    st.markdown("---")
    st.markdown("#### Reference images")
    st.caption("Up to 14 images. Passed to the model before the prompt.")

    ref_files = st.file_uploader(
        "Upload references",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="text2img_refs"
    )

    reference_images = []
    if ref_files:
        ref_cols = st.columns(min(len(ref_files), 4))
        for i, ref_file in enumerate(ref_files):
            ref_img = Image.open(ref_file)
            reference_images.append(ref_img)
            with ref_cols[i % 4]:
                st.image(ref_img, caption=f"Ref {i+1}", use_container_width=True)

    st.markdown("---")

    prompt = st.text_area(
        "Prompt",
        height=110,
        placeholder="What do you want to generate?"
    )

    negative_prompt = st.text_input(
        "What to avoid",
        placeholder="blurry, low quality, distorted faces..."
    )

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        generate_btn = st.button("Generate", use_container_width=True, type="primary")
    with col_btn2:
        stop_btn = st.button("Stop", on_click=stop_clicked, use_container_width=True)

    if generate_btn:
        if not prompt:
            st.warning("Write a prompt first.")
        else:
            reset_stop()

            full_prompt = prompt
            if negative_prompt:
                full_prompt += f"\n\nAVOID: {negative_prompt}"

            search_parts = []
            if use_web_search: search_parts.append("web search")
            if use_image_search: search_parts.append("image search")
            search_str = f" · {', '.join(search_parts)}" if search_parts else ""
            st.caption(f"{resolution} · {aspect_ratio} · thinking: {thinking_level}{search_str}")

            result_cols = st.columns(min(num_versions, 2))
            success_count = 0

            for i in range(num_versions):
                if st.session_state.stop_generation:
                    st.warning(f"Stopped at {success_count}.")
                    break

                with result_cols[i % 2]:
                    st.caption(f"#{i+1}")
                    with st.spinner("Generating..."):
                        generated_img, error_msg = generate_image_raw(
                            prompt=full_prompt,
                            reference_images=reference_images if reference_images else None,
                            aspect_ratio=aspect_ratio,
                            resolution=resolution,
                            thinking_level=thinking_level,
                            use_web_search=use_web_search,
                            use_image_search=use_image_search,
                        )

                        if generated_img:
                            st.image(generated_img, use_container_width=True)
                            saved_path = save_generated_image(generated_img, f"text2img_v{i+1}")
                            st.caption(f"{generated_img.size[0]}×{generated_img.size[1]} · {os.path.basename(saved_path)}")
                            success_count += 1
                        else:
                            st.error(error_msg)

                if i < num_versions - 1:
                    time.sleep(1.5)

            if not st.session_state.stop_generation and success_count > 0:
                st.success(f"{success_count} image{'s' if success_count > 1 else ''} saved.")

# ============================================
# GREEN SCREEN
# ============================================
elif app_mode == "Green Screen":
    st.title("Green Screen")
    st.caption("Generates your character in different poses on a chroma key background.")

    VARIATION_MODIFIERS = [
        "mouth open, happy expression, arms raised in excitement",
        "mouth closed, calm neutral expression, arms at sides",
        "looking to the left, slight smile, one hand on hip",
        "looking to the right, surprised expression, hands up",
        "sitting pose, relaxed expression, legs crossed",
        "action pose, determined expression, pointing forward",
        "waving hello, friendly smile, one arm raised",
        "thumbs up gesture, confident grin, chest puffed out",
        "thinking pose, hand on chin, curious expression",
        "crossed arms, smirking, cool confident stance",
        "jumping pose, excited expression, arms spread wide",
        "shy pose, looking down slightly, hands behind back",
    ]

    uploaded_file = st.file_uploader("Character", type=["png", "jpg", "jpeg"], key="greenscreen")

    if uploaded_file:
        reference_image = Image.open(uploaded_file)
        st.image(reference_image, width=280)

        user_text = st.text_area(
            "Extra notes",
            height=80,
            placeholder="Different pose, facing left, arms raised..."
        )

        num_images = st.slider("Variations", min_value=1, max_value=6, value=5, key="gs_num")

        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            generate_btn = st.button("Generate", use_container_width=True, type="primary")
        with col_btn2:
            stop_btn = st.button("Stop", on_click=stop_clicked, use_container_width=True)

        if generate_btn:
            reset_stop()
            cols = st.columns(min(num_images, 3))
            success_count = 0

            for i in range(num_images):
                if st.session_state.stop_generation:
                    st.warning(f"Stopped at {success_count}.")
                    break

                variation_mod = VARIATION_MODIFIERS[i % len(VARIATION_MODIFIERS)]
                full_prompt = (
                    "I am providing a reference image of a character. "
                    f"Additional instructions: {user_text or 'keep original style'}. "
                    f"VARIATION REQUEST: Generate the character with this specific pose/expression: {variation_mod}. "
                    "Keep the EXACT same visual style, features, clothing, and design as the reference. "
                    "CRITICAL REQUIREMENT: Place the character on a solid, uniform, bright neon green background (chroma key green, RGB 0,255,0). "
                    "There must be no other objects, environment textures, or gradients in the background. "
                    "The lighting on the character should be even and flat to minimize hard shadows on the green floor. "
                    "The character must be completely isolated on the green screen. "
                    "FRAMING REQUIREMENT: The ENTIRE character must be fully visible and CENTERED in the frame. "
                    "NO part of the character should be cut off or extend outside the image boundaries. "
                    "OUTPUT FORMAT: The image MUST be a perfect square (1:1 aspect ratio)."
                )

                with cols[i % 3]:
                    st.caption(f"#{i+1}")
                    with st.spinner("Generating..."):
                        generated_img, error_msg = generate_with_reference_raw(
                            prompt=full_prompt,
                            reference_image=reference_image,
                            aspect_ratio="1:1",
                            resolution="2K"
                        )

                        if generated_img:
                            width, height = generated_img.size
                            if width != height:
                                size = min(width, height)
                                left = (width - size) // 2
                                top = (height - size) // 2
                                generated_img = generated_img.crop((left, top, left + size, top + size))
                            st.image(generated_img, use_container_width=True)
                            saved_path = save_generated_image(generated_img, f"greenscreen_{i+1}")
                            st.caption(os.path.basename(saved_path))
                            success_count += 1
                        else:
                            st.error(error_msg)

                if i < num_images - 1:
                    time.sleep(1.5)

            if not st.session_state.stop_generation and success_count > 0:
                st.success(f"{success_count} image{'s' if success_count > 1 else ''} saved.")

# ============================================
# SCENE CREATOR
# ============================================
elif app_mode == "Scene Creator":
    st.title("Scene Creator")
    st.caption("Places your character in a custom scene. The prompt gets rewritten for each version.")

    uploaded_file = st.file_uploader("Character", type=["png", "jpg", "jpeg"], key="scene")

    if uploaded_file:
        reference_image = Image.open(uploaded_file)
        st.image(reference_image, width=280)

        user_prompt = st.text_area(
            "Scene",
            height=100,
            placeholder="Riding a skateboard through a city, eating pizza at a rooftop..."
        )

        num_images = st.slider("Versions", min_value=1, max_value=3, value=3, key="scene_num")

        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            generate_btn = st.button("Generate", use_container_width=True, type="primary")
        with col_btn2:
            stop_btn = st.button("Stop", on_click=stop_clicked, use_container_width=True)

        if generate_btn:
            if not user_prompt:
                st.warning("Describe a scene first.")
            else:
                reset_stop()
                cols = st.columns(num_images)
                success_count = 0

                for i in range(num_images):
                    if st.session_state.stop_generation:
                        st.warning(f"Stopped at {success_count}.")
                        break

                    with cols[i]:
                        if i == 0:
                            current_prompt = user_prompt
                            st.caption(f"#{i+1} — original")
                        else:
                            with st.spinner("Rewriting prompt..."):
                                current_prompt = rewrite_prompt(user_prompt, i + 1)
                            st.caption(f"#{i+1} — rewritten")

                        if st.session_state.stop_generation:
                            break

                        with st.spinner("Generating..."):
                            full_prompt = (
                                "I am providing a reference image of a character. "
                                "Keep the EXACT same character design, visual style, and features. "
                                f"Generate a new image based on these instructions: {current_prompt}"
                            )
                            generated_img, error_msg = generate_with_reference_raw(
                                prompt=full_prompt,
                                reference_image=reference_image,
                                aspect_ratio="1:1",
                                resolution="2K"
                            )

                            if generated_img:
                                st.image(generated_img, use_container_width=True)
                                saved_path = save_generated_image(generated_img, f"scene_{i+1}")
                                st.caption(os.path.basename(saved_path))
                                success_count += 1
                            else:
                                st.error(error_msg)

                if not st.session_state.stop_generation and success_count > 0:
                    st.success(f"{success_count} scene{'s' if success_count > 1 else ''} saved.")

# ============================================
# COMPOSITOR
# ============================================
elif app_mode == "Compositor":
    st.title("Compositor")
    st.caption("Drop a character onto any background. Aspect ratio is mapped to the closest supported ratio automatically.")

    col_upload1, col_upload2 = st.columns(2)

    with col_upload1:
        st.markdown("#### Character")
        char_file = st.file_uploader("Upload", type=["png", "jpg", "jpeg"], key="comp_char")
        if char_file:
            character_image = Image.open(char_file)
            st.image(character_image, use_container_width=True)

    with col_upload2:
        st.markdown("#### Background")
        bg_file = st.file_uploader("Upload", type=["png", "jpg", "jpeg"], key="comp_bg")
        if bg_file:
            background_image = Image.open(bg_file)
            st.image(background_image, use_container_width=True)

    if char_file and bg_file:
        st.markdown("---")
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            generate_btn = st.button("Composite", use_container_width=True, type="primary")
        with col_btn2:
            stop_btn = st.button("Stop", on_click=stop_clicked, use_container_width=True)

        if generate_btn:
            reset_stop()

            bg_width, bg_height = background_image.size

            SUPPORTED_RATIOS = [
                ("1:1", 1/1), ("1:4", 1/4), ("1:8", 1/8),
                ("2:3", 2/3), ("3:2", 3/2), ("3:4", 3/4),
                ("4:1", 4/1), ("4:3", 4/3), ("4:5", 4/5),
                ("5:4", 5/4), ("8:1", 8/1), ("9:16", 9/16),
                ("16:9", 16/9), ("21:9", 21/9),
            ]
            img_ratio = bg_width / bg_height
            aspect = min(SUPPORTED_RATIOS, key=lambda x: abs(x[1] - img_ratio))[0]

            max_dim = max(bg_width, bg_height)
            if max_dim <= 1024:
                resolution = "1K"
            elif max_dim <= 2048:
                resolution = "2K"
            else:
                resolution = "4K"

            prompt = (
                "I have provided two images. "
                "The first image is a 'Background'. "
                "The second image is a 'Character'. "
                "CRITICAL REQUIREMENTS: "
                "1. DO NOT MODIFY THE BACKGROUND IN ANY WAY. The background must remain 100% identical. "
                "2. Simply OVERLAY the Character on top of the Background. "
                "3. The Character should be realistically integrated with proper lighting and shadows. "
                "4. NEVER place the Character in front of ANY text. Scan for text and avoid those areas. "
                "5. Place the Character in an empty area where they fit naturally. "
                f"6. OUTPUT MUST MATCH THE EXACT ASPECT RATIO OF THE BACKGROUND: {bg_width}x{bg_height} pixels."
            )

            st.caption(f"{resolution} · aspect ratio {aspect} (from {bg_width}×{bg_height}px)")

            with st.spinner("Compositing..."):
                generated_img, error_msg = generate_image_raw(
                    prompt=prompt,
                    reference_images=[background_image, character_image],
                    aspect_ratio=aspect,
                    resolution=resolution
                )

                if generated_img:
                    st.image(generated_img, use_container_width=True)
                    saved_path = save_generated_image(generated_img, "composite")
                    st.caption(f"{generated_img.size[0]}×{generated_img.size[1]} · {os.path.basename(saved_path)}")
                else:
                    st.error(error_msg)
