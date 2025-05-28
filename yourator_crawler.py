import asyncio
import discord
import os
import random
import json
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from dotenv import dotenv_values
from pyquery import PyQuery as pq
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = dotenv_values(".env")
TOKEN = os.getenv('DISCORD_TOKEN') or config.get('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_YOURATOR_CHANNEL_ID') or dotenv_values(".env").get('DISCORD_YOURATOR_CHANNEL_ID'))

# Yourator URL
BASE_URL = "https://www.yourator.co/jobs"
PARAMS = {
    "area[]": ["TPE", "NWT"],
    "position[]": "full_time",
    "remoteWork[]": ["none", "full", "partial"],
    "sort": "most_related",
    "term[]": "QA Engineer",
    "page": 1
}

JOBS_PER_MESSAGE = 10
MAX_PAGES = 5 
KEYWORDS = [
    'qa', '測試', 'test', 'testing', 'sdet', 'quality', '品質', 'quality assurance', '軟體測試', '軟體測試工程師', 'set'
]

intents = discord.Intents.default()
client = discord.Client(intents=intents)

delete_tasks = []

async def fetch_jobs(page=1):
    logger.info(f"Fetching page {page}")
    
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        url = f"{BASE_URL}?area[]=TPE&area[]=NWT&position[]=full_time&remoteWork[]=none&remoteWork[]=full&remoteWork[]=partial&sort=most_related&term[]=QA%20Engineer&page={page}"
        
        driver.get(url)
          
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "flex.min-w-0.flex-auto.flex-col.flex-nowrap.py-3.pl-4.pr-5"))
        )
        
        html = driver.page_source
        doc = pq(html)
        jobs = []
        

        job_items = doc('div.flex.min-w-0.flex-auto.flex-col.flex-nowrap.py-3.pl-4.pr-5')
        logger.info(f"Found {len(job_items)} jobs on page {page}")
        
        for job_item in job_items:
            try:
                title = pq(job_item).find('p.truncate.text-general.font-bold.text-lightest-navy').text()
                if not any(k in title.lower() for k in KEYWORDS):
                    continue
                
                company = pq(job_item).find('p.flex-initial.truncate.text-sub.text-main-blue').text()
                
                info_items = pq(job_item).find('div.flex.shrink.gap-0\\.5.items-center.min-w-0.text-hint.leading-\\[1\\.125rem\\] span.truncate')
                location = info_items.eq(0).text() if info_items else "地點未指定"
                salary = info_items.eq(-1).text() if info_items else "薪資面議"
                
                job = {
                    'title': title,
                    'company': company,
                    'salary': salary,
                    'location': location
                }
                jobs.append(job)
                logger.info(f"Added job: {title} at {company}")
                
            except Exception as e:
                logger.error(f"Error processing job data: {str(e)}")
                continue
        
        driver.quit()
                
        return jobs
        
    except Exception as e:
        logger.error(f"Error fetching page {page}: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return []

async def send_jobs_to_discord(channel, jobs, page):
    if not jobs:
        logger.warning(f"No jobs to send for page {page}")
        return
        
    formatted_date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    for i in range(0, len(jobs), JOBS_PER_MESSAGE):
        batch_jobs = jobs[i:i + JOBS_PER_MESSAGE]
        page_header = f"📄 第 {page} 頁職缺資訊 (Yourator)\n⏰ 更新時間：{formatted_date}\n\n"
        job_list = ""
        for index, job in enumerate(batch_jobs, start=i+1):
            job_list += (
                f"【職缺 {index}】\n"
                f"📌 職位：{job['title']}\n"
                f"🏢 公司：{job['company']}\n"
                f"💰 薪資：{job['salary']}\n"
                f"📍 地點：{job['location']}\n\n"
            )
        message = page_header + job_list
        try:
            msg = await channel.send(message)
            task = asyncio.create_task(delete_later(msg, 18000))
            delete_tasks.append(task)
            logger.info(f"Sent message with {len(batch_jobs)} jobs for page {page}")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")

async def delete_later(msg, delay):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
        logger.info("Message deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete message: {str(e)}")

@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user}')
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        logger.error(f"Could not find channel with ID {CHANNEL_ID}")
        await client.close()
        return
        
    try:
        for page in range(1, MAX_PAGES + 1):
            jobs = await fetch_jobs(page)
            if jobs:
                await send_jobs_to_discord(channel, jobs, page)
                await asyncio.sleep(10)
            else:
                logger.warning(f"No jobs found on page {page}, stopping")
                break
                
        if delete_tasks:
            await asyncio.gather(*delete_tasks)
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
            
    await client.close()

client.run(TOKEN)
