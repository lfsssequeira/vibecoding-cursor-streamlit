import streamlit as st
import random

# Set the page title
st.set_page_config(page_title="Welcome", page_icon="🚀")

# Main content
st.title("We are great")
st.write("Welcome to our amazing application!")

# Add some simple styling
st.markdown("---")

# Voting section
st.header("Vibe Coding Vote! 🎵")
st.write("Choose your favorite vibe coding style:")

# Vibe coding texts for each option
vibe_texts_a = [
    "Late night coding with chill beats",
    "Coffee-fueled productivity sessions",
    "Debugging with your favorite playlist"
]

vibe_texts_b = [
    "Pair programming with great music",
    "Coding marathons with energy drinks",
    "Building apps while vibing to lo-fi"
]

vibe_texts_c = [
    "Creative coding with ambient sounds",
    "Problem-solving with epic soundtracks",
    "Development flow with perfect tempo"
]

# Create voting options
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Option A 🎧"):
        selected_text = random.choice(vibe_texts_a)
        st.success(f"You chose A! {selected_text}")

with col2:
    if st.button("Option B 🎵"):
        selected_text = random.choice(vibe_texts_b)
        st.success(f"You chose B! {selected_text}")

with col3:
    if st.button("Option C 🎶"):
        selected_text = random.choice(vibe_texts_c)
        st.success(f"You chose C! {selected_text}")

st.markdown("---")
st.write("This is a simple landing page built with Streamlit.")
