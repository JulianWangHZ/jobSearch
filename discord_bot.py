import asyncio
import discord
import aiohttp
import os

from dotenv import dotenv_values
from pyquery import PyQuery as pq
from datetime import datetime, timedelta

# use environment variables first, then use .env file
TOKEN = os.getenv('DISCORD_TOKEN') or dotenv_values(".env").get('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID') or dotenv_values(".env").get('DISCORD_CHANNEL_ID'))

BASE_URL = "https://www.cake.me/jobs/qa%20engineer"
PARAMS = {
    "location_list[0]": "Taipei City, Taiwan",
    "location_list[1]": "New Taipei City, Taiwan",
    "job_type[0]": "full_time",
    "seniority_level[0]": "entry_level",
    "seniority_level[1]": "mid_senior_level"
}
JOBS_PER_MESSAGE = 10
MAX_PAGES = 9
KEYWORDS = [
    'qa', '測試', 'test', 'testing', 'sdet', 'quality', '品質', 'quality assurance', '軟體測試'
]

intents = discord.Intents.default()
client = discord.Client(intents=intents)

delete_tasks = []

async def fetch_jobs(session, page=1):
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"{BASE_URL}?page={page}"
    for key, value in PARAMS.items():
        url += f"&{key}={value}"
    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            return []
        text = await response.text()
        doc = pq(text)
        jobs = []
        job_elements = doc('.JobSearchItem_container__oKoBL')
        for each in job_elements.items():
            title = each('.JobSearchItem_jobTitle__bu6yO').text()
            title = title.replace('\n', ' ').replace('\r', ' ').strip()
            if not any(k in title.lower() for k in KEYWORDS):
                continue
            company = each('.JobSearchItem_companyName__bY7JI').text()
            salary_element = each('.InlineMessage_label__LJGjW:contains(\"TWD\")')
            salary = salary_element.text() if salary_element else "薪資面議"
            job_link = each('.JobSearchItem_jobTitle__bu6yO').attr('href')
            if job_link and not job_link.startswith('http'):
                job_link = f"https://www.cake.me{job_link}"
            job = {
                'title': title,
                'company': company,
                'salary': salary,
                'url': job_link
            }
            if job['title'] and job['company']:
                jobs.append(job)
        return jobs

async def send_jobs_to_discord(channel, jobs, page):
    formatted_date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    for i in range(0, len(jobs), JOBS_PER_MESSAGE):
        batch_jobs = jobs[i:i + JOBS_PER_MESSAGE]
        page_header = f"📄 第 {page} 頁職缺資訊\n⏰ 更新時間：{formatted_date}\n\n"
        job_list = ""
        for index, job in enumerate(batch_jobs, start=i+1):
            job_list += (
                f"【職缺 {index}】\n"
                f"📌 職位：{job['title']}\n"
                f"🏢 公司：{job['company']}\n"
                f"💰 薪資：{job['salary']}\n"
                f"🔗 職缺連結：{job['url']}\n\n"
            )
        message = page_header + job_list
        msg = await channel.send(message)
        task = asyncio.create_task(delete_later(msg, 18000))
        delete_tasks.append(task)

async def delete_later(msg, delay):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception as e:
        print(f"Failed to delete message: {e}")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel = client.get_channel(CHANNEL_ID)
    async with aiohttp.ClientSession() as session:
        for page in range(1, MAX_PAGES + 1):
            jobs = await fetch_jobs(session, page)
            if jobs:
                await send_jobs_to_discord(channel, jobs, page)
                await asyncio.sleep(10)
            else:
                break
    if delete_tasks:
        await asyncio.gather(*delete_tasks)
    await client.close()

client.run(TOKEN)