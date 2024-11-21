from reddit import RedditScraper
from generator import Video
from pprint import pprint

def main():
    scraper = RedditScraper("MinecraftMemes")
    #scraper.save_media()
    print(scraper.manifest)
    for item in scraper.manifest:
        video = Video(item)
        video.generate_short()
        # TODO: Post Video
        exit()

if __name__ == "__main__":
    main()