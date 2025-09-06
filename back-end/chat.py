import json
from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS

import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set your OpenAI API key (ideally, load this from an environment variable)

app = Flask(__name__)
CORS(app,origins="http://localhost:5173")

def extract_json(text):
    start = text.find('{')
    if start == -1:
        return None, "No JSON object found in the output."
    json_part = text[start:]
    try:
        data = json.loads(json_part)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"JSON decoding error: {e}"


def generate_workout_chatgpt(goal, work_day, duration, injury_area=None, injury_action=None):
    prompt = (
        "Output only a valid JSON object with no additional text, explanation, or markdown formatting. "
        "The JSON object must start with a '{' and end with a '}'. I need a valid JSON so I can scrape data from it; do not add comments or any extra text!!!\n\n"
        "I am giving you a REAL example JSON, and your output needs to be exactly like this with the respective exercises.\n"
        "Below is an example of the expected JSON format:\n"
        "{\n"
        '  "cooldown": "5 minutes of stretching and cool down.",\n'
        '  "exercises": [\n'
        "    {\n"
        '      "description": "A compound exercise that works the shoulders and triceps.",\n'
        '      "duration": "15-20 minutes",\n'
        '      "name": "Overhead Press",\n'
        '      "reps": "12-15",\n'
        "      \"sets\": 3,\n"
        '      "type": "compound"\n'
        "    },\n"
        "    {\n"
        '      "description": "A compound exercise targeting the chest and triceps.",\n'
        '      "duration": "15-20 minutes",\n'
        '      "name": "Bench Press",\n'
        '      "reps": "12-15",\n'
        "      \"sets\": 3,\n"
        '      "type": "compound"\n'
        "    },\n"
        "    {\n"
        '      "description": "Cardio exercise that targets upper body endurance.",\n'
        '      "duration": "15 minutes",\n'
        '      "name": "Rowing Machine",\n'
        '      "type": "cardio"\n'
        "    }\n"
        "  ],\n"
        '  "warmup": "10 minutes of dynamic warm-up (e.g., jogging, jumping jacks)."\n'
        "}\n\n"
        f"Now, generate a detailed workout plan for a {work_day} day session for a user whose goal is to {goal} weight "
        f"and who has {duration} minutes to workout. "
    )

    # Append injury/injury_action details if provided
    if injury_area:
        prompt += f"\nThe user reports pain or injury in the following area(s): {injury_area}. "
        if injury_action == "avoid":
            prompt += "Avoid exercises that stress these areas. "
        elif injury_action == "address":
            prompt += "Include rehabilitation exercises to help address these issues. "

    prompt += (
        "The plan must include three keys: 'warmup', 'exercises', and 'cooldown'. "
        "The 'exercises' should list compound movements first, then isolation exercises, and include a cardio exercise if the goal is 'lose'.\n\n"
        "Output only a valid JSON object exactly in the above format."
    )

    messages = [
        {"role": "system", "content": "You are a workout plan generator. Output only the JSON object as specified, with no additional commentary."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
                                                  messages=messages,
                                                  temperature=0.7,
                                                  max_tokens=600)
        result_text = response.choices[0].message.content.strip()
        try:
            workout_plan = json.loads(result_text)
            return workout_plan
        except json.JSONDecodeError:
            workout_plan, err = extract_json(result_text)
            if err:
                return {"error": "Unable to parse output as JSON", "raw_output": result_text}
            return workout_plan
    except Exception as e:
        return {"error": str(e)}


@app.route("/workout", methods=["POST"])
def workout():
    data = request.get_json()
    print("Received data:", data)
    goal = data.get("goal", "").strip().lower()
    duration = data.get("duration")
    work_day = data.get("work_day", "").strip().lower()
    # e.g., "knee, lower back"
    injury_area = data.get("injury_area", "").strip().lower()
    # "avoid" or "address"
    injury_action = data.get("injury_action", "").strip().lower()

    if goal not in ["gain", "lose"]:
        return jsonify({"error": "Invalid goal. Must be 'gain' or 'lose'."}), 400
    if not isinstance(duration, int) or duration < 20:
        return jsonify({"error": "Duration must be an integer of at least 20 minutes."}), 400
    if work_day not in ["leg", "push", "pull"]:
        return jsonify({"error": "Invalid work_day. Must be 'leg', 'push', or 'pull'."}), 400
    if injury_area and injury_action not in ["avoid", "address"]:
        return jsonify({"error": "Invalid injury_action. Must be 'avoid' or 'address' if an injury area is provided."}), 400

    workout_plan = generate_workout_chatgpt(
        goal, work_day, duration, injury_area, injury_action)
    return jsonify(workout_plan)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
