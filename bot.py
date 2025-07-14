import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Load config
with open("config.json") as f:
    config = json.load(f)

ADMIN_ID = config["admin_id"]
UPI_ID = config["upi_id"]
SUPPORT_USERNAME = config["support_username"]

# Load IG stock
def load_ig_stock():
    with open("data/indo_ig_stock.json") as f:
        return json.load(f)

def save_ig_stock(data):
    with open("data/indo_ig_stock.json", "w") as f:
        json.dump(data, f, indent=4)

def save_utr_request(user, utr):
    with open("data/utr_requests.json") as f:
        data = json.load(f)
    data.append({"user": user, "utr": utr})
    with open("data/utr_requests.json", "w") as f:
        json.dump(data, f, indent=4)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 ADD FUNDS", callback_data='add_funds')],
        [InlineKeyboardButton("🇮🇳 INDO IG", callback_data='indo_ig')],
        [InlineKeyboardButton("📦 STOCK", callback_data='stock')],
        [InlineKeyboardButton("💬 CONTACT SUPPORT", callback_data='contact')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)

# Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'add_funds':
        context.user_data["awaiting_utr"] = True
        await query.edit_message_text(f"💰 Send ₹ to UPI: `{UPI_ID}`\nAfter payment, reply with your UTR/Txn ID.")
    
    elif query.data == 'indo_ig':
        keyboard = [
            [InlineKeyboardButton(f"{i} IG", callback_data=f"ig_{i}")]
            for i in range(1, 11)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🇮🇳 Choose IG pack:", reply_markup=reply_markup)
    
    elif query.data == 'stock':
        stock = load_ig_stock()
        stock_msg = "\n".join([f"{k}: {len(v)} available" for k, v in stock.items()])
        await query.edit_message_text(f"📦 Current Stock:\n{stock_msg}")
    
    elif query.data == 'contact':
        await query.edit_message_text(f"💬 Contact Support:\nTelegram: {SUPPORT_USERNAME}")
    
    elif query.data.startswith("ig_"):
        ig_key = f"{query.data.split('_')[1]} IG"
        stock = load_ig_stock()
        if stock.get(ig_key):
            creds = stock[ig_key].pop(0)
            save_ig_stock(stock)
            await query.edit_message_text(f"✅ Your IG Credentials:\nID: `{creds['id']}`\nPASS: `{creds['pass']}`")
        else:
            await query.edit_message_text("❌ Sorry, out of stock for this IG pack.")

# Handle UTR message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
