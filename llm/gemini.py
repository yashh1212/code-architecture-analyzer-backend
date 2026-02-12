import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyCIZ6FoXvTqVFiU2AfGrCMTFjODK516T8o")

model = genai.GenerativeModel("gemini-3-flash-preview")

def ask_llm(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text
