import asyncio
from script import scrape
import aiohttp
import gspread
from playwright.async_api import async_playwright


gc = gspread.service_account(filename='goolglesheet-connect.json') 


async def main():
    try:
        async with async_playwright() as p:
        
            browser = await p.chromium.launch(headless=True)

            async with aiohttp.ClientSession() as session:
                loop = asyncio.get_event_loop()

                sh = await loop.run_in_executor(None, gc.open, 'Video Stats Scraper')
                worksheet = await loop.run_in_executor(None, sh.worksheet, 'Sheet1')
                all_values = await loop.run_in_executor(None, worksheet.get_all_values)    
                worksheet_data = all_values[2:]

                stopper = asyncio.Semaphore(10)
                tasks = [scrape(row, session, browser, stopper) for row in worksheet_data]
                results = await asyncio.gather(*tasks)        

                # Updating the googlesheet
                await loop.run_in_executor(None, worksheet.update, results, 'D3')
                print('Stats scraped success successfully!')
    except Exception as e:
        print(f'Error Starting main script: {e}')

if __name__ == '__main__':
    asyncio.run(main())
