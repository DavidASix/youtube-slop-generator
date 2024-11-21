import os
import uuid
import random
import numpy as np

# Video Generation
import moviepy as mp

"""
Video class for generating YouTube shorts content.

Attributes:
    content(dict): A dictionary containing the data for the video. Example structure:
    {
        "author": "RedditUserHandle",
        "url": "https://example.com/media",
        "path": "/local/path/to/media",
        "name": "media_filename.ext",
        "title": "Reddit Post Title",
        "type": "image" | "video",
        "duration": (int, optional, for videos) Duration of the video in seconds,
        "dimensions": (dict, optional, for videos) {
            "height": 1920,
            "width": 1080
        }
    }
"""


class Video:
    def __init__(self, content):
        output_dir = os.path.join(os.getcwd(), "build", "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.content = content
        self.title = content.get("title")
        self.uuid = uuid.uuid4()
        self.output_path = os.path.join(output_dir, f"{self.uuid}.mp4")

    def generate_short(self):
        current_dir = os.getcwd()
        build_path = os.path.join(current_dir, "build")
        music_path = os.path.join(build_path, "music.mp3")
        background_path = os.path.join(build_path, "background.mp4")
        dimensions = {"height": 1280, "width": 720}
        duration = 35

        music = mp.AudioFileClip(music_path)

        # Create a video clip with the audio
        bg_color = mp.ColorClip(
            size=(dimensions["width"], dimensions["height"]),
            color=(240, 240, 240),
        )

        bg_video = (
            mp.VideoFileClip(background_path)
            .resized(height=dimensions["height"])
            .with_position(("center", "center"))
            .with_opacity(0.8)
        )
        bg_start_time = random.uniform(0, bg_video.duration - duration)
        bg_video = bg_video.with_start(-bg_start_time, False)

        # TODO: Content Clip should be properly sized depending on if it's portrait or landscape
        if self.content["type"] == "image":
            content_clip = mp.ImageClip(self.content["path"])
        else:

            content_clip = mp.VideoFileClip(self.content["path"])
            print(content_clip.audio)
            duration = min(content_clip.duration * 2, 60)
            content_clip = mp.vfx.Loop().apply(content_clip)

        content_clip = (
            content_clip.resized(width=dimensions["width"] * 0.92)
            .with_duration(duration)
            .with_position("center")
        )

        content_clip = content_clip.with_position(
            (
                "center",
                dimensions["height"] - content_clip.h - (dimensions["height"] * 0.30),
            )
        )

        title_clip = (
            mp.TextClip(
                text=f"{self.title}!!",
                font="Comicy.otf",
                color="white",
                stroke_color="black",
                stroke_width=2,
                size=(dimensions["width"], None),
                font_size=52,
                method="caption",
                text_align="center",
            )
            .with_position(("center", "center"))
            .with_duration(duration)
        )

        title_clip = title_clip.with_position(("center", dimensions["height"] * 0.15))

        composite = mp.CompositeVideoClip(
            [bg_color, bg_video, content_clip, title_clip]
        )
        
        # composite = composite.with_audio(music)
        composite = composite.with_duration(duration)
        composite.write_videofile(self.output_path, fps=30, remove_temp=True)
