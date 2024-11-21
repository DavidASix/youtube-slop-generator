from reddit import RedditScraper
from pprint import pprint

def main():
    scraper = RedditScraper("MinecraftMemes")
    
    pprint(scraper.recent_posts)

    scraper.save_media()

if __name__ == "__main__":
    main()