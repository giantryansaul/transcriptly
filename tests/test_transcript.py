from unittest import TestCase, main
from unittest.mock import patch
from transcriptly.transcribe import Transcribe
from transcriptly.data_types import AudioInput, Segment, TranscriptionResult

class TestTranscript(TestCase):
    def test_init(self):
        # Test that the default values are set correctly
        transcribe = Transcribe(
            service_name="whisper", 
            model_name="tiny"
        )
        self.assertEqual(transcribe.service_name, "whisper")
        self.assertEqual(transcribe.model_name, "tiny")
        self.assertEqual(transcribe.remove_duplicates, False)

    def test_init_remove_duplicates(self):
        # Test that remove_duplicates is set to True when specified
        transcribe = Transcribe(
            service_name="whisper", 
            model_name="tiny",
            remove_duplicates=True
        )
        self.assertEqual(transcribe.remove_duplicates, True)

    def test_init_model_name_runtime_error(self):
        # Test that a RuntimeError is raised when model_name is not specified
        with self.assertRaises(RuntimeError):
            Transcribe(service_name="whisper")

    @patch("transcriptly.transcribe_services.whisper_service.WhisperTranscribe")
    def test_transcribe_single_audio_file(self, mock):
        # Test that transcribe_single_audio_file calls the transcribe method of
        # the WhisperTranscribe class
        whisper_instance = mock.return_value
        whisper_instance.transcribe.return_value = TranscriptionResult(
            segments=[
                Segment("Hello", 0, 1),
                Segment("world", 1, 2),
            ]
        )
        transcribe = Transcribe(
            service_name="whisper",
            model_name="tiny"
        )
        ainput = AudioInput("test.wav")
        transcription_result = transcribe.transcribe_single_audio_file(ainput)
        whisper_instance.transcribe.assert_called_once_with("test.wav")
        self.assertEqual(transcription_result[0].text, "Hello")
        self.assertEqual(transcription_result[1].text, "world")

    @patch("transcriptly.transcribe_services.whisper_service.WhisperTranscribe")
    def test_remove_duplicates_from_segments(self, mock):
        whisper_instance = mock.return_value
        whisper_instance.transcribe.return_value = TranscriptionResult(
            segments=[
                Segment("Hello", 0, 1),
                Segment("world", 1, 2),
                Segment("world", 2, 3),
            ]
        )
        transcribe = Transcribe(
            service_name="whisper",
            model_name="tiny",
            remove_duplicates=True
        )
        ainput = AudioInput("test.wav")
        transcription_result = transcribe.transcribe_single_audio_file(ainput)
        self.assertEqual(len(transcription_result), 2)
        self.assertEqual(transcription_result[0].text, "Hello")
        self.assertEqual(transcription_result[1].text, "world")

    @patch("transcriptly.transcribe_services.whisper_service.WhisperTranscribe")
    def test_remove_duplicates_with_one_segment(self, mock):
        whisper_instance = mock.return_value
        whisper_instance.transcribe.return_value = TranscriptionResult(
            segments=[
                Segment("Hello", 0, 1)
            ]
        )
        transcribe = Transcribe(
            service_name="whisper",
            model_name="tiny",
            remove_duplicates=True
        )
        ainput = AudioInput("test.wav")
        transcription_result = transcribe.transcribe_single_audio_file(ainput)
        self.assertEqual(len(transcription_result), 1)
        self.assertEqual(transcription_result[0].text, "Hello")
    
    @patch("transcriptly.transcribe_services.whisper_service.WhisperTranscribe")
    def test_add_speaker_to_segments(self, mock):
        whisper_instance = mock.return_value
        whisper_instance.transcribe.return_value = TranscriptionResult(
            segments=[
                Segment("Hello", 0, 1),
                Segment("world", 1, 2),
            ]
        )
        transcribe = Transcribe(
            service_name="whisper",
            model_name="tiny",
        )
        ainput = AudioInput("test.wav", speaker="John")
        transcription_result = transcribe.transcribe_single_audio_file(ainput)
        self.assertEqual(len(transcription_result), 2)
        self.assertEqual(transcription_result[0].speaker, "John")
        self.assertEqual(transcription_result[1].speaker, "John")
    
    @patch("os.path.basename")
    def test_get_speaker_from_file_path(self, mock):
        # Test that get_speaker_from_file_path returns the correct speaker
        mock.return_value = "John.wav"
        speaker = Transcribe.get_speaker_from_file_path("test/file/path/John.wav")
        self.assertEqual(speaker, "John")
        mock.assert_called_once_with("test/file/path/John.wav")

    @patch("os.path.basename")
    def test_get_speaker_from_file_path_no_extension(self, mock):
        # Test that get_speaker_from_file_path returns the correct speaker
        mock.return_value = "John"
        speaker = Transcribe.get_speaker_from_file_path("test/file/path/John")
        self.assertEqual(speaker, "John")
        mock.assert_called_once_with("test/file/path/John")

    @patch("os.path.basename")
    def test_get_speaker_from_file_path_with_symbol_delimiters(self, mock):
        # Test that the speaker is returned correctly when the file name contains symbols
        mock.return_value = "John_01.wav"
        speaker = Transcribe.get_speaker_from_file_path("test/file/path/John_01.wav")
        self.assertEqual(speaker, "John")
        mock.assert_called_once_with("test/file/path/John_01.wav")

    def test_sort_segments(self):
        # Test that the segments are sorted correctly
        segment_collection = [
            [Segment("three", 3, 2), Segment("five", 5, 3), Segment("six", 6, 1)],
            [Segment("one", 1, 2), Segment("two", 2, 3), Segment("four", 4, 1)],
        ]
        sorted_segments = Transcribe.sort_segments(segment_collection)
        self.assertEqual(sorted_segments[0].text, "one")
        self.assertEqual(sorted_segments[1].text, "two")
        self.assertEqual(sorted_segments[2].text, "three")
        self.assertEqual(sorted_segments[3].text, "four")
        self.assertEqual(sorted_segments[4].text, "five")
        self.assertEqual(sorted_segments[5].text, "six")

if __name__ == '__main__':
    main()