
result = client.models.generate_content(
    model="gemini-3.1-flash-image",
    contents=full_prompt,
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        response_format={
            "image": {
                "aspect_ratio": aspect_ratio,
                "image_size": image_size
            }
        }
    )
)

generated = None

for part in result.parts:
    if part.inline_data is not None:
        generated = part.as_image()
        break

if generated is not None:
    st.session_state["generated_image"] = generated
    st.success("Your image has been generated!")
else:
    st.error("No image was returned. Try another prompt.")
    for part in result.parts:
        if part.text:
            st.write(part.text)
