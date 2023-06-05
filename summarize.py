
import os
import openai
import tiktoken
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

max_tokens_per_transcript = 2000
max_lines_per_transcript = 100
transcription_file = "./transcriptions/adventure-zone-ep1.txt"
with open(transcription_file, 'r') as f:
    lines = f.readlines()
prompt = f"Summarize the transcript of this Dungeons and Dragons session. This is only a part of the transcript. Summarize what is happening with each of the players."

model_name = "gpt-3.5-turbo"
enc = tiktoken.encoding_for_model(model_name)
encoded_prompt = enc.encode(prompt)
# print(f"The amount of tokens for the transcritpion is {len(encoded_prompt)}")
sliced_transcript = [lines[i:i+max_lines_per_transcript] for i in range(0, len(lines), max_lines_per_transcript)]
sliced_prompt = [encoded_prompt[i:i+max_tokens_per_transcript] for i in range(0, len(encoded_prompt), max_tokens_per_transcript)]

summaries = []
for i, tslice in enumerate(sliced_transcript):
    print(f"Request {i+1} of {len(tslice)}")
    chat_completion = openai.ChatCompletion.create(
        model=model_name, 
        messages=[
                {"role": "system", "content": 'You will be provided with a transcript delimited by triple quotes and a prompt to summarize. Your task is to summarize using the provided transcript and be as concise as possible.'},
                {"role": "user", "content": f'"""{tslice}""" Prompt: {prompt} '},
            ])
    print(chat_completion.choices[0].message.content)
    summaries.append(chat_completion.choices[0].message.content)


# # Write the summaries to a new file
# with open('summaries.txt', 'w') as f:
#     for summary in summaries:
#         f.write(summary + '\n')