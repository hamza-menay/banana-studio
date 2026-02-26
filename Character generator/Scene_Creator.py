import streamlit as st
from google import genai
from PIL import Image
import os
import datetime
import io
import logging

# --- Configuration ---
API_KEY = "AIzaSyACIK4niRkFuyr09EvHUEzpbEDxtfbZRZE"

# Initialize the new Genai client
client = genai.Client(api_key=API_KEY)

# Models
IMAGE_MODEL = "gemini-3-pro-image-preview"  # Nano Banana Pro for image generation
TEXT_MODEL = "gemini-2.5-pro-preview-05-06"  # Gemini 2.5 Pro for prompt rewriting

# Unified output folder (absolute path)
OUTPUT_DIR = "/Users/stableunit-hamza/Desktop/Image generator for content/generated_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Logging Setup ---
LOG_FILE = os.path.join(OUTPUT_DIR, "scene_creator.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Session State for Stop Button ---
if 'stop_generation' not in st.session_state:
    st.session_state.stop_generation = False

def stop_clicked():
    st.session_state.stop_generation = True

def reset_stop():
    st.session_state.stop_generation = False

# --- Helper Functions ---

def save_generated_image(image: Image.Image, index: int):
    """Saves the PIL image locally with a unique timestamped filename."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"scene_{timestamp}_{index}.png")
    image.save(filename)
    logger.info(f"Image saved to: {filename}")
    return filename

def rewrite_prompt(original_prompt, variation_number):
    """
    Uses Gemini 2.5 Pro to completely rewrite the prompt for variety.
    Each call produces a distinctly different interpretation.
    """
    rewrite_request = (
        "You are a creative prompt engineer for AI image generation. "
        f"I need variation #{variation_number} of this scene concept. "
        "COMPLETELY REWRITE this prompt with a fresh, creative interpretation. "
        "You MUST change at least 3 of these elements: "
        "- Camera angle (close-up, wide shot, bird's eye, low angle, etc.) "
        "- Time of day or lighting (dawn, sunset, night, dramatic lighting, etc.) "
        "- Character action or pose (different activity, emotion, gesture) "
        "- Environment details (weather, season, background elements) "
        "- Mood or atmosphere (dramatic, peaceful, energetic, mysterious) "
        "\n\nMake it VISUALLY DISTINCT from the original. "
        "Return ONLY the new prompt, no explanations.\n\n"
        f"Original prompt: {original_prompt}"
    )

    try:
        logger.info(f"Rewriting prompt for variation #{variation_number}")
        response = client.models.generate_content(
            model=TEXT_MODEL,
            contents=rewrite_request,
        )
        rewritten = response.text.strip()
        logger.info(f"Rewritten prompt: {rewritten}")
        return rewritten
    except Exception as e:
        logger.error(f"Prompt rewrite failed: {e}")
        return original_prompt + f" (variation {variation_number})"

def generate_from_prompt(reference_image, prompt):
    """
    Sends the reference image and prompt to Gemini for generation.
    """
    logger.info(f"Generating with prompt: {prompt}")
    logger.debug(f"Reference image size: {reference_image.size}, mode: {reference_image.mode}")

    full_prompt = (
        "I am providing a reference image of a character. "
        "Keep the EXACT same character design, visual style, and features. "
        f"Generate a new image based on these instructions: {prompt}"
    )

    try:
        logger.info("Sending request to Gemini API...")
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[full_prompt, reference_image],
        )
        logger.info("Response received from API")

        # Extract image from response parts
        for idx, part in enumerate(response.candidates[0].content.parts):
            if hasattr(part, 'inline_data') and part.inline_data:
                logger.info(f"Found inline_data in part {idx}")
                image_data = part.inline_data.data
                img = Image.open(io.BytesIO(image_data))
                logger.info(f"Successfully created image: {img.size}")
                return img

        # No image found
        logger.warning("No image found in response")
        try:
            text = response.text
            if text:
                logger.warning(f"Model returned text: {text}")
                st.warning(f"Model returned text instead of image: {text}")
        except (ValueError, AttributeError):
            pass
        return None

    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        st.error(f"Generation failed: {e}")
        return None

# --- Streamlit UI ---
st.set_page_config(page_title="Scene Creator", page_icon="✨")

logger.info("="*50)
logger.info("Scene Creator started")

st.title("✨ Scene Creator")
st.markdown(
    "Upload a character, describe a scene. "
    "**Image 1** uses your prompt. **Image 2 & 3** are AI-rewritten variations."
)

# Image upload
uploaded_file = st.file_uploader("Upload Character Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    reference_image = Image.open(uploaded_file)
    logger.info(f"Image uploaded: {uploaded_file.name}, size: {reference_image.size}")
    st.image(reference_image, caption="Reference Character", width=300)

    # Text prompt
    user_prompt = st.text_area(
        "Describe the scene:",
        height=100,
        placeholder="e.g., character riding a skateboard in a city, character eating pizza, character as a superhero..."
    )

    # Number of images
    num_images = st.slider("Number of images to generate:", min_value=1, max_value=3, value=3)

    # Buttons side by side
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        generate_btn = st.button("✨ Generate Images", use_container_width=True)
    with col_btn2:
        stop_btn = st.button("🛑 Stop", on_click=stop_clicked, use_container_width=True)

    if generate_btn:
        reset_stop()  # Reset stop flag when starting

        if not user_prompt:
            st.warning("Please enter a prompt describing what you want.")
        else:
            logger.info(f"Generate clicked. Original prompt: {user_prompt}, Count: {num_images}")

            cols = st.columns(num_images)
            success_count = 0

            for i in range(num_images):
                # Check if stop was pressed
                if st.session_state.stop_generation:
                    st.warning(f"Stopped after {success_count} image(s).")
                    logger.info("Generation stopped by user")
                    break

                logger.info(f"--- Generating image {i+1}/{num_images} ---")

                with cols[i]:
                    st.markdown(f"**Image {i+1}**")

                    # Image 1: Use original prompt
                    # Image 2, 3: Rewrite with Gemini 2.5 Pro
                    if i == 0:
                        current_prompt = user_prompt
                        st.caption(f"Original: {current_prompt[:80]}...")
                    else:
                        with st.spinner("AI rewriting prompt..."):
                            current_prompt = rewrite_prompt(user_prompt, i + 1)
                        st.caption(f"Rewritten: {current_prompt[:80]}...")

                    # Check stop again after prompt rewrite
                    if st.session_state.stop_generation:
                        break

                    with st.spinner("Generating image..."):
                        generated_img = generate_from_prompt(reference_image, current_prompt)

                    if generated_img:
                        st.image(generated_img, use_container_width=True)
                        saved_path = save_generated_image(generated_img, i+1)
                        st.caption(f"Saved: `{os.path.basename(saved_path)}`")
                        success_count += 1
                    else:
                        st.error("Failed to generate.")

            if not st.session_state.stop_generation:
                logger.info(f"Generation complete. Success: {success_count}/{num_images}")
                if success_count > 0:
                    st.success(f"Generated {success_count} images! Saved to: `{OUTPUT_DIR}`")
                else:
                    st.error("No images were generated.")
