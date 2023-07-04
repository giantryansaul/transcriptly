# Transcriptly

## Transcription

Using OpenAI Whisper, take a multi-speaker audio file and transcribe it into text.

## Summarization

Using OpenAI GPT, take a text file and summarize it. Chunk the text into smaller parts and summarize each chunk. Then, combine the summaries into a single summary.

### Notes on how GPT works

Using ChatGPT gives a bit of a false impression of how the model and interface work. To have context to past messages, you need to send the entire history of the conversation to the model on each subsequent message. I think ChatGPT probably has a pretty streamlined way to go about this, but if you were going to build your own ChatGPT using the same API, you'd quickly find that the messages being sent are pretty long. This is because the model needs to have the entire history of the conversation to be able to generate the next message.

This means that building an understanding of the entire transcript can't really be done without sending the *entire* transcript to the model. This is a problem because the token limit for GPT is pretty low for large documents like this. A future version of GPT-4 that allows 32K tokens should be able to handle very long documents, but for now its better to just chunk things up, summarize them, then throw all the summaries together for a single summary request.

Messages are sent via a list, and you can specify wether the message is a user prompt (`user`), a GPT reseponse (`assistant`), or a system directive to help GPT craft a helpful response (`system`). 

### Chunking by lines instead of tokens

So its possible to chunk by tokens in GPT using tiktoken, but I found this to be a bad way to go about it since you could very easily lose a lot of context in the messages sent to GPT. Instead I started chunking by some arbitrary lines in the transcription. This makes it so that you 

