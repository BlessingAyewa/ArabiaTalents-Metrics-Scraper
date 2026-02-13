from dotenv import load_dotenv
import os
import re
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import json
import asyncio


load_dotenv()
developer_key = os.getenv('DEVELOPER_KEY')
api_service_name = 'youtube'
api_version = 'v3'
pattern = [r'([\w\W]+)v=([\w\W.]{11})', r'([\w\W]+)live/([\w\W.]{11})', r'([\w\W]+).be/([\w\W.]{11})', r'([\w\W]+)shorts/([\w\W.]{11})']
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/json,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}


# Connection Engines
youtube = build(api_service_name, api_version, developerKey=developer_key)


def regex_match(pattern: list, url: str):
    try:
        for pat in pattern:
            match = re.search(pat, url)
            if match:
                video_id = match.group(2)
                return video_id
                break
    except Exception as e:
        print(f'Error Matching Regexp: {e}')


def regexp_count(text):    
    match = re.search(r'([\d,.]+)\s*([KMkm]?)', text.replace(',', ''))        
    number_part = float(match.group(1))
    suffix = match.group(2).upper()
    
    # Multiplier Map
    multipliers = {
        'K': 1000,
        'M': 1000000,
        '': 1
    }
    return int(number_part * multipliers.get(suffix, 1))


async def youtube_scraper(video_link, youtube_con):
    try:
        video_id = regex_match(
            pattern=pattern,
            url=video_link
        ) 
        # Wrap synchronous SDK call in a thread to prevent blocking
        loop = asyncio.get_event_loop()
        request = youtube_con.videos().list(id=video_id, part="statistics")
        response = await loop.run_in_executor(None, request.execute)

        stats = response['items'][0]['statistics']

        scraped_views = int(stats['viewCount'])
        scraped_likes = int(stats['likeCount'])
        scraped_comments = int(stats['commentCount'])
        
        return scraped_views, scraped_likes, scraped_comments
    except Exception as e:
        print(f'Error Getting Youtube Data: {e}')
        return 0, 0, 0


async def tiktok_scraper(video_link, http_session):
    try:
        async with http_session.get(video_link) as response:
            html_body = await response.text()
            soup = BeautifulSoup(html_body, 'html.parser')
            sub_html = soup.find('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')
            
            data = json.loads(sub_html.string)["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]['stats']
            scraped_views = data['playCount']
            scraped_likes = data['diggCount']
            scraped_comments = data['commentCount']
        
        return scraped_views, scraped_likes, scraped_comments
    except Exception as e:
        print(f'Error Getting Tiktok Data: {e}')
        return 0, 0, 0


async def facebook_scraper(video_link, browser):
    page = await browser.new_page()
    try:
        await page.goto(video_link, wait_until="load", timeout=20000)
       # await page.wait_for_selector('text="views"', timeout=5000)
        html_body = await page.content()
        
        soup = BeautifulSoup(html_body, 'html.parser')
        view_text = soup.find('span', class_='_26fq').text
        like_text = soup.find('span', class_="xt0b8zv").text
        comment_text = soup.select_one('span.html-span.xdj266r.x14z9mp.xat24cr.x1lziwak.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x1hl2dhg.x16tdsg8.x1vvkbs.xkrqix3.x1sur9pj').text        

        scraped_view = regexp_count(view_text)
        scraped_like = regexp_count(like_text)
        scraped_comment = regexp_count(comment_text)

        return scraped_view, scraped_like, scraped_comment    
    except Exception as e:
        print(f'Error Getting Facebook Data: {e}')
        return 0, 0, 0
    finally:
        await page.close()


async def scrape(row: list, session, browser, stopper):
    async with stopper:
        scrape_check = row[0]
        link = row[1]
        platform = row[2]
        old_view_count = row[3]
        old_like_count = row[4]
        old_comment_count = row[5]
        
        if scrape_check == 'FALSE':
            return int(old_view_count.strip()), int(old_like_count.strip()), int(old_comment_count.strip())
        
        if 'Youtube' in platform:
            scraped_views, scraped_likes, scraped_comments = await youtube_scraper(
                video_link=link,
                youtube_con=youtube
            )
        elif 'Tiktok' in platform:
            scraped_views, scraped_likes, scraped_comments = await tiktok_scraper(
                video_link=link,
                http_session=session
            )
        else:
            scraped_views, scraped_likes, scraped_comments = await facebook_scraper(
                video_link=link,
                browser=browser
            )
        return scraped_views, scraped_likes, scraped_comments
