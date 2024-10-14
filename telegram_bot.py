
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# إعداد تخزين المذكرات لكل مستخدم
user_memos = {}  # {user_id: [memo1, memo2, ...]}
scheduler = AsyncIOScheduler()
is_adding_memo = {}  # {user_id: True/False}
is_searching_memo = {}  # {user_id: True/False}
OWNER_ID = 1464889307  # معرف المالك

def main_menu():
    buttons = [
        [InlineKeyboardButton("📝 إضافة مذكرة", callback_data="add_memo")],
        [InlineKeyboardButton("📜 عرض المذكرات", callback_data="view_memos")],
        [InlineKeyboardButton("🗑️ مسح جميع المذكرات", callback_data="delete_all_memos")],
        [InlineKeyboardButton("🔍 بحث عن مذكرة", callback_data="search_memo")],
        [InlineKeyboardButton("↩️ رجوع", callback_data="back")]
    ]
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_adding_memo[user_id] = False
    is_searching_memo[user_id] = False
    user_memos.setdefault(user_id, [])  # تأكد من وجود قائمة للمستخدم
    await update.message.reply_text("مرحبًا بك في بوت المذكرات!", reply_markup=main_menu())

async def add_memo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_adding_memo[user_id] = True
    await update.callback_query.message.reply_text("اكتب المذكرة التي تريد إضافتها:")

async def handle_text_memo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_adding_memo.get(user_id, False):
        user_memos[user_id].append(update.message.text)
        is_adding_memo[user_id] = False
        await update.message.reply_text("تم حفظ المذكرة!", reply_markup=main_menu())
    elif is_searching_memo.get(user_id, False):
        await search_memo_by_number(update, context)
    else:
        await update.message.reply_text("الرجاء استخدام الأزرار المتاحة.")

async def view_memos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    memos = user_memos.get(user_id, [])
    if not memos:
        await update.callback_query.message.reply_text("لا توجد مذكرات متاحة.")
    else:
        memo_list = "\n".join([f"{i + 1}: {memo}" for i, memo in enumerate(memos)])
        await update.callback_query.message.reply_text(f"📜 مذكراتك:\n{memo_list}")

async def search_memo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_searching_memo[user_id] = True
    await update.callback_query.message.reply_text("اكتب رقم المذكرة للعثور عليها:")

async def search_memo_by_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    memos = user_memos.get(user_id, [])
    try:
        memo_index = int(update.message.text) - 1
        if 0 <= memo_index < len(memos):
            await update.message.reply_text(f"📜 المذكرة: {memos[memo_index]}")
        else:
            await update.message.reply_text("رقم المذكرة غير صحيح.")
    except ValueError:
        await update.message.reply_text("يرجى إدخال رقم صحيح.")
    finally:
        is_searching_memo[user_id] = False

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == OWNER_ID or user_id in user_memos:
        user_memos[user_id] = []  # مسح مذكرات المستخدم
        await update.callback_query.message.reply_text("تم مسح جميع المذكرات.", reply_markup=main_menu())
    else:
        await update.callback_query.message.reply_text("ليس لديك إذن لمسح هذه المذكرات.")

# إعداد البوت وإضافة المعالجات
app = ApplicationBuilder().token("7608219803:AAHCg-UXkIsx_XBUEgClxcWjhgkl1GMxnYw").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(add_memo, pattern="add_memo"))
app.add_handler(CallbackQueryHandler(view_memos, pattern="view_memos"))
app.add_handler(CallbackQueryHandler(search_memo, pattern="search_memo"))
app.add_handler(CallbackQueryHandler(confirm_delete, pattern="delete_all_memos"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_memo))

app.run_polling()
