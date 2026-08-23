import os
import html
import logging

from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
FORCE_CHANNEL = os.getenv("FORCE_CHANNEL", "@mani_bio")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ==================================================
# PREMIUM CUSTOM EMOJIS
# ==================================================

MUSIC = '<tg-emoji emoji-id="5463107823946717464">🎵</tg-emoji>'
SEARCH = '<tg-emoji emoji-id="5397986013681295058">🔎</tg-emoji>'
DOWNLOAD = '<tg-emoji emoji-id="6203886371363364022">📥</tg-emoji>'
HELP = '<tg-emoji emoji-id="5274099962655816924">ℹ️</tg-emoji>'
AUDIO = '<tg-emoji emoji-id="5404416185313818354">🎧</tg-emoji>'
CROWN = '<tg-emoji emoji-id="6206096153511990389">👑</tg-emoji>'
SUCCESS = '<tg-emoji emoji-id="6305150619187418915">✅</tg-emoji>'
USER = '<tg-emoji emoji-id="6307777408300753473">👤</tg-emoji>'

PREMIUM = '<tg-emoji emoji-id="6206027872121918710">💎</tg-emoji>'
FAST = '<tg-emoji emoji-id="5427168083074628963">⚡</tg-emoji>'
SECURITY = '<tg-emoji emoji-id="5240241223632954241">🛡️</tg-emoji>'
PLAYLIST = '<tg-emoji emoji-id="5197269100878907942">📋</tg-emoji>'
LIKE = '<tg-emoji emoji-id="5388790256772331442">❤️</tg-emoji>'
HISTORY = '<tg-emoji emoji-id="5467538555158943525">📅</tg-emoji>'

# ==================================================
# FORCE JOIN
# ==================================================

async def is_joined(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(
            chat_id=FORCE_CHANNEL,
            user_id=user_id,
        )

        return member.status in (
            "member",
            "administrator",
            "creator",
        )

    except Exception as e:
        logging.error("Force join check failed: %s", e)
        return False


# ==================================================
# HOME
# ==================================================

async def send_home(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    name = html.escape(user.first_name or "User")

    text = (
        f"{MUSIC} <b>PREMIUM MUSIC BOT</b>\n\n"
        f"{USER} Welcome, <b>{name}</b>!\n\n"

        f"{AUDIO} <b>Music Search & Player</b>\n"
        f"{SEARCH} Search your favourite music\n"
        f"{PLAYLIST} Create playlists\n"
        f"{LIKE} Save favourite tracks\n"
        f"{HISTORY} Listening history\n\n"

        f"{PREMIUM} <b>Premium Experience</b>\n"
        f"{FAST} Fast & modern system\n"
        f"{SECURITY} Secure & protected\n\n"

        f"{SUCCESS} <b>Status:</b> Online\n\n"
        f"👇 <b>Select an option:</b>"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🔎 Search Music",
                callback_data="search_music",
            ),
            InlineKeyboardButton(
                "👤 My Profile",
                callback_data="profile",
            ),
        ],
        [
            InlineKeyboardButton(
                "🎧 Player",
                callback_data="player",
            ),
            InlineKeyboardButton(
                "❤️ Favorites",
                callback_data="favorites",
            ),
        ],
        [
            InlineKeyboardButton(
                "📋 Playlist",
                callback_data="playlist",
            ),
            InlineKeyboardButton(
                "💎 VIP",
                callback_data="vip",
            ),
        ],
        [
            InlineKeyboardButton(
                "📅 History",
                callback_data="history",
            ),
            InlineKeyboardButton(
                "⚙️ Settings",
                callback_data="settings",
            ),
        ],
        [
            InlineKeyboardButton(
                "ℹ️ Help",
                callback_data="help",
            ),
        ],
    ]

    await update.effective_message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ==================================================
# START
# ==================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if not user:
        return

    joined = await is_joined(
        context.bot,
        user.id,
    )

    if not joined:

        text = (
            f"{MUSIC} <b>Premium Music Bot</b>\n\n"
            f"🔒 <b>Join Required</b>\n\n"
            "Bot use karne ke liye pehle hamara channel join karo.\n\n"
            f"{DOWNLOAD} Join karne ke baad "
            "<b>I've Joined</b> press karo."
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "📢 Join Channel",
                    url="https://t.me/mani_bio",
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ I've Joined",
                    callback_data="check_join",
                )
            ],
        ]

        await update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return

    await send_home(update, context)


# ==================================================
# CALLBACKS
# ==================================================

async def callbacks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    await query.answer()

    if query.data == "check_join":

        joined = await is_joined(
            context.bot,
            query.from_user.id,
        )

        if not joined:

            await query.answer(
                "❌ Pehle channel join karo.",
                show_alert=True,
            )

            return

        await query.message.delete()

        await send_home(update, context)

        return

    if query.data == "search_music":

        await query.message.reply_text(
            f"{SEARCH} <b>Music Search</b>\n\n"
            f"{AUDIO} Song ya artist ka naam bhejo.\n\n"
            "Example: <code>Imagine Dragons</code>",
            parse_mode=ParseMode.HTML,
        )

        return

    if query.data == "profile":

        user = query.from_user

        await query.message.reply_text(
            f"{USER} <b>Your Profile</b>\n\n"
            f"🆔 <code>{user.id}</code>\n"
            f"👤 <b>Name:</b> "
            f"{html.escape(user.full_name)}\n"
            f"🔹 <b>Username:</b> "
            f"@{html.escape(user.username) if user.username else 'None'}",
            parse_mode=ParseMode.HTML,
        )

        return

    if query.data == "help":

        await query.message.reply_text(
            f"{HELP} <b>Command Guide</b>\n\n"
            "/start — Open bot\n"
            "/id — Get your Telegram ID\n"
            "/help — Help menu",
            parse_mode=ParseMode.HTML,
        )

        return

    if query.data == "vip":

        await query.message.reply_text(
            f"{CROWN} <b>VIP System</b>\n\n"
            f"{PREMIUM} VIP features will be available here.",
            parse_mode=ParseMode.HTML,
        )

        return

    if query.data in (
        "player",
        "favorites",
        "playlist",
        "history",
        "settings",
    ):

        await query.message.reply_text(
            f"{FAST} <b>Coming Soon</b>\n\n"
            "This module is being prepared.",
            parse_mode=ParseMode.HTML,
        )

        return


# ==================================================
# /ID
# ==================================================

async def user_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    await update.message.reply_text(
        f"{USER} <b>Your Telegram ID</b>\n\n"
        f"<code>{user.id}</code>",
        parse_mode=ParseMode.HTML,
    )


# ==================================================
# /HELP
# ==================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        f"{HELP} <b>Premium Music Bot</b>\n\n"
        "/start — Start bot\n"
        "/id — Your Telegram ID\n"
        "/help — Command guide",
        parse_mode=ParseMode.HTML,
    )


# ==================================================
# MAIN
# ==================================================

def main():

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("id", user_id)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        CallbackQueryHandler(callbacks)
    )

    logging.info("Premium Music Bot started.")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
