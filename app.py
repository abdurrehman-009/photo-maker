
import streamlit as st
import base64
from io import BytesIO
from google import genai
from PIL import Image

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="PixelForge AI | Photo Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- PROFESSIONAL DESIGN ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0b1020, #111827);
    color: #f8fafc;
}
[data-testid="stSidebar"] {
    background: #0f172a;
    border-right: 1px solid #293449;
}
.hero {
    padding: 30px;
    border: 1px solid #334155;
    border-radius: 22px;
    background: linear-gradient(120deg, #1e293b, #172554);
    margin-bottom: 24px;
}
.hero h1 {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 8px;
}
.hero p {
    color: #cbd5e1;
    font-size: 16px;
}
.section-title {
    font-size: 22px;
    font-weight: 700;
    margin: 20px 0 12px 0;
}
div.stButton > button {
    width: 100%;
    border-radius: 12px;
    min-height: 48px;
    font-weight: 700;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
}
div.stButton > button:hover {
    border: 1px solid #c4b5fd;
    color: white;
}
.stTextArea textarea {
    border-radius: 12px;
}
.footer {
    text-align: center;
    color: #94a3b8;
    padding: 25px 0;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- API CONFIGURATION ----------------
def get_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return ""

# ---------------- HEADER ----------------
st.markdown("""
<div class="hero">
    <h1>🎨 PixelForge AI</h1>
    <p>Your imagination. Your prompt. Your AI-generated masterpiece.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🎨 PixelForge AI")
    st.caption("AI-powered creative studio")
    st.divider()

    st.markdown("### 🖼️ Image settings")

    style = st.selectbox(
        "Art style",
        [
            "Photorealistic",
            "3D Cartoon",
            "Anime",
            "Digital Art",
            "Cinematic",
            "Watercolor",
            "Fantasy",
            "Minimalist",
            "Product Photography"
        ]
    )

    aspect_ratio = st.selectbox(
        "Image ratio",
        ["1:1", "16:9", "9:16", "4:3", "3:4"]
    )

    image_size = st.selectbox(
        "Image quality",
        ["1K", "2K", "4K"]
    )

    st.divider()
    st.caption("Powered by Google Gemini")
    st.caption("Keep your API key private.")

# ---------------- MAIN WORKSPACE ----------------
left, right = st.columns([1, 1.1], gap="large")

with left:
    st.markdown('<div class="section-title">✍️ Create your image</div>',
                unsafe_allow_html=True)

    prompt = st.text_area(
        "Describe the image you want",
        placeholder=(
            "Example: A cute baby elephant in a magical forest, "
            "glowing fireflies, cinematic lighting, highly detailed..."
        ),
        height=180,
        max_chars=4000
    )

    negative_prompt = st.text_input(
        "Things to avoid (optional)",
        placeholder="Blurry image, distorted objects, unwanted text..."
    )

    st.caption("Be specific about the subject, background, lighting, and mood.")

    generate = st.button(
        "✨ Generate AI Image",
        type="primary"
    )

    if st.button("🧹 Clear prompt"):
        st.session_state["prompt_clear"] = True
        st.rerun()

with right:
    st.markdown('<div class="section-title">🖼️ Your masterpiece</div>',
                unsafe_allow_html=True)

    if "generated_image" not in st.session_state:
        st.session_state["generated_image"] = None

    if generate:
        if not prompt.strip():
            st.warning("Please enter a description for your image.")
        else:
            api_key = get_api_key()

            if not api_key:
                st.error(
                    "Gemini API key is missing. Add GEMINI_API_KEY "
                    "to Streamlit Secrets before generating an image."
                )
            else:
                try:
                    client = genai.Client(api_key=api_key)

                    full_prompt = (
                        f"Generate a high-quality {style} image. "
                        f"Image description: {prompt.strip()}. "
                        f"Composition aspect ratio: {aspect_ratio}. "
                        "Create a polished, visually appealing image."
                    )

                    if negative_prompt.strip():
                        full_prompt += (
                            "\nAvoid these elements where possible: "
                            + negative_prompt.strip()
                        )

                    with st.spinner(
                        "Creating your image with Gemini AI..."
                    ):
                        result = client.interactions.create(
                            model="gemini-3.1-flash-image",
                            input=full_prompt,
                            response_format={
                                "type": "image",
                                "mime_type": "image/png",
                                "aspect_ratio": aspect_ratio,
                                "image_size": image_size
                            }
                        )

                    image_data = getattr(
                        getattr(result, "output_image", None),
                        "data",
                        None
                    )

                    if image_data:
                        if isinstance(image_data, str):
                            image_bytes = base64.b64decode(image_data)
                        else:
                            image_bytes = base64.b64decode(image_data)

                        generated = Image.open(
                            BytesIO(image_bytes)
                        ).convert("RGB")

                        st.session_state["generated_image"] = generated
                        st.success("Your image has been generated!")
                    else:
                        st.error(
                            "The model returned no image. "
                            "Try a different prompt or check model availability."
                        )

                except Exception as e:
                    st.error(
                        "Image generation failed. Check your API key, "
                        "model access, API quota, and connection."
                    )
                    with st.expander("Technical details"):
                        st.code(str(e))

    if st.session_state["generated_image"] is not None:
        image = st.session_state["generated_image"]

        st.image(image, use_container_width=True)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        st.download_button(
            "⬇️ Download Image (PNG)",
            data=buffer.getvalue(),
            file_name="pixelforge_ai_image.png",
            mime="image/png",
            type="primary"
        )

    else:
        st.info(
            "Your generated image will appear here. "
            "Enter a prompt and click Generate AI Image."
        )

# ---------------- FOOTER ----------------
st.divider()
st.markdown("""
<div class="footer">
    PixelForge AI · Creative possibilities powered by Gemini
</div>
""", unsafe_allow_html=True)
