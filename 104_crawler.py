import asyncio
import discord
import aiohttp
import os
import random
import json
import logging

from dotenv import dotenv_values

from pyquery import PyQuery as pq
from datetime import datetime, timedelta


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = dotenv_values(".env")
TOKEN = os.getenv('DISCORD_TOKEN') or config.get('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_104_CHANNEL_ID') or dotenv_values(".env").get('DISCORD_104_CHANNEL_ID'))

# 104 API URL
API_URL = "https://www.104.com.tw/jobs/search/list"
PARAMS = {
    "area": "6001001000,6001002000",  # Taipei, New Taipei
    "jobsource": "joblist_search",
    "keyword": "軟體測試工程師",
    "mode": "s",
    "order": "3",
    "asc": "0",
    "searchTempExclude": "2",
    "excludeIndustryCat": "1009001000",
    "jobexp": "10,5,3",
    "ro": "1",
    "page": "1",
    "rows": "20"
}

JOBS_PER_MESSAGE = 10
MAX_PAGES = 5 
KEYWORDS = [
    'qa', '測試', 'test', 'testing', 'sdet', 'quality', '品質', 'quality assurance', '軟體測試', '軟體測試工程師', 'set'
]

intents = discord.Intents.default()
client = discord.Client(intents=intents)

delete_tasks = []

async def fetch_jobs(session, page=1):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.104.com.tw/jobs/search/',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    params = PARAMS.copy()
    params['page'] = str(page)
    
    logger.info(f"Fetching page {page}")
    
    try:
        async with session.get(API_URL, params=params, headers=headers) as response:
            if response.status != 200:
                logger.error(f"Failed to fetch page {page}, status code: {response.status}")
                return []
            
            data = await response.json()
            jobs = []
            
            if 'data' in data and 'list' in data['data']:
                job_list = data['data']['list']
                logger.info(f"Found {len(job_list)} jobs on page {page}")
                
                for job_data in job_list:
                    try:
                        title = job_data.get('jobName', '')
                        if not any(k in title.lower() for k in KEYWORDS):
                            continue
                            
                        company = job_data.get('custName', '')
                        salary = job_data.get('salaryDesc', '薪資面議')
                        location = job_data.get('jobAddrNoDesc', '') or "地點未指定"
                        
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
                        
            return jobs
            
    except Exception as e:
        logger.error(f"Error fetching page {page}: {str(e)}")
        return []

async def send_jobs_to_discord(channel, jobs, page):
    if not jobs:
        logger.warning(f"No jobs to send for page {page}")
        return
        
    formatted_date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    for i in range(0, len(jobs), JOBS_PER_MESSAGE):
        batch_jobs = jobs[i:i + JOBS_PER_MESSAGE]
        page_header = f"📄 第 {page} 頁職缺資訊 (104)\n⏰ 更新時間：{formatted_date}\n\n"
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
        
    connector = aiohttp.TCPConnector(limit=1)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            for page in range(1, MAX_PAGES + 1):
                jobs = await fetch_jobs(session, page)
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
        finally:
            await session.close()
            
    await client.close()

client.run(TOKEN) 