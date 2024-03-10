from transformers import pipeline

generator = pipeline("text-generation", model="llama2-model-checkpoint")

result = generator("Hello, how can I help you today?", max_length=50)
print(result[0]['generated_text'])
