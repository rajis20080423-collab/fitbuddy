"""
FitBuddy - AI Fitness Plan Generator
Powered by Google Gemini models + Streamlit
"""

import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------- Setup ----------
load_dotenv()

st.set_page_config(page_title="FitBuddy AI", page_icon="💪", layout="wide")

SYSTEM_PROMPT = (
    "You are FitBuddy, a friendly and certified-level AI fitness coach. "
    "Create safe, realistic, well-structured fitness plans. "
    "Always respect the user's injuries, equipment and diet preference. "
    "Use clear Markdown with headings, tables and bullet points. "
    "End with a short safety note advising a doctor check-up if needed."
)


# ---------- Helper functions ----------
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return round(bmi, 1), category


def build_prompt(d):
    return f"""
Create a personalised fitness plan for this person:

- Name: {d['name']}
- Age: {d['age']}
- Gender: {d['gender']}
- Height: {d['height']} cm
- Weight: {d['weight']} kg
- BMI: {d['bmi']} ({d['bmi_cat']})
- Goal: {d['goal']}
- Fitness level: {d['level']}
- Workout days per week: {d['days']}
- Time per session: {d['minutes']} minutes
- Equipment: {d['equipment']}
- Diet preference: {d['diet']}
- Injuries / health issues: {d['injuries'] or 'None'}

Please include:
1. A short summary of the person's profile and strategy.
2. A weekly workout plan table (Day | Focus | Exercises | Sets x Reps | Rest).
3. Warm-up and cool-down routine.
4. Daily calorie and macro (protein/carbs/fat) target estimate.
5. A one-day sample meal plan matching the diet preference (Indian food options are welcome).
6. Sleep, hydration and recovery tips.
7. A 4-week progression plan.
8. Motivation tips and a safety note.
""".strip()


def generate_plan(api_key, model, prompt):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
        ),
    )
    return response.text or ""


# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Get a free key from https://aistudio.google.com/apikey",
    )
    model_name = st.selectbox(
        "Gemini Model",
        ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite"],
        index=0,
    )

# ---------- Main UI ----------
st.title("💪 FitBuddy - AI Fitness Plan Generator")
st.write("Unga details kudunga, Gemini AI unaku personalised fitness plan generate pannum.")

with st.form("fitness_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Name", placeholder="Ex: Arun")
        age = st.number_input("Age", min_value=10, max_value=90, value=25)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    with c2:
        height = st.number_input("Height (cm)", min_value=100.0, max_value=230.0, value=170.0)
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=250.0, value=70.0)
        level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
    with c3:
        goal = st.selectbox(
            "Goal",
            [
                "Weight Loss",
                "Muscle Gain",
                "Stay Fit / Maintenance",
                "Improve Stamina",
                "Flexibility & Mobility",
            ],
        )
        days = st.slider("Workout days / week", 2, 7, 4)
        minutes = st.slider("Minutes / session", 20, 120, 45, step=5)

    c4, c5 = st.columns(2)
    with c4:
        equipment = st.selectbox(
            "Equipment", ["No equipment (Home)", "Dumbbells only", "Full Gym"]
        )
    with c5:
        diet = st.selectbox(
            "Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"]
        )

    injuries = st.text_area("Injuries / health issues (optional)", placeholder="Ex: knee pain")
    submitted = st.form_submit_button("🚀 Generate My Plan", use_container_width=True)

# ---------- Generate ----------
if submitted:
    if not api_key.strip():
        st.error("Sidebar la Gemini API Key enter pannunga.")
    else:
        bmi, bmi_cat = calculate_bmi(weight, height)
        m1, m2 = st.columns(2)
        m1.metric("BMI", bmi)
        m2.metric("Category", bmi_cat)

        form_data = {
            "name": name or "User",
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
            "bmi": bmi,
            "bmi_cat": bmi_cat,
            "goal": goal,
            "level": level,
            "days": days,
            "minutes": minutes,
            "equipment": equipment,
            "diet": diet,
            "injuries": injuries.strip(),
        }

        try:
            with st.spinner("FitBuddy unga plan ready pannitu irukku... 🏋️"):
                plan = generate_plan(api_key.strip(), model_name, build_prompt(form_data))

            if plan:
                st.success("Plan ready! 🎉")
                st.markdown(plan)
                st.download_button(
                    "📥 Download Plan (.md)",
                    data=plan,
                    file_name=f"fitbuddy_plan_{form_data['name']}.md",
                    mime="text/markdown",
                )
            else:
                st.warning("Empty response vandhuchu. Again try pannunga.")
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("API key, internet, illa model name check pannunga.")

st.divider()
st.caption("⚠️ Idhu AI generated general guidance. Health issues irundha doctor-a consult pannunga.")