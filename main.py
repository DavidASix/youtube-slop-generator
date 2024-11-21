from reddit import RedditScraper
from pprint import pprint

def main():
    scraper = RedditScraper("MinecraftMemes")
    scraper.save_media()
    print(scraper.manifest)

if __name__ == "__main__":
    main()