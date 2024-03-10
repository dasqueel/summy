import whisperx
import os
import sys

podcast = sys.argv[1]
hgApiKey = os.getenv("hgApiKey")

device = "cuda"
wavPath = f"./wavs/"
audio_file = f"/root/neilbob/squeel-gpt/transcripts/wavs/{podcast}.wav"
batch_size = 16
compute_type = "float16"

def transcribe(podcast):
    model = whisperx.load_model("large-v2", device, compute_type=compute_type, language="en")
    audio = whisperx.load_audio(f"{wavPath}/{podcast}.wav")
    result = model.transcribe(audio, batch_size=batch_size)
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

    diarize_model = whisperx.DiarizationPipeline(use_auth_token=hgApiKey, device=device)
    diarize_segments = diarize_model(audio)
    diarize_model(audio, min_speakers=2, max_speakers=3)

    result = whisperx.assign_word_speakers(diarize_segments, result)
    # print(diarize_segments)
    # print(result["segments"]) # segments are now assigned speaker IDs
    data_segments = result["segments"]

    # Initialize variables
    final_transcript = ""
    current_speaker = None

    for segment in data_segments:
        speaker = segment['words'][0]['speaker']
        text = segment['text']
        
        if speaker != current_speaker:
            # If this is not the first segment, add a newline to separate from the previous speaker's text
            if current_speaker is not None:
                final_transcript += "\n\n"
            current_speaker = speaker
            final_transcript += f"{speaker}: {text}"
        else:
            final_transcript += f" {text}"

    with open(f'./diarizedTranscripts/{podcast}.txt', "w") as file:
        file.write(final_transcript)