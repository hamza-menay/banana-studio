import streamlit as st
from google import genai
from PIL import Image
import os
import datetime
import time
import io
import logging

# --- Configuration ---
API_KEY = "AIzaSyACIK4niRkFuyr09EvHUEzpbEDxtfbZRZE"

# Initialize the new Genai client
client = genai.Client(api_key=API_KEY)

# Use Nano Banana Pro (Gemini 3 Pro Image) for advanced image generation
MODEL_NAME = "gemini-3-pro-image-preview"

# Unified output folder (absolute path)
OUTPUT_DIR = "/Users/stableunit-hamza/Desktop/Image generator for content/generated_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Logging Setup ---
LOG_FILE = os.path.join(OUTPUT_DIR, "greenscreen_poses.log")
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

def force_square(image: Image.Image) -> Image.Image:
    """Crops image to 1:1 aspect ratio (center crop)."""
    width, height = image.size
    if width == height:
        return image

    size = min(width, height)
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size

    cropped = image.crop((left, top, right, bottom))
    logger.info(f"Cropped image from {width}x{height} to {size}x{size}")
    return cropped

def save_generated_image(image: Image.Image, index: int):
    """Saves the PIL image locally with a unique timestamped filename."""
    # Force 1:1 aspect ratio
    image = force_square(image)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"greenscreen_pose_{timestamp}_{index}.png")
    image.save(filename)
    logger.info(f"Image saved to: {filename}")
    return filename

# Variation modifiers to make each generation unique
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

def generate_chroma_character(reference_image, user_instructions, variation_index=0):
    """
    Sends the reference image and prompt to Gemini, requesting variations on green screen.
    """
    # Pick a variation modifier based on index
    variation_mod = VARIATION_MODIFIERS[variation_index % len(VARIATION_MODIFIERS)]

    logger.info(f"Starting generation with instructions: {user_instructions}")
    logger.info(f"Variation modifier: {variation_mod}")
    logger.debug(f"Reference image size: {reference_image.size}, mode: {reference_image.mode}")

    logger.debug(f"Using model: {MODEL_NAME}")

    # Build the prompt with green screen constraints and variation
    full_prompt = (
        "I am providing a reference image of a character. "
        f"Additional instructions: {user_instructions}. "
        f"VARIATION REQUEST: Generate the character with this specific pose/expression: {variation_mod}. "
        "Keep the EXACT same visual style, features, clothing, and design as the reference. "
        "CRITICAL REQUIREMENT: Place the character on a solid, uniform, bright neon green background (chroma key green, RGB 0,255,0). "
        "There must be no other objects, environment textures, or gradients in the background. "
        "The lighting on the character should be even and flat to minimize hard shadows on the green floor. "
        "The character must be completely isolated on the green screen. "
        "FRAMING REQUIREMENT: The ENTIRE character must be fully visible and CENTERED in the frame. "
        "NO part of the character (hands, feet, head, arms, accessories) should be cut off or extend outside the image boundaries. "
        "Leave adequate padding/margin around the character on all sides. "
        "OUTPUT FORMAT: The image MUST be a perfect square (1:1 aspect ratio)."
    )
    logger.debug(f"Full prompt: {full_prompt}")

    try:
        logger.info("Sending request to Gemini API...")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[full_prompt, reference_image],
        )
        logger.info("Response received from API")

        # Extract image from response parts
        for idx, part in enumerate(response.candidates[0].content.parts):
            logger.debug(f"Part {idx}: type={type(part)}")

            # Check for inline_data (base64 image bytes)
            if hasattr(part, 'inline_data') and part.inline_data:
                logger.info(f"Found inline_data in part {idx}")
                image_data = part.inline_data.data
                logger.debug(f"Image data size: {len(image_data)} bytes")
                img = Image.open(io.BytesIO(image_data))
                logger.info(f"Successfully created image: {img.size}, mode: {img.mode}")
                return img

        # If no image found, check for text response
        logger.warning("No image found in response parts")
        try:
            text = response.text
            if text:
                logger.warning(f"Model returned text instead of image: {text}")
                st.warning(f"Model returned text instead of image: {text}")
        except (ValueError, AttributeError) as ve:
            logger.error(f"Error accessing response.text: {ve}")
        return None

    except Exception as e:
        logger.error(f"Generation failed with exception: {type(e).__name__}: {e}", exc_info=True)
        st.error(f"Generation failed: {e}")
        return None

# --- Streamlit UI ---
st.set_page_config(page_title="Chroma Character Gen", page_icon="🟩")

logger.info("="*50)
logger.info("Application started")

st.title("🟩 Green Screen Character Generator")
st.markdown(
    "Upload a character image and generate variations on a solid green background, "
    "ready for easy isolation."
)

# Image upload
uploaded_file = st.file_uploader("Upload Character Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    reference_image = Image.open(uploaded_file)
    logger.info(f"Image uploaded: {uploaded_file.name}, size: {reference_image.size}")
    st.image(reference_image, caption="Reference Character", width=300)

    # Text input for additional instructions
    user_text = st.text_area(
        "Additional Instructions (optional):",
        height=80,
        placeholder="e.g., different pose, facing left, arms raised, sitting down..."
    )

    # Slider for number of variations
    num_images = st.slider("Number of variations to generate:", min_value=1, max_value=6, value=5)

    # Buttons side by side
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        generate_btn = st.button("🚀 Generate Variations", use_container_width=True)
    with col_btn2:
        stop_btn = st.button("🛑 Stop", on_click=stop_clicked, use_container_width=True)

    if generate_btn:
        reset_stop()  # Reset stop flag when starting
        logger.info(f"Generate button clicked. Requesting {num_images} variations.")
        logger.info(f"User instructions: {user_text or 'keep original style'}")

        cols = st.columns(min(num_images, 3))
        success_count = 0

        for i in range(num_images):
            # Check if stop was pressed
            if st.session_state.stop_generation:
                st.warning(f"Stopped after {success_count} image(s).")
                logger.info("Generation stopped by user")
                break

            col_idx = i % 3
            logger.info(f"--- Starting variation {i+1}/{num_images} ---")

            with cols[col_idx]:
                st.markdown(f"**Variation {i+1}**")
                with st.spinner("Generating..."):
                    generated_img = generate_chroma_character(reference_image, user_text or "keep original style", variation_index=i)

                if generated_img:
                    st.image(generated_img, use_container_width=True)
                    saved_path = save_generated_image(generated_img, i+1)
                    logger.info(f"Variation {i+1} saved to: {saved_path}")
                    st.caption(f"Saved: `{os.path.basename(saved_path)}`")
                    success_count += 1
                else:
                    logger.error(f"Variation {i+1} failed to generate")
                    st.error("Failed to generate.")

            time.sleep(0.5)

        if not st.session_state.stop_generation:
            logger.info(f"Generation complete. Success: {success_count}/{num_images}")
            if success_count > 0:
                st.success(f"Generated {success_count} images! Saved to: `{OUTPUT_DIR}`")
            else:
                st.error("Generation process completed, but no images were successfully created.")
