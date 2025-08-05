import logging

def get_video_transcript(video_id):
    """
    Fetch transcript for a given YouTube video ID using youtube_transcript_api.
    Returns transcript as a string, or a fallback message if not available.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text
    except ImportError:
        logging.warning("youtube_transcript_api not installed. Transcript unavailable.")
        return "Transcript unavailable (missing dependency)."
    except (TranscriptsDisabled, NoTranscriptFound):
        return "Transcript unavailable for this video."
    except Exception as e:
        logging.error(f"Error fetching transcript: {e}")
        return "Transcript unavailable due to error."
