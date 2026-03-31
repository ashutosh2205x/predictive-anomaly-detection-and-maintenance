from openai import OpenAI
import os

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_explanation(data, severity, prediction):
    return """
#     try:
#         prompt = f"""
# Machine Data:
# Temperature: {data['temperature']}
# Vibration: {data['vibration']}
# Pressure: {data['pressure']}
# Severity: {severity}
# Risk: {prediction['risk']}
#
# Explain what is happening and what action to take.
# """
#
#         res = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt}]
#         )
#
#         return res.choices[0].message.content
#
#     except:
#         return "AI explanation unavailable."