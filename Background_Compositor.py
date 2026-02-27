import streamlit as st
from google import genai
from PIL import Image
import os
import io
import datetime
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialize the new Genai client
client = genai.Client(api_key=API_KEY)

# Use Nano Banana Pro (Gemini 3 Pro Image) for advanced image generation/editing
MODEL_NAME = "gemini-3-pro-image-preview"

# Unified output folder (absolute path)
OUTPUT_DIR = "/Users/stableunit-hamza/Desktop/Image generator for content/generated_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Session State for Stop Button ---
if 'stop_generation' not in st.session_state:
    st.session_state.stop_generation = False

def stop_clicked():
    st.session_state.stop_generation = True

def reset_stop():
    st.session_state.stop_generation = False

def save_generated_image(image: Image.Image):
    """Saves the PIL image locally with a unique timestamped filename."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"composite_{timestamp}.png")
    image.save(filename)
    return filename

def match_background_size(generated_img: Image.Image, background_img: Image.Image) -> Image.Image:
    """Resize generated image to match background dimensions exactly."""
    bg_width, bg_height = background_img.size
    gen_width, gen_height = generated_img.size

    if gen_width == bg_width and gen_height == bg_height:
        return generated_img

    # Resize to match background exactly
    resized = generated_img.resize((bg_width, bg_height), Image.Resampling.LANCZOS)
    return resized

def generate_composite_image(background_img, character_img):
    """
    Sends both images + prompt to Gemini to perform the edit.
    """
    try:
        # Get background dimensions to enforce aspect ratio
        bg_width, bg_height = background_img.size

        prompt = (
            "I have provided two images. "
            "The first image is a 'Background'. "
            "The second image is a 'Character'. "
            "CRITICAL REQUIREMENTS: "
            "1. DO NOT MODIFY THE BACKGROUND IN ANY WAY. The background must remain 100% identical - same colors, same details, same everything. "
            "2. Simply OVERLAY the Character on top of the Background. "
            "3. The Character should be realistically integrated with proper lighting and shadows that match the scene. "
            "4. NEVER place the Character in front of ANY text. Scan the entire background for text and avoid those areas completely. "
            "5. Place the Character in an empty area of the background where they fit naturally. "
            f"6. OUTPUT MUST MATCH THE EXACT ASPECT RATIO OF THE BACKGROUND: {bg_width}x{bg_height} pixels. "
            "7. The final image dimensions must be identical to the background image dimensions."
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, background_img, character_img],
        )

        # Extract image from response parts
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data
                return Image.open(io.BytesIO(image_data))

        # No image found, check for text
        try:
            return response.text
        except (AttributeError, ValueError):
            return None

    except Exception as e:
        st.error(f"An error occurred during generation: {e}")
        return None

# --- Streamlit UI ---
st.set_page_config(page_title="Background Compositor", page_icon="🍌")

st.title("🍌 Background Compositor")
st.markdown("Upload a **character** and a **background** - Gemini will insert the character creatively (avoiding text).")

# Two image uploaders
col_upload1, col_upload2 = st.columns(2)

with col_upload1:
    st.subheader("1. Character")
    char_file = st.file_uploader("Upload Character Image", type=["png", "jpg", "jpeg"], key="char")
    if char_file:
        character_image = Image.open(char_file)
        st.image(character_image, caption="Character", use_container_width=True)

with col_upload2:
    st.subheader("2. Background")
    bg_file = st.file_uploader("Upload Background Image", type=["png", "jpg", "jpeg"], key="bg")
    if bg_file:
        background_image = Image.open(bg_file)
        st.image(background_image, caption="Background", use_container_width=True)

# Only show generate button if both images uploaded
if char_file and bg_file:
    st.markdown("---")

    # Buttons side by side
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        generate_btn = st.button("✨ Composite Images", use_container_width=True)
    with col_btn2:
        stop_btn = st.button("🛑 Stop", on_click=stop_clicked, use_container_width=True)

    if generate_btn:
        reset_stop()

        if st.session_state.stop_generation:
            st.warning("Generation stopped.")
        else:
            with st.spinner("Gemini is analyzing the scene and inserting the character..."):
                result = generate_composite_image(background_image, character_image)

            if not st.session_state.stop_generation and result:
                st.subheader("Result")
                if isinstance(result, Image.Image):
                    # Ensure output matches background dimensions
                    result = match_background_size(result, background_image)
                    st.image(result, caption="Generated Composite", use_container_width=True)
                    saved_path = save_generated_image(result)
                    st.caption(f"Saved: `{os.path.basename(saved_path)}`")
                    st.success(f"Saved to: `{OUTPUT_DIR}`")
                elif isinstance(result, str):
                    st.warning("The model returned text instead of an image:")
                    st.write(result)
                else:
                    st.error("Unexpected response format.")
