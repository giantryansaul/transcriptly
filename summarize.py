
import os
import openai
from openai import Model
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

question = "Summarize the transcript of this Dungeons and Dragons session tell me the story of the game, what happened, who did what, and what was the outcome. Please write several outcomes if there are more than one. There will be several prompts after this one with the transcript."
transcription_file = "./transcript.txt"
max_tokens = 100
temperature = 0.7
model_name = "text-davinci-002"
model = Model(model_name)
chunk_size = 100

with open(transcription_file, 'r') as f:
    lines = f.readlines()

# Split the lines into chunks
chunks = [lines[i:i+chunk_size] for i in range(0, len(lines), chunk_size)]
chunks.insert(0, [question])

# Loop over each chunk and generate a summary using ChatGPT
summaries = []
for chunk in chunks:
    print(f'Processing chunk of {len(chunk)} lines...')
    prompt = ''.join(chunk)
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature
    )
    print(f'Response: {response.choices[0].text.strip()}')
    summary = response.choices[0].text.strip()
    summaries.append(summary)

# Write the summaries to a new file
with open('summaries.txt', 'w') as f:
    for summary in summaries:
        f.write(summary + '\n')