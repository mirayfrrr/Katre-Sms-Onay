from keep_alive import keep_alive
keep_alive()

import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# --- AYARLAR ---
BOT_TOKEN = "8197121234:AAEWzGy56oLW9i3OKxI-gyZM6ywN1zpWyw0"
ADMIN_ID = 6484811971
BOT_USERNAME = "KatreSmsOnayBot"
REQUIRED_CHANNEL = "@KatreSms"
REQUIRED_GROUP = "https://t.me/KatreSmsChat"  # Yeni grup
REQUIRED_GROUP_ID = "-1002900454087"  # Bu ID'yi gerÃ§ek grup ID'si ile deÄŸiÅŸtirin

# --- VERÄ° DOSYALARI ---
USERS_FILE = "users.json"
STOCK_FILE = "stock.json"
BANNED_FILE = "banned.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_banned():
    try:
        with open(BANNED_FILE, "r") as f:
            return json.load(f)
    except:
        return {"banned_users": []}

def save_banned(banned_data):
    with open(BANNED_FILE, "w") as f:
        json.dump(banned_data, f, indent=2)

def load_stock():
    try:
        with open(STOCK_FILE, "r") as f:
            return json.load(f)
    except:
        return {"numbers": []}

def save_stock(stock):
    with open(STOCK_FILE, "w") as f:
        json.dump(stock, f, indent=2)

def get_greeting():
    import datetime
    now = datetime.datetime.now()
    hour = now.hour
    
    if 5 <= hour < 12:
        return "ðŸŒ… GÃ¼naydÄ±n!"
    elif 12 <= hour < 18:
        return "â˜€ï¸ Ä°yi gÃ¼nler!"
    elif 18 <= hour < 22:
        return "ðŸŒ† Ä°yi akÅŸamlar!"
    else:
        return "ðŸŒ™ Ä°yi geceler!"

def calculate_level(tokens):
    """Jeton sayÄ±sÄ±na gÃ¶re seviye hesapla"""
    if tokens < 10:
        return 1, 10 - tokens  # Seviye 1, kalan jeton
    elif tokens < 30:  # 10 + 20 = 30
        return 2, 30 - tokens  # Seviye 2, kalan jeton
    elif tokens < 60:  # 10 + 20 + 30 = 60
        return 3, 60 - tokens  # Seviye 3, kalan jeton
    elif tokens < 100:  # 10 + 20 + 30 + 40 = 100
        return 4, 100 - tokens
    elif tokens < 150:  # +50 = 150
        return 5, 150 - tokens
    elif tokens < 210:  # +60 = 210
        return 6, 210 - tokens
    elif tokens < 280:  # +70 = 280
        return 7, 280 - tokens
    elif tokens < 360:  # +80 = 360
        return 8, 360 - tokens
    elif tokens < 450:  # +90 = 450
        return 9, 450 - tokens
    else:
        return 10, 0  # Maksimum seviye

def get_level_emoji(level):
    """Seviyeye gÃ¶re emoji dÃ¶ndÃ¼r"""
    emojis = {
        1: "ðŸ¥‰", 2: "ðŸ¥ˆ", 3: "ðŸ¥‡", 4: "ðŸ’Ž", 5: "ðŸ‘‘",
        6: "ðŸ†", 7: "â­", 8: "ðŸŒŸ", 9: "ðŸ’«", 10: "ðŸŽ–ï¸"
    }
    return emojis.get(level, "ðŸ…")

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = str(user.id)
    users = load_users()
    banned = load_banned()

    # Ban kontrolÃ¼
    if user_id in banned["banned_users"]:
        await update.message.reply_text(
            "ðŸš« ÃœzgÃ¼nÃ¼z, botumuz tarafÄ±ndan engellendiniz.\n"
            "Daha fazla bilgi iÃ§in admin ile iletiÅŸime geÃ§in â†’ @SiberSubeden"
        )
        return

    # Referans parametresini al ve geÃ§ici kaydet
    ref_id = None
    if context.args:
        ref_id = context.args[0].replace("ref", "")

    # EÄŸer kullanÄ±cÄ± daha Ã¶nce kaydedilmemiÅŸse, referans bilgisini geÃ§ici olarak kaydet
    if user_id not in users:
        users[user_id] = {
            "name": user.first_name,
            "tokens": 0,
            "temp_ref": ref_id if ref_id and ref_id != user_id and ref_id in users else None
        }
        save_users(users)

    # Kanal doÄŸrulamasÄ±
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user.id)
        if member.status not in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            keyboard = [[InlineKeyboardButton("âœ… Kanala KatÄ±l", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")]]
            await update.message.reply_text(
                "ðŸš¨ Botu kullanmak iÃ§in Ã¶nce kanala katÄ±lmalÄ±sÄ±n.\n"
                "Kanala katÄ±ldÄ±ktan sonra tekrar /start yazman yeterli.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
    except:
        await update.message.reply_text("âš ï¸ Kanal bulunamadÄ± veya bot yetkisi yok.")
        return

    # Grup doÄŸrulamasÄ±
    try:
        member = await context.bot.get_chat_member(REQUIRED_GROUP_ID, user.id)
        if member.status not in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            keyboard = [[InlineKeyboardButton("âœ… Gruba KatÄ±l", url=REQUIRED_GROUP)]]
            await update.message.reply_text(
                "ðŸš¨ Botu kullanmak iÃ§in Ã¶nce doÄŸrulama grubuna katÄ±lmalÄ±sÄ±n.\n"
                "Gruba katÄ±ldÄ±ktan sonra tekrar /start yazman yeterli.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
    except:
        await update.message.reply_text("âš ï¸ DoÄŸrulama grubu bulunamadÄ± veya bot yetkisi yok.")
        return

    # KullanÄ±cÄ± hem kanala hem gruba Ã¼ye, referans kontrolÃ¼ yap
    user_data = users[user_id]
    if user_data.get("temp_ref") and user_data["temp_ref"] in users:
        inviter_id = user_data["temp_ref"]
        inviter_name = users[inviter_id]["name"]
        
        # Davet edene jeton ekle
        users[inviter_id]["tokens"] += 1
        
        # Referans bilgisini temizle
        users[user_id]["temp_ref"] = None
        save_users(users)
        
        # Davet edene mesaj gÃ¶nder
        try:
            await context.bot.send_message(
                chat_id=inviter_id,
                text=f"ðŸŽ‰ ReferansÄ±nÄ±z sayÄ±ldÄ±!\n"
                     f"ðŸ‘¤ Davet edilen: {user.first_name}\n"
                     f"ðŸŽ +1 jeton kazandÄ±nÄ±z!"
            )
        except:
            pass  # Mesaj gÃ¶nderilemezse sessizce devam et
        
        # Davet edilene mesaj gÃ¶nder
        greeting = get_greeting()
        await update.message.reply_text(
            f"{greeting}\n"
            f"ðŸŽ‰ BaÅŸarÄ±yla {inviter_name} tarafÄ±ndan davet edildiniz!\n"
            f"HoÅŸ geldin {user.first_name}!"
        )
    else:
        # Normal hoÅŸ geldin mesajÄ±
        greeting = get_greeting()
        await update.message.reply_text(f"{greeting}\nHoÅŸ geldin {user.first_name}!")

    # MenÃ¼ aÃ§
    await show_menu(update, users[user_id]["tokens"], user_id)

# --- MENÃœ ---
async def show_menu(update: Update, tokens: int, user_id: str):
    level, remaining = calculate_level(tokens)
    level_emoji = get_level_emoji(level)
    
    keyboard = [
        [InlineKeyboardButton("ðŸŽ JetonlarÄ±m", callback_data="my_tokens")],
        [InlineKeyboardButton("ðŸŽ¯ Referans Linkim", callback_data="my_ref")],
        [InlineKeyboardButton("ðŸ“± Numara Al", callback_data="get_number")],
    ]
    text = (f"ðŸ“‹ MenÃ¼\n\n"
            f"ðŸ‘¤ KullanÄ±cÄ± ID: {user_id}\n"
            f"ðŸŽ Jeton SayÄ±n: {tokens}\n"
            f"{level_emoji} Seviye: {level}")
    
    if level < 10:
        text += f"\nðŸ“ˆ Bir sonraki seviye iÃ§in: {remaining} jeton kaldÄ±"
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def menu_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    users = load_users()
    banned = load_banned()

    # Ban kontrolÃ¼
    if user_id in banned["banned_users"]:
        await query.edit_message_text(
            "ðŸš« ÃœzgÃ¼nÃ¼z, botumuz tarafÄ±ndan engellendiniz.\n"
            "Daha fazla bilgi iÃ§in admin ile iletiÅŸime geÃ§in â†’ @SiberSubeden"
        )
        return

    if query.data == "my_tokens":
        tokens = users[user_id]["tokens"]
        await query.edit_message_text(
            f"ðŸŽ Jeton sayÄ±n: {tokens}",
            reply_markup=query.message.reply_markup
        )

    elif query.data == "my_ref":
        link = f"https://t.me/{BOT_USERNAME}?start=ref{user_id}"
        await query.edit_message_text(
            f"ðŸŽ¯ Referans linkin:\n{link}",
            reply_markup=query.message.reply_markup
        )

    elif query.data == "get_number":
        tokens = users[user_id]["tokens"]
        if tokens >= 10:
            # Stok kontrolÃ¼
            stock = load_stock()
            if not stock["numbers"]:
                await query.edit_message_text(
                    "âŒ ÃœzgÃ¼nÃ¼z! Åžu anda numara stoÄŸumuz bulunmuyor.\n"
                    "Admin ile iletiÅŸime geÃ§ebilirsiniz â†’ @SiberSubeden",
                    reply_markup=query.message.reply_markup
                )
                return
            
            # Stoktan bir numara al
            number = stock["numbers"].pop(0)
            save_stock(stock)
            
            # Jetonu dÃ¼ÅŸ
            users[user_id]["tokens"] -= 10
            save_users(users)
            
            # NumarayÄ± kullanÄ±cÄ±ya gÃ¶nder
            await query.edit_message_text(
                f"ðŸŽ‰ Numara baÅŸarÄ±yla alÄ±ndÄ±!\n\n"
                f"ðŸ“± NumaranÄ±z: `{number}`\n\n"
                f"KullanÄ±m talimatlarÄ± iÃ§in admin ile iletiÅŸime geÃ§in â†’ @SiberSubeden\n"
                f"ðŸŽ Kalan jeton: {users[user_id]['tokens']}",
                reply_markup=query.message.reply_markup,
                parse_mode="Markdown"
            )
            
            # Admin'e bildirim gÃ¶nder
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"ðŸ“± Numara AlÄ±mÄ±!\n\n"
                         f"ðŸ‘¤ KullanÄ±cÄ±: {users[user_id]['name']} ({user_id})\n"
                         f"ðŸ“± AlÄ±nan numara: {number}\n"
                         f"ðŸ“¦ Kalan stok: {len(stock['numbers'])}"
                )
            except:
                pass
        else:
            await query.edit_message_text(
                "âŒ Yetersiz jeton. En az 10 jeton gerekli.",
                reply_markup=query.message.reply_markup
            )

# --- ADMIN PANELÄ° ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("ðŸš« Yetkin yok.")
        return

    stock = load_stock()
    stock_count = len(stock["numbers"])
    
    keyboard = [
        [InlineKeyboardButton("ðŸ‘¥ KullanÄ±cÄ± Listesi", callback_data="adm_list")],
        [InlineKeyboardButton("âž•âž– Jeton YÃ¶net", callback_data="adm_tokens")],
        [InlineKeyboardButton("ðŸŽ Herkese Jeton Ver", callback_data="adm_give_all")],
        [InlineKeyboardButton("ðŸ“¢ Herkese Bildirim", callback_data="adm_broadcast")],
        [InlineKeyboardButton("ðŸ“¦ Stok YÃ¶net ({stock_count})", callback_data="adm_stock")],
        [InlineKeyboardButton("ðŸš« Ban YÃ¶netimi", callback_data="adm_ban")],
        [InlineKeyboardButton("ðŸ“‚ JSON DÄ±ÅŸa Aktar", callback_data="adm_export")],
    ]
    await update.message.reply_text(
        f"âš™ï¸ Admin Paneli\n\nðŸ“¦ Mevcut stok: {stock_count} numara",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("ðŸš« Yetkin yok.")
        return

    users = load_users()
    stock = load_stock()

    if query.data == "adm_list":
        text = "ðŸ‘¥ KullanÄ±cÄ±lar:\n\n"
        for uid, info in users.items():
            text += f"ID: {uid} | Ad: {info['name']} | Jeton: {info['tokens']}\n"
        await query.edit_message_text(text, reply_markup=query.message.reply_markup)

    elif query.data == "adm_tokens":
        text = (
            "âž•âž– Jeton YÃ¶netimi\n\n"
            "KomutlarÄ± kullan:\n"
            "`/addtokens <user_id> <sayÄ±>`\n"
            "`/removetokens <user_id> <sayÄ±>`"
        )
        await query.edit_message_text(text, reply_markup=query.message.reply_markup, parse_mode="Markdown")

    elif query.data == "adm_give_all":
        text = (
            "ðŸŽ Herkese Jeton Ver\n\n"
            "Komutu kullan:\n"
            "`/giveall <sayÄ±>`\n\n"
            "Ã–rnek: `/giveall 5` (herkese 5 jeton verir)"
        )
        await query.edit_message_text(text, reply_markup=query.message.reply_markup, parse_mode="Markdown")

    elif query.data == "adm_broadcast":
        text = (
            "ðŸ“¢ Herkese Bildirim GÃ¶nder\n\n"
            "Komutu kullan:\n"
            "`/broadcast <mesajÄ±nÄ±z>`\n\n"
            "Ã–rnek: `/broadcast Yeni gÃ¼ncelleme geldi!`\n"
            "TÃ¼m kullanÄ±cÄ±lara mesajÄ±nÄ±z iletilecek."
        )
        await query.edit_message_text(text, reply_markup=query.message.reply_markup, parse_mode="Markdown")

    elif query.data == "adm_stock":
        stock_count = len(stock["numbers"])
        text = (
            f"ðŸ“¦ Stok YÃ¶netimi\n\n"
            f"Mevcut stok: {stock_count} numara\n\n"
            "KomutlarÄ± kullan:\n"
            "`/addstock <numara1> <numara2> ...`\n"
            "`/clearstock` - TÃ¼m stoÄŸu temizle\n"
            "`/showstock` - Stoku gÃ¶ster\n\n"
            "Ã–rnek: `/addstock +905551234567 +905551234568`"
        )
        await query.edit_message_text(text, reply_markup=query.message.reply_markup, parse_mode="Markdown")

    elif query.data == "adm_ban":
        banned = load_banned()
        banned_count = len(banned["banned_users"])
        text = (
            f"ðŸš« Ban YÃ¶netimi\n\n"
            f"BanlÄ± kullanÄ±cÄ± sayÄ±sÄ±: {banned_count}\n\n"
            "KomutlarÄ± kullan:\n"
            "`/ban <user_id>` - KullanÄ±cÄ±yÄ± banla\n"
            "`/unban <user_id>` - BanÄ± kaldÄ±r\n"
            "`/banlist` - BanlÄ± kullanÄ±cÄ±larÄ± listele\n\n"
            "Ã–rnek: `/ban 123456789`"
        )
        await query.edit_message_text(text, reply_markup=query.message.reply_markup, parse_mode="Markdown")

    elif query.data == "adm_export":
        with open(USERS_FILE, "rb") as f:
            await query.message.reply_document(f, filename="users.json")

# --- STOK KOMUTLARI ---
async def add_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("âš ï¸ KullanÄ±m: /addstock <numara1> <numara2> ...")
        return
    
    stock = load_stock()
    added_numbers = []
    
    for number in context.args:
        if number not in stock["numbers"]:
            stock["numbers"].append(number)
            added_numbers.append(number)
    
    save_stock(stock)
    
    if added_numbers:
        await update.message.reply_text(
            f"âœ… {len(added_numbers)} numara stoÄŸa eklendi!\n\n"
            f"ðŸ“± Eklenen numaralar:\n" + "\n".join(added_numbers) + 
            f"\n\nðŸ“¦ Toplam stok: {len(stock['numbers'])}"
        )
    else:
        await update.message.reply_text("âš ï¸ HiÃ§bir yeni numara eklenmedi. (Zaten mevcut)")

async def clear_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    stock = load_stock()
    cleared_count = len(stock["numbers"])
    stock["numbers"] = []
    save_stock(stock)
    
    await update.message.reply_text(f"ðŸ—‘ï¸ Stok temizlendi! {cleared_count} numara silindi.")

async def show_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    stock = load_stock()
    if not stock["numbers"]:
        await update.message.reply_text("ðŸ“¦ Stok boÅŸ!")
        return
    
    stock_text = "ðŸ“¦ Mevcut Stok:\n\n" + "\n".join(stock["numbers"])
    stock_text += f"\n\nðŸ“Š Toplam: {len(stock['numbers'])} numara"
    
    if len(stock_text) > 4000:  # Telegram mesaj limiti
        await update.message.reply_text(f"ðŸ“¦ Toplam stok: {len(stock['numbers'])} numara\n(Ã‡ok fazla numara olduÄŸu iÃ§in liste gÃ¶sterilemiyor)")
    else:
        await update.message.reply_text(stock_text)

# --- BAN KOMUTLARI ---
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("âš ï¸ KullanÄ±m: /ban <user_id>")
        return
    
    user_id = context.args[0]
    users = load_users()
    banned = load_banned()
    
    if user_id not in users:
        await update.message.reply_text("ðŸš« KullanÄ±cÄ± bulunamadÄ±.")
        return
    
    if user_id in banned["banned_users"]:
        await update.message.reply_text("âš ï¸ KullanÄ±cÄ± zaten banlÄ±.")
        return
    
    banned["banned_users"].append(user_id)
    save_banned(banned)
    
    user_name = users[user_id]["name"]
    
    # KullanÄ±cÄ±ya bildirim gÃ¶nder
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="ðŸš« Botumuz tarafÄ±ndan engellendiniz.\n"
                 "Daha fazla bilgi iÃ§in admin ile iletiÅŸime geÃ§in â†’ @SiberSubeden"
        )
        await update.message.reply_text(f"âœ… {user_name} ({user_id}) baÅŸarÄ±yla banlandÄ± ve bildirim gÃ¶nderildi.")
    except:
        await update.message.reply_text(f"âœ… {user_name} ({user_id}) baÅŸarÄ±yla banlandÄ±. (Bildirim gÃ¶nderilemedi)")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("âš ï¸ KullanÄ±m: /unban <user_id>")
        return
    
    user_id = context.args[0]
    users = load_users()
    banned = load_banned()
    
    if user_id not in banned["banned_users"]:
        await update.message.reply_text("âš ï¸ KullanÄ±cÄ± zaten banlÄ± deÄŸil.")
        return
    
    banned["banned_users"].remove(user_id)
    save_banned(banned)
    
    user_name = users.get(user_id, {}).get("name", "Bilinmeyen")
    
    # KullanÄ±cÄ±ya bildirim gÃ¶nder
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="âœ… BanÄ±nÄ±z kaldÄ±rÄ±lmÄ±ÅŸtÄ±r!\n"
                 "ArtÄ±k botu tekrar kullanabilirsiniz. /start yazarak baÅŸlayÄ±n."
        )
        await update.message.reply_text(f"âœ… {user_name} ({user_id}) banÄ± kaldÄ±rÄ±ldÄ± ve bildirim gÃ¶nderildi.")
    except:
        await update.message.reply_text(f"âœ… {user_name} ({user_id}) banÄ± kaldÄ±rÄ±ldÄ±. (Bildirim gÃ¶nderilemedi)")

async def ban_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    banned = load_banned()
    users = load_users()
    
    if not banned["banned_users"]:
        await update.message.reply_text("ðŸ“ BanlÄ± kullanÄ±cÄ± bulunmuyor.")
        return
    
    ban_text = "ðŸš« BanlÄ± KullanÄ±cÄ±lar:\n\n"
    for user_id in banned["banned_users"]:
        user_name = users.get(user_id, {}).get("name", "Bilinmeyen")
        ban_text += f"â€¢ {user_name} ({user_id})\n"
    
    ban_text += f"\nðŸ“Š Toplam: {len(banned['banned_users'])} kullanÄ±cÄ±"
    await update.message.reply_text(ban_text)

# --- JETON KOMUTLARI ---
async def add_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        user_id = context.args[0]
        count = int(context.args[1])
    except:
        await update.message.reply_text("âš ï¸ KullanÄ±m: /addtokens <user_id> <sayÄ±>")
        return

    users = load_users()
    if user_id not in users:
        await update.message.reply_text("ðŸš« KullanÄ±cÄ± bulunamadÄ±.")
        return

    users[user_id]["tokens"] += count
    save_users(users)
    
    # KullanÄ±cÄ±ya bildirim gÃ¶nder
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"ðŸŽ Size {count} jeton eklendi!\n"
                 f"ðŸ’° Yeni bakiyeniz: {users[user_id]['tokens']} jeton"
        )
        await update.message.reply_text(f"âœ… {user_id} kullanÄ±cÄ±sÄ±na {count} jeton eklendi ve bildirim gÃ¶nderildi.")
    except:
        await update.message.reply_text(f"âœ… {user_id} kullanÄ±cÄ±sÄ±na {count} jeton eklendi. (Bildirim gÃ¶nderilemedi)")

async def remove_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        user_id = context.args[0]
        count = int(context.args[1])
    except:
        await update.message.reply_text("âš ï¸ KullanÄ±m: /removetokens <user_id> <sayÄ±>")
        return

    users = load_users()
    if user_id not in users:
        await update.message.reply_text("ðŸš« KullanÄ±cÄ± bulunamadÄ±.")
        return

    old_tokens = users[user_id]["tokens"]
    users[user_id]["tokens"] = max(0, users[user_id]["tokens"] - count)
    save_users(users)
    
    # KullanÄ±cÄ±ya bildirim gÃ¶nder
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"ðŸ“‰ HesabÄ±nÄ±zdan {count} jeton dÃ¼ÅŸÃ¼ldÃ¼.\n"
                 f"ðŸ’° Yeni bakiyeniz: {users[user_id]['tokens']} jeton"
        )
        await update.message.reply_text(f"âœ… {user_id} kullanÄ±cÄ±sÄ±ndan {count} jeton silindi ve bildirim gÃ¶nderildi.")
    except:
        await update.message.reply_text(f"âœ… {user_id} kullanÄ±cÄ±sÄ±ndan {count} jeton silindi. (Bildirim gÃ¶nderilemedi)")

async def give_all_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        count = int(context.args[0])
    except:
        await update.message.reply_text("âš ï¸ KullanÄ±m: /giveall <sayÄ±>")
        return

    users = load_users()
    success_count = 0
    total_users = len(users)
    
    await update.message.reply_text(f"ðŸ”„ {total_users} kullanÄ±cÄ±ya {count} jeton gÃ¶nderiliyor...")
    
    for user_id, user_data in users.items():
        users[user_id]["tokens"] += count
        # Her kullanÄ±cÄ±ya bildirim gÃ¶nder
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"ðŸŽ Tebrikler! Size {count} jeton hediye edildi!\n"
                     f"ðŸ’° Yeni bakiyeniz: {users[user_id]['tokens']} jeton\n\n"
                     f"Admin tarafÄ±ndan tÃ¼m kullanÄ±cÄ±lara daÄŸÄ±tÄ±ldÄ±! ðŸŽ‰"
            )
            success_count += 1
        except:
            pass  # Mesaj gÃ¶nderilemezse sessizce devam et
    
    save_users(users)
    await update.message.reply_text(
        f"âœ… TamamlandÄ±!\n"
        f"ðŸ‘¥ Toplam kullanÄ±cÄ±: {total_users}\n"
        f"ðŸ“¨ Bildirim gÃ¶nderilen: {success_count}\n"
        f"ðŸŽ Verilen jeton: {count} (kullanÄ±cÄ± baÅŸÄ±na)"
    )

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("âš ï¸ KullanÄ±m: /broadcast <mesajÄ±nÄ±z>")
        return
    
    # MesajÄ± birleÅŸtir
    message = " ".join(context.args)
    users = load_users()
    
    total_users = len(users)
    success_count = 0
    failed_count = 0
    
    await update.message.reply_text(f"ðŸ“¢ {total_users} kullanÄ±cÄ±ya bildirim gÃ¶nderiliyor...")
    
    # Her kullanÄ±cÄ±ya mesaj gÃ¶nder
    for user_id in users.keys():
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"ðŸ“¢ **Admin Bildirimi**\n\n{message}\n\nâ€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”\nðŸ¤– {BOT_USERNAME}",
                parse_mode="Markdown"
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
            # Hata detayÄ±nÄ± logla (opsiyonel)
            print(f"Mesaj gÃ¶nderilemedi {user_id}: {e}")
    
    # SonuÃ§ raporu
    await update.message.reply_text(
        f"âœ… Bildirim GÃ¶nderimi TamamlandÄ±!\n\n"
        f"ðŸ‘¥ Toplam kullanÄ±cÄ±: {total_users}\n"
        f"âœ… BaÅŸarÄ±lÄ±: {success_count}\n"
        f"âŒ BaÅŸarÄ±sÄ±z: {failed_count}\n\n"
        f"ðŸ“ GÃ¶nderilen mesaj:\n\"{message}\""
    )

# --- MAIN ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_callbacks, pattern="^(my_tokens|my_ref|get_number)$"))

    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(admin_callbacks, pattern="^(adm_)"))
    app.add_handler(CommandHandler("addtokens", add_tokens))
    app.add_handler(CommandHandler("removetokens", remove_tokens))
    app.add_handler(CommandHandler("giveall", give_all_tokens))
    app.add_handler(CommandHandler("broadcast", broadcast_message))
    
    # Stok komutları
    app.add_handler(CommandHandler("addstock", add_stock))
    app.add_handler(CommandHandler("clearstock", clear_stock))
    app.add_handler(CommandHandler("showstock", show_stock))
    
    # Ban komutları
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("banlist", ban_list))

    print("🚀 Bot başlatılıyor...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
