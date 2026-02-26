# Nano Banana 2 — Gemini Image Generation API Documentation

> **"Nano Banana"** is the name for Gemini's native image generation capabilities. Gemini can generate and process images conversationally with text, images, or a combination of both.

---

## Model Overview

| Brand Name | Model ID | Best For |
|---|---|---|
| **Nano Banana 2** | `gemini-3.1-flash-image-preview` | High-efficiency, speed, high-volume use — **recommended default** |
| **Nano Banana Pro** | `gemini-3-pro-image-preview` | Professional asset production, complex instructions, advanced reasoning |
| **Nano Banana** | `gemini-2.5-flash-image` | Speed & efficiency, high-volume low-latency tasks |

All generated images include a **SynthID watermark**.

---

## Quick Start

### Text to Image (Python)

```python
from google import genai
from google.genai import types
from PIL import Image

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=["Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"],
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("generated_image.png")
```

### Text to Image (JavaScript)

```javascript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({});
const response = await ai.models.generateContent({
  model: "gemini-3.1-flash-image-preview",
  contents: "Create a picture of a nano banana dish in a fancy restaurant",
});

for (const part of response.candidates[0].content.parts) {
  if (part.text) console.log(part.text);
  else if (part.inlineData) {
    fs.writeFileSync("image.png", Buffer.from(part.inlineData.data, "base64"));
  }
}
```

### REST API

```bash
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Your prompt here"}]}],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"]
    }
  }'
```

---

## Image Editing (Text + Image → Image)

Send an image with a text prompt to edit, transform, or extend it.

```python
from PIL import Image

client = genai.Client()
image = Image.open("/path/to/image.png")

response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=["Add a wizard hat to the character", image],
)
```

---

## Multi-Turn Conversational Editing

Use chat sessions to iteratively refine images:

```python
from google import genai
from google.genai import types

client = genai.Client()
chat = client.chats.create(
    model="gemini-3.1-flash-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    )
)

response = chat.send_message("Create a vibrant infographic about photosynthesis")
# Then refine:
response2 = chat.send_message("Update this infographic to be in Spanish")
```

---

## New Features in Nano Banana 2 (Gemini 3.1 Flash Image)

### High-Resolution Output
Generate images up to **4K** resolution. Use uppercase 'K':
- `"512px"` — 0.5K (unique to Nano Banana 2)
- `"1K"` — 1024px
- `"2K"` — 2048px
- `"4K"` — 4096px

```python
config=types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    image_config=types.ImageConfig(
        aspect_ratio="16:9",
        image_size="2K",  # Must be uppercase K
    ),
)
```

### Extended Aspect Ratios (Nano Banana 2 exclusive)
New ultra-wide/tall ratios: `1:4`, `4:1`, `1:8`, `8:1`

Full list: `1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9`

### Thinking Level Control

```python
config=types.GenerateContentConfig(
    response_modalities=["IMAGE"],
    thinking_config=types.ThinkingConfig(
        thinking_level="High",   # "minimal" (default) or "High"
        include_thoughts=True     # Return thought images in response
    ),
)
```

> **Note:** Thinking tokens are billed regardless of `include_thoughts` setting.

### Google Image Search Grounding (Nano Banana 2 exclusive)

```python
config=types.GenerateContentConfig(
    response_modalities=["IMAGE"],
    tools=[
        types.Tool(google_search=types.GoogleSearch(
            search_types=types.SearchTypes(
                web_search=types.WebSearch(),
                image_search=types.ImageSearch()  # New: visual context from web
            )
        ))
    ]
)
```

**Display Requirements for Image Search:**
- Provide a link to the **containing webpage** (not the image file directly)
- Direct, single-click navigation to source page from any displayed images

### Up to 14 Reference Images

| Gemini 3.1 Flash Image | Gemini 3 Pro Image |
|---|---|
| Up to 10 object images (high-fidelity) | Up to 6 object images |
| Up to 4 character images (consistency) | Up to 5 character images |

```python
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=[
        "An office group photo making funny faces.",
        Image.open('person1.png'),
        Image.open('person2.png'),
        Image.open('person3.png'),
        Image.open('person4.png'),
    ],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(aspect_ratio="5:4", image_size="2K"),
    )
)
```

### Grounding with Google Search (Web)

```python
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents="Visualize the weather forecast for the next 5 days in San Francisco",
    config=types.GenerateContentConfig(
        response_modalities=['Text', 'Image'],
        image_config=types.ImageConfig(aspect_ratio="16:9"),
        tools=[{"google_search": {}}]
    )
)
```

---

## Resolution Tables

### Nano Banana 2 — 3.1 Flash Image Preview

| Aspect Ratio | 512px | 1K | 2K | 4K |
|---|---|---|---|---|
| 1:1 | 512×512 | 1024×1024 | 2048×2048 | 4096×4096 |
| 16:9 | 688×384 | 1376×768 | 2752×1536 | 5504×3072 |
| 9:16 | 384×688 | 768×1376 | 1536×2752 | 3072×5504 |
| 4:3 | 600×448 | 1200×896 | 2400×1792 | 4800×3584 |
| 3:4 | 448×600 | 896×1200 | 1792×2400 | 3584×4800 |
| 21:9 | 792×168 | 1584×672 | 3168×1344 | 6336×2688 |
| 1:4 | 256×1024 | 512×2048 | 1024×4096 | 2048×8192 |
| 4:1 | 1024×256 | 2048×512 | 4096×1024 | 8192×2048 |
| 1:8 | 192×1536 | 384×3072 | 768×6144 | 1536×12288 |
| 8:1 | 1536×192 | 3072×384 | 6144×768 | 12288×1536 |

### Nano Banana Pro — 3 Pro Image Preview

| Aspect Ratio | 1K | 2K | 4K |
|---|---|---|---|
| 1:1 | 1024×1024 | 2048×2048 | 4096×4096 |
| 16:9 | 1376×768 | 2752×1536 | 5504×3072 |
| 9:16 | 768×1376 | 1536×2752 | 3072×5504 |
| 21:9 | 1584×672 | 3168×1344 | 6336×2688 |

---

## Output Modality Configuration

```python
# Images only (no text in response)
config=types.GenerateContentConfig(response_modalities=['Image'])

# Both text and images (default)
config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE'])
```

---

## Thought Signatures (Multi-Turn)

When using thinking mode in multi-turn conversations, pass `thought_signature` fields back in subsequent turns. If using the official SDK with chat sessions, this is **handled automatically**.

---

## Prompting Best Practices

1. **Describe scenes, don't list keywords** — narrative paragraphs beat keyword lists
2. **Be hyper-specific** — describe camera angle, lighting, mood, textures
3. **Provide context/intent** — "logo for a high-end skincare brand" vs "create a logo"
4. **Iterate conversationally** — use multi-turn to refine small details
5. **Step-by-step for complex scenes** — background → foreground → focal element
6. **Use photography terms** — `wide-angle shot`, `85mm lens`, `bokeh`, `golden hour`
7. **Semantic negative prompts** — describe what you want instead of what to avoid

### Style Templates

**Photorealistic:**
```
A photorealistic [shot type] of [subject], [action], set in [environment].
Illuminated by [lighting]. Captured with [camera/lens]. [Aspect ratio].
```

**Product Shot:**
```
A high-resolution, studio-lit product photograph of [product] on [surface].
Three-point softbox lighting. [Camera angle]. Ultra-realistic. [Aspect ratio].
```

**Icon/Sticker:**
```
A [style] sticker of [subject] with [features]. Bold outlines, cel-shading,
vibrant colors. White/transparent background.
```

---

## Limitations

- Best language support: EN, ar-EG, de-DE, es-MX, fr-FR, hi-IN, id-ID, it-IT, ja-JP, ko-KR, pt-BR, ru-RU, ua-UA, vi-VN, zh-CN
- No audio or video input support
- Model may not always match exact requested number of image outputs
- `gemini-2.5-flash-image` works best with ≤3 input images
- When generating text in images: generate text first, then request image with text

---

## Model Selection Guide

| Need | Model |
|---|---|
| Best all-around, speed/quality balance | **Nano Banana 2** (`gemini-3.1-flash-image-preview`) |
| Professional assets, complex instructions, 4K | **Nano Banana Pro** (`gemini-3-pro-image-preview`) |
| High volume, low latency, simple tasks | **Nano Banana** (`gemini-2.5-flash-image`) |
| Specialized image-only generation | **Imagen 4** (via Gemini API) |
