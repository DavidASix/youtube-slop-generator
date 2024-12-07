from reddit import RedditScraper
from generator import Video
from youtube_api import YouTube


def main():
    scraper = RedditScraper("MinecraftMemes")
    # scraper.save_media()
    youtube = YouTube()
    print(scraper.manifest)
    for item in scraper.manifest:
        video = Video(item)
        video.generate_short()
        video_data = youtube.upload_video(
            file_path=video.output_path,
            title=video.title,
            description=video.description,
            tags=video.tags,
        )
        print(f"Video uploaded with ID: {video_data['id']}")


if __name__ == "__main__":
    main()
