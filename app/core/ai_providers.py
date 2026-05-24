import os
import google.generativeai as genai
import ollama
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def summarize_document(self, content): pass
    @abstractmethod
    def describe_image(self, image_path): pass

class GoogleAIProvider(AIProvider):
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    def summarize_document(self, content):
        response = self.model.generate_content(f"Summarize document (JSON: summary, topics, entities): {content}")
        return response.text
    def describe_image(self, image_path): pass

class OllamaProvider(AIProvider):
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
    def summarize_document(self, content):
        response = ollama.chat(model=self.model_name, messages=[{'role': 'user', 'content': f"Summarize (JSON): {content}"}])
        return response['message']['content']
    def describe_image(self, image_path):
        response = ollama.generate(model='moondream', prompt='Describe image', images=[image_path])
        return response['response']
