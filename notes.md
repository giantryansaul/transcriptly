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

# Development Log

## 06-06-2023

I began working back on the transcription and summarization project by going back through my old experiments on Whisper and GPT. I'm starting a log of this work today so I can keep track of my thoughts for future reference.

Currently the summarization project is in a good place. I have a working prototype that can summarize a long transcription file. I have a sample transcription from The Adventure Zone that I can use to test. I want to consolidate the code into a better structure that I can iterate with several different tests.

- [x] Consolidate code into a callable python script with arguments for transcription files.
- [x] Test with multiple transcription files and compare the summaries to what is stored on their wiki.

After this, take some of the transcription files from my own D&D group and test them. I want to see how well the summarization works for these private sessions that are less geared toward a public audience. The transcripts are generated through Whisper using a script I developed, but there is a lot of garbage and the timings of the speakers don't line up very well, will need to work through this some more.

- [ ] Clean up older D&D transcripts programmatically.
- [ ] Test with D&D transcripts.
- [x] Allow settings in the summarization script to change the desired outcome of the summary.
- [ ] Run through summarization script.


### Results from Adventure Zone ep 1

```
In this Dungeons and Dragons session, the Dungeon Master Griffin introduces the game to the players Travis, Justin, and Clint. They joke around and discuss creating their characters and abilities. Travis plays a human fighter named Magnus Burnsides, while Justin plays a wizard named Taako. Clint plays a dwarf cleric named Merle. The players discuss their abilities, class, and equipment while joking around, and prepare for a quest offered by Gundren Rockseeker which pays poorly but promises to be their last job. During this quest, they encounter goblins and wolves and engage in combat with them. They use different tactics to defeat their enemies, including spellcasting, attacking, and talking. There is joking and humor throughout the game as they learn the rules and develop their characters. At the end of the session, Taako hears Gerblin in the distance and asks if they got the players, leaving a cliff-hanger for the next session. No treasure was gained during this session and no levels were gained. 

Fights Summary:
- Combat with goblins rushing towards their cart.
- Encounter with wolves in a cavern.
- Battle with gerblins in a hideout.

Players:
- Magnus Burnsides, played by Travis, human fighter.
- Taako, played by Justin, wizard.
- Merle, played by Clint, dwarf cleric.

Cliff-hanger: 
In the last session, Taako hears Gerblin in the distance and asks if they got the players, leaving a cliff-hanger for the next session.
```

## 06-07-2023

Continuing from yesterday's proof of conception completion. 

## 06-14-2023

Transcribed some transcripts with modified parameters.

## 06-18-2023

* Cleaning up the repo to commit.
* Went through the summarize.py file and made it more modular, better logging, and made the summarization prompts into environment variables, loading them through a .env file. This file can be customized and you can save multiple versions of it to use for different summarization tasks.
* Split transcribe into multi and single inputs. I can probably consolidate these into a single script, but for now I'm keeping them separate.
* The commit from today includes several weeks of uncommitted work.

## 06-24-2023

* Updates to transcription script, moved the transcription model to an environment variable.
* Changed from print in the transcription script to a logger. Should consider consolidating both transcription scripts into one with some arguments.
* Added a function to remove duplicate lines, I should probably write a simple unit test for this function.

[ ] Add unit test framework to the project.
[ ] Add unit tests for the duplicate line removal function.
[ ] Add unit tests for the summarization script.

## 06-25-2023

* Setup some of the project structure for unit tests and general organization.
* I'm going through refactoring the multi-input script into a module service, this will take some time to abstract the whisper output into a more generic format.
* Although I'm not sure if I'll ever use something that's not Whisper, I'd like to put simple abstractions in place so I can create some unit tests.
* What is going to be helpful for unit testing is abstracting all of the parts that whisper returns that I use in my own transcriptions. This means abstracting the transcript, the segments, and the speakers. I can then use these abstractions to create unit tests for the summarization script.

[ ] Finish refactoring the multi-input script into a module service.
[x] Finish refactoring all of the transcription service parts so that the transcript, segments, and speakers are all abstracted into a generic format.

## 07-02-2023

* Continued refactoring the multi-input script into a module service and abstracting the parts of the whisper output that I use in my own transcriptions.
* Segements and transcription output are in their own data classes now, so I should be able to setup some unit tests.

## 07-03-2023
* Created multiple unit tests for the Transcript class.
* WhisperService is mocked out.
* There are some transcription tasks that I would like to break out into worker services and await them to finish. This should be the next major development.

[ ] Follow TODOs in the Transcript service to break out multi-input methods.
[ ] Read up more on worker services that Python offers.
[ ] Create a worker service for the multi-input transcription.