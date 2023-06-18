import os
import pickle
import argparse
import logging
from time import sleep

from dotenv import dotenv_values
import openai
import tiktoken

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
model_name = "gpt-3.5-turbo"
enc = tiktoken.encoding_for_model(model_name)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Saving the following comments for later in case I need to come back to chunking by tokens
# max_tokens_per_transcript = args.max_tokens
# encoded_prompt = enc.encode(slice_prompt)
# print(f"The amount of tokens for the transcritpion is {len(encoded_prompt)}")
# sliced_prompt = [encoded_prompt[i:i+max_tokens_per_transcript] for i in range(0, len(encoded_prompt), max_tokens_per_transcript)]

def slice_transcript_file(transcription_file):
    with open(transcription_file, 'r') as f:
        transcript_lines = f.readlines()

    sliced_transcript = [transcript_lines[i:i+MAX_LINES_PER_TRANSCRIPT] for i in range(0, len(transcript_lines), MAX_LINES_PER_TRANSCRIPT)]
    logging.info(f"Number of slices from transcript: {len(sliced_transcript)}")
    return sliced_transcript

def summarize_transcript_slice(tslice, slice_system_directive: str, slice_prompt: str):
    messages = [
                {"role": "system", "content": slice_system_directive},
                {"role": "user", "content": f'"""{tslice}""" Prompt: {slice_prompt} '},
            ]

    logging.debug(f'Tokens for slice: {len(enc.encode(str(messages)))}')

    chat_completion = openai.ChatCompletion.create(
        model=model_name, 
        messages=messages)
    
    summary = chat_completion.choices[0].message.content
    return summary
    
def create_summaries_from_sliced_transcript(sliced_transcript, slice_system_directive: str, slice_prompt: str):
    summaries = []
    for i, tslice in enumerate(sliced_transcript):
        iterator = i + 1
        num_slices = len(sliced_transcript)
        logging.info(f"Creating Summary {iterator} of {num_slices}")
        while True:
            try:
                summary = summarize_transcript_slice(tslice, slice_system_directive, slice_prompt)
            except:
                logging.info(f"Ran into error from OpenAI, retrying in 2 seconds")
                sleep(2)
                continue
            break
        logging.info(f"Summary {iterator} of {num_slices}: {summary}")
        summaries.append(summary)
    return summaries

def summarize_all_summaries(summaries, summary_system_directive: str, summary_prompt: str):
    triple_quote_join = '\"\"\" \"\"\"'.join(summaries)
    logging.info(f"Token length of summaries: {len(enc.encode(triple_quote_join))}")

    messages = [
                {"role": "system", 
                "content": summary_system_directive},
                {"role": "user", "content": f'"""{triple_quote_join}""" Prompt: {summary_prompt} '},
            ]
    
    logging.debug(f'Tokens for all summaries: {len(enc.encode(str(messages)))}')

    chat_completion = openai.ChatCompletion.create(
        model=model_name, 
        messages=messages)
    finished_summary = chat_completion.choices[0].message.content
    logging.info(f"Finished summary:\n{finished_summary}")
    return finished_summary

def check_str_configs_are_set_correctly(*configs):
    bad_configs = []
    for cfg in configs:
        if not isinstance(cfg, str) or cfg == "":
            bad_configs.append(cfg)
    if bad_configs:
        raise RuntimeError(f'The following configs were not set correctly: {" ".join(bad_configs)}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Summarize transcript with GPT')
    parser.add_argument('-f', '--file', type=str, help='Input file path')
    parser.add_argument('-o', '--output', type=str, default='./output_summary.txt', help='Output file path')
    parser.add_argument('-c', '--cache', action='store_true', help='Cache summaries')
    parser.add_argument('-r', '--resume', action='store_true', help='Resume from cache')
    parser.add_argument('--config', type=str, default='.env', help='Path to .env file')
    args = parser.parse_args()

    transcription_file = args.file
    output_file = args.output
    cache_summaries = args.cache
    resume_from_cache = args.resume
    config_env_file = args.config

    config = {
        **dotenv_values(config_env_file),
        **os.environ
    }

    MAX_LINES_PER_TRANSCRIPT = int(config.get("MAX_LINES_PER_TRANSCRIPT", 100))
    SLICE_SYSTEM_DIRECTIVE = config.get("SLICE_SYSTEM_DIRECTIVE")
    SLICE_PROMPT = config.get("SLICE_PROMPT")
    SUMMARY_SYSTEM_DIRECTIVE = config.get("SUMMARY_SYSTEM_DIRECTIVE")
    SUMMARY_PROMPT = config.get("SUMMARY_PROMPT")

    check_str_configs_are_set_correctly(
        SLICE_SYSTEM_DIRECTIVE, 
        SLICE_PROMPT, 
        SUMMARY_SYSTEM_DIRECTIVE, 
        SUMMARY_PROMPT
    )
    
    logging.info(
        (
            f"\n"
            f"************************************\n"
            f"*** GPT Transcript Summarization ***\n"
            f"************************************\n"
            f"\n"
            f"CONFIGURATION:\n\n"
            f"TRANSCRIPTION_FILE: {transcription_file}\n\n"
            f"MAX_LINES_PER_TRANSCRIPT: {MAX_LINES_PER_TRANSCRIPT}\n\n"
            f"SLICE_SYSTEM_DIRECTIVE: {SLICE_SYSTEM_DIRECTIVE}\n"
            f"SLICE_PROMPT: {SLICE_PROMPT}\n"
            f"SUMMARY_SYSTEM_DIRECTIVE: {SUMMARY_SYSTEM_DIRECTIVE}\n"
            f"SUMMARY_PROMPT: {SUMMARY_PROMPT}\n\n"
        ))
        
    if not resume_from_cache:
        logging.info(f"Loading transcript from {transcription_file}")
        if not transcription_file:
            raise Exception("Please provide a file path to the transcription file in the -f argument")
        logging.info(f"Slicing transcript")
        sliced_transcript = slice_transcript_file(transcription_file)
        summaries = create_summaries_from_sliced_transcript(sliced_transcript, SLICE_SYSTEM_DIRECTIVE, SLICE_PROMPT)
        with open('cache/summaries.pkl', 'wb') as f:
            logging.info(f"Caching summaries")
            pickle.dump(summaries, f)
    else:
        with open('cache/summaries.pkl', 'rb') as f:
            logging.info(f"Loading summaries from cache")
            summaries = pickle.load(f)

    finished_summary = summarize_all_summaries(summaries, SUMMARY_SYSTEM_DIRECTIVE, SUMMARY_PROMPT)

    with open(output_file, 'w') as f:
        logging.info(f"Writing summary to {output_file}")
        f.write(finished_summary)