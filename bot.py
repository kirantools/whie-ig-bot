from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import json
import asyncio

ADMIN_ID = 6691650560
BOT_TOKEN = "8097664827:AAFMBlfi-jyRsIghAbFGVXQ_JOpn2Zyln8E"

# Load IG accounts from local JSON
def load_ig_accounts():
    with open("ig_accounts.json", "r") as f:
        return json.load(f)

# Save UTR request to JSON
def save_utr_request(user, utr):
    with open("utr_requests.json", "a") as f:
        f.write(json.dumps({"user": user, "utr": utr}) + "\n")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1️⃣ ADD FUNDS", callback_data="add_funds")],
        [InlineKeyboardButton("🇮🇩 INDO IG", callback_data="indo_ig")],
        [InlineKeyboardButton("📦 STOCK", callback_data="stock")],
        [InlineKeyboardButton("🛠 CONTACT SUPPORT", callback_data="contact_support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Please choose an option:", reply_markup=reply_markup)

# Handle button press
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add_funds":
        context.user_data["awaiting_utr"] = True
        await query.edit_message_text("💰 Send ₹ to UPI: `whiteigcc@slice`\nThen reply here with the UTR number.")
    elif query.data == "indo_ig":
        keyboard = [[InlineKeyboardButton(f"{i} IG", callback_data=f"buy_{i}")] for i in range(1, 11)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select how many IG IDs you want:", reply_markup=reply_markup)
    elif query.data == "stock":
        ig_accounts = load_ig_accounts()
        await query.edit_message_text(f"✅ Stock Available: {len(ig_accounts)} IG IDs")
    elif query.data == "contact_support":
        await query.edit_message_text("📩 Contact: @shirohackss")
    elif query.data.startswith("buy_"):
        count = int(query.data.split("_")[1])
        ig_accounts = load_ig_accounts()

        if len(ig_accounts) < count:
            await query.edit_message_text("❌ Not enough IG IDs in stock.")
            return

        # Get & remove selected accounts
        selected = ig_accounts[:count]
        remaining = ig_accounts[count:]

        # Save updated stock
        with open("ig_accounts.json", "w") as f:
            json.dump(remaining, f, indent=2)

        message = "\n".join([f"🆔 {acc['id']}\n🔑 {acc['pass']}" for acc in selected])
        await query.edit_message_text(f"✅ Here are your {count} IG IDs:\n\n{message}")

# Handle UTR replies
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_utr"):
        utr = update.message.text.strip()
        save_utr_request(update.effective_user.username or update.effective_user.id, utr)
        await update.message.reply_text("✅ UTR submitted. Please wait for admin verification.")
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📥 New UTR from @{update.effective_user.username or update.effective_user.id}:\n{utr}"
        )
        context.user_data["awaiting_utr"] = False

# Main runner
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
