from openai import OpenAI
import openai

def generate_explanation_ai(data):
    prompt = f"""
Machine Data:
Temperature: {data['temperature']}
Severity: {data['severity']}
Anomaly Score: {data['score']}

Explain:
- What is happening
- How serious it is
- What action to take
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

client = OpenAI()

def generate_explanation_ai(temp, humidity, pred, score, severity):
    try:
        prompt = f"""
You are an industrial maintenance AI.

Sensor Data:
- Temperature: {temp}°C
- Humidity: {humidity}%
- Anomaly Score: {score}
- Severity: {severity}

Explain clearly:
1. What is happening
2. How serious it is
3. Likely cause
4. Recommended action

Keep it concise and professional.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        print("OpenAI error:", e)
        return generate_explanation(temp, humidity, pred, score, severity)