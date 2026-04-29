import discord
from discord.ext import commands
import sqlite3

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Подключение к БД
conn = sqlite3.connect("pointsp.db")
cursor = conn.cursor()

# Создание таблицы
cursor.execute("""
CREATE TABLE IF NOT EXISTS points (
    user_id INTEGER PRIMARY KEY,
    points INTEGER
)
""")
conn.commit()

ALLOWED_ROLE_ID = 1496560709973049526,1479285767342915604

def add_points(user_id, amount):
    cursor.execute("SELECT points FROM points WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        cursor.execute("INSERT INTO points (user_id, points) VALUES (?, ?)", (user_id, amount))
    else:
        cursor.execute("UPDATE points SET points = points + ? WHERE user_id = ?", (amount, user_id))

    conn.commit()


def get_points(user_id):
    cursor.execute("SELECT points FROM points WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0


@bot.event
async def on_ready():
    print(f'Бот запущен как {bot.user}')


@bot.command()
async def выдать(ctx, member: discord.Member, amount: int):
    if member.id == ctx.author.id:
        await ctx.reply("? Ты не можешь выдавать поинты самому себе.")
        return

    if ALLOWED_ROLE_ID == ctx.

    if amount <= 0:
        await ctx.reply("? Укажи положительное число.")
        return

    add_points(member.id, amount)
    total = get_points(member.id)

    embed = discord.Embed(
        title="?? Начисление баллов",
        description=f"{member.mention} получает баллы!",
        color=discord.Color.green()
    )

    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

    embed.add_field(name="?? Начислено", value=f"+{amount}", inline=True)
    embed.add_field(name="?? Баланс", value=f"{total}", inline=True)

    embed.set_footer(text=f"Выдал: {ctx.author}")

    await ctx.reply(embed=embed)

@bot.command()
async def снять(ctx, member: discord.Member, amount: int):
    if member.id == ctx.author.id:
        await ctx.reply("? Ты не можешь снимать поинты самому себе.")
        return

    if amount <= 0:
        await ctx.reply("? Укажи положительное число.")
        return

    current = get_points(member.id)

    if current <= 0:
        await ctx.reply(f"? У {member.mention} нет баллов.")
        return

    amount = min(amount, current)

    cursor.execute(
        "UPDATE points SET points = points - ? WHERE user_id = ?",
        (amount, member.id)
    )
    conn.commit()

    total = get_points(member.id)

    embed = discord.Embed(
        title="?? Списание баллов",
        description=f"С {member.mention} списаны баллы",
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

    embed.add_field(name="?? Списано", value=f"-{amount}", inline=True)
    embed.add_field(name="?? Осталось", value=f"{total}", inline=True)

    embed.set_footer(text=f"Списал: {ctx.author}")

    await ctx.reply(embed=embed)


@bot.command()
async def баллы(ctx, member: discord.Member = None):
    member = member or ctx.author
    points = get_points(member.id)

    embed = discord.Embed(
        title="?? Баланс пользователя",
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

    embed.add_field(name="?? Пользователь", value=member.mention, inline=True)
    embed.add_field(name="?? Баллы", value=f"**{points}**", inline=True)

    embed.set_footer(
        text=f"Запросил: {ctx.author}",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
    )

    embed.set_author(
        name=str(member),
        icon_url=member.avatar.url if member.avatar else member.default_avatar.url
    )

    await ctx.reply(embed=embed)

@bot.command()
async def лидеры(ctx):
    cursor.execute("SELECT user_id, points FROM points ORDER BY points DESC LIMIT 10")
    results = cursor.fetchall()

    if not results:
        await ctx.reply("? Пока нет данных.")
        return

    embed = discord.Embed(
        title="?? Таблица лидеров",
        description="Топ игроков по поинтам",
        color=discord.Color.gold()
    )

    medals = ["??", "??", "??"]
    lines = []

    for i, (user_id, points) in enumerate(results):
        member = ctx.guild.get_member(user_id)

        # ВСЕГДА стараемся получить пинг
        if member:
            user_text = member.mention
        else:
            user_text = f"<@{user_id}>"

        prefix = medals[i] if i < 3 else f"{i+1}."
        lines.append(f"{prefix} {user_text} — **{points}** ??")

    embed.description = "\n".join(lines)

    embed.set_footer(text=f"Запросил: {ctx.author}")

    await ctx.reply(embed=embed)

@bot.command()
async def хелп(ctx):
    embed = discord.Embed(
        title="?? Помощь по командам",
        description="Список доступных команд бота",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="?? Экономика",
        value=(
            "`!баллы [@user]` — посмотреть баланс\n"
            "`!выдать @user число` — выдать поинты\n"
            "`!снять @user число` — снять поинты\n"
            "`!лидеры` — топ игроков"
        ),
        inline=False
    )

    embed.add_field(
        name="?? Информация",
        value=(
            "`!хелп` — список команд\n"
        ),
        inline=False
    )

    embed.add_field(
        name="?? Ограничения",
        value=(
            "? Нельзя выдавать/снимать себе\n"
            "?? Все данные сохраняются в базе"
        ),
        inline=False
    )

    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)

    embed.set_footer(
        text=f"Запросил: {ctx.author}",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
    )

    await ctx.reply(embed=embed)

bot.run("MTQ5NjU2NjUwMTcyMzg2NTIyMA.GImjF0.NL4XIRyU1xgB-kFBdeSXprlBS2OaETnhU0T5WA")