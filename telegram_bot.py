import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
import aiohttp
import json
from tarifs import fetch_and_save_data


##TODO: Function to check if the phone supports eSIM
##TODO: Buy server and connect bot to the server

API_TOKEN = '7638142338:AAFl2w7mtLn2kRZ7Q-wizj5eQPEJmBYucXs'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
user_languages = {}
user_currencies = {}

from aiogram.types import BotCommand

@dp.startup()
async def on_startup(bot: Bot):
    commands = [
        BotCommand(command="start", description="🔁 start/restart")
    ]
    await bot.set_my_commands(commands)


#extracting data
def get_local_country_data(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = user_languages[user_id]
    cur = user_currencies[user_id]
    lang = lang.split("_")[1]
    with open(f"country_data_{lang}_{cur}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("bundles", [])

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    print(f"[LOG] User {user_id} started the bot")
    buttons_lang = [
        [
            InlineKeyboardButton(text="🇦🇿 Azərbaycan", callback_data="lang_az"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons_lang)
    await message.answer("🌐 Выберите язык | Dil seçin | Choose language:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("lang_"))
async def handle_language_choice(callback: types.CallbackQuery):
    lang = callback.data  # lang_ru, lang_az, lang_en
    user_id = callback.from_user.id
    user_languages[user_id] = lang

    await callback.answer()
    await callback.message.edit_text(f"✔")

    # Теперь предложим выбрать валюту
    buttons_cur = [
        [
            InlineKeyboardButton(text="🇦🇿 AZN", callback_data="cur_azn"),
            InlineKeyboardButton(text="🇺🇸 USD", callback_data="cur_usd")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons_cur)
    await bot.send_message(user_id, "💱 Выберите валюту | Məzənnə seçin | Choose currency:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("cur_"))
async def handle_currency_choice(callback: types.CallbackQuery):
    currency = callback.data.split("_")[1]
    user_id = callback.from_user.id
    user_currencies[user_id] = currency

    lang = user_languages.get(user_id, "lang_ru")

    if lang == "lang_ru":
        
        info_text = (
            "👋 Привет! Я TravelESIM-бот.\n\n"
            "Я помогу вам узнать:\n"
            "• что такое eSIM\n"
            "• как подключить eSIM\n"
            "• где купить eSIM и тарифы"
        )
    elif lang == "lang_az":
        
        info_text = (
            "👋 Salam! Mən TravelESIM botuyam.\n\n"
            "Mən sizə kömək edəcəyəm:\n"
            "• eSIM nədir\n"
            "• eSIM necə qoşulur\n"
            "• eSIM haradan almaq olar və tariflər"
        )
    else:
        
        info_text = (
            "👋 Hi! I am TravelESIM bot.\n\n"
            "I will help you:\n"
            "• What is eSIM\n"
            "• How to activate eSIM\n"
            "• Where to buy eSIM and plans"
        )

    await callback.answer()
    await callback.message.edit_text(f"✔")
    await bot.send_message(user_id, info_text)

    await show_main_menu(user_id)

async def show_main_menu(chat_id: int):

    lang = user_languages.get(chat_id, "lang_ru")

    if lang == "lang_ru":
        mess = "👇 Выберите раздел"
        menu_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="ℹ️ Информация", callback_data="info"),
                 InlineKeyboardButton(text="🌍 Покрытие и тарифы", callback_data="coverage")],
                [InlineKeyboardButton(text="📲 Как подключить", callback_data="howto"),
                 InlineKeyboardButton(text="🛒 Купить eSIM", url="https://travelesim.az/ru/")],
                [InlineKeyboardButton(text="💬 Поддержка", callback_data="support"),
                 InlineKeyboardButton(text="🔄 Сменить язык", callback_data="change_lang")]
            ]
        )
    elif lang == "lang_az":
        mess = "👇 Seçim et"
        menu_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="ℹ️ İnformasiya", callback_data="info"),
                 InlineKeyboardButton(text="🌍 Əhatə və tariflər", callback_data="coverage")],
                [InlineKeyboardButton(text="📲 Necə qoşulmalı", callback_data="howto"),
                 InlineKeyboardButton(text="🛒 eSim almaq", url="https://travelesim.az/az/")],
                [InlineKeyboardButton(text="💬 Dəstək", callback_data="support"),
                 InlineKeyboardButton(text="🔄 Dili dəyiş", callback_data="change_lang")]
            ]
        )
    else:  # "lang_en"
        mess = "👇 Choose an option"
        menu_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="ℹ️ Information", callback_data="info"),
                 InlineKeyboardButton(text="🌍 Coverage and plans", callback_data="coverage")],
                [InlineKeyboardButton(text="📲 How to use", callback_data="howto"),
                 InlineKeyboardButton(text="🛒 Buy eSim", url="https://travelesim.az/en/")],
                [InlineKeyboardButton(text="💬 Support", callback_data="support"),
                 InlineKeyboardButton(text="🔄 Change language", callback_data="change_lang")]
            ]
        )


    await bot.send_message(chat_id, mess, reply_markup=menu_kb)



@dp.callback_query(F.data == "info")
async def handle_info(callback: types.CallbackQuery):
    
    await callback.answer()  # Подтверждаем callback

    chat_id = callback.from_user.id
    lang = user_languages.get(chat_id, "lang_ru")

    if lang == "lang_ru":
        text = (
    "ℹ️ TravelESIM — твой идеальный спутник в путешествиях. \n"
    "Забудь о дорогом роуминге и поиске Wi-Fi! \n\n"
    
    "С помощью бота ты можешь:\n"
    "🌍 Выбрать страну\n"
    "💳 Купить удобный тариф\n"
    "📲 Мгновенно получить eSIM\n\n"
    
    "Путешествуй свободно — связь всегда с тобой."
)

        keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
        ]
    )
        await callback.message.edit_text(text, reply_markup=keyboard)
        
    elif lang == "lang_az":
        text = (
        "ℹ️ TravelESIM — sənin səyahətdə ideal yoldaşındır. \n"
         "Bahalı rouminqi və Wi-Fi axtarışını unut! \n\n"
         
         "Bot vasitəsilə sən:\n"
         "🌍 Ölkə seçə bilərsən\n"
         "💳 Rahat tarif ala bilərsən\n"
         "📲 eSIM-i dərhal əldə edə bilərsən\n\n"

         "Sərbəst səyahət et — əlaqə həmişə səninlədir."

    )
        keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Geriyə", callback_data="back_to_menu")]
        ]
    )   
        await callback.message.edit_text(text, reply_markup=keyboard)
    
    elif lang == "lang_en":
        text = (
    "ℹ️ TravelESIM — your perfect travel companion. \n"
    "Forget expensive roaming and searching for Wi-Fi! \n\n"
    
    "With the bot, you can:\n"
    "🌍 Choose a country\n"
    "💳 Buy a convenient plan\n"
    "📲 Instantly receive your eSIM\n\n"
    
    "Travel freely — stay connected wherever you go."
)

        keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")]
        ]
    )
        await callback.message.edit_text(text, reply_markup=keyboard)


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.answer()
    await show_main_menu(callback.from_user.id)


@dp.callback_query(F.data == "support")
async def support(callback: types.CallbackQuery):
    await callback.answer()
    
    chat_id = callback.from_user.id
    lang = user_languages.get(chat_id, "lang_ru")

    if lang == "lang_en":
        info_text = (
            "👇 Please, contact with our support team via email: \n\n"
            "support@travelesim.az"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")]
            ]
        )
    elif lang == "lang_ru":
        info_text = (
            "👇 Пожалуйста, свяжитесь с нашей командой поддержки через электронную почту: \n\n"
            "support@travelesim.az"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
            ]
        )
    elif lang == "lang_az":
        info_text = (
            "👇 Zəhmət olmasa dəstək komandası ilə elektron poçt vasitəsi ilə əlaqə saxlayın: \n\n"
            "support@travelesim.az"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Geriyə", callback_data="back_to_menu")]
            ]
        )
    
    await bot.send_message(chat_id, info_text, reply_markup=keyboard)


@dp.callback_query(F.data == "howto")
async def how_to_activate(callback: types.CallbackQuery):
    await callback.answer()

    chat_id = callback.from_user.id
    lang = user_languages.get(chat_id)

    if lang == "lang_az":
        info_text = ("1️⃣ Al \n\n"
        "eSIM planı seçin, platformada qeydiyyatdan keçin və alışınızı tamamlayın.\n\n"
        "2️⃣ Quraşdırın və Aktivləşdirin \n\n"
        "eSIM quraşdırmaq üçün QR kodunu skan edin və ya linkə keçid edin. İlk data istifadəsi ilə xəttiniz aktivləşdiriləcək.\n\n"
        "3️⃣ İdarə et \n\n"
        "Xətt təfərrüatlarına baxın və şəxsi hesabınızdan eSIM-ə nəzarət edin.\n\n"
        "4️⃣ Yenidən doldurun \n\n"
        "Əlavə bağlantıya ehtiyacınız olduqda eSIM-i yeni data planı ilə doldurun.")
        mess = "Geriyə"
        dir = "az"
        act = "eSim al"

    elif lang == "lang_ru":
        info_text = ("1️⃣ Купите \n\n"
        "Выберите eSIM-план, зарегистрируйтесь на платформе и завершите покупку.\n\n"
        "2️⃣ Установите и активируйте \n\n"
        "Отсканируйте QR-код для установки eSIM либо перейдите по ссылке. Ваша линия будет активирована при первом использовании интернета.\n\n"
        "3️⃣ Управляйте \n\n"
        "Просматривайте детали линии и контролируйте eSIM через ваш личный кабинет.\n\n"
        "4️⃣ Пополните \n\n"
        "При необходимости дополнительного подключения пополните eSIM новым тарифным планом.")
        mess = "Назад"
        dir = "ru"
        act = "Купить eSim"

        
    elif lang == "lang_en":
        info_text = ("1️⃣ Buy \n\n"
        "Choose an eSIM plan, register on the platform and complete your purchase.\n\n"
        "2️⃣ Install and Activate \n\n"
        "Scan the QR code to set up your eSIM or follow the link. Your line will be activated with the first data usage.\n\n"
        "3️⃣ Manage \n\n"
        "View line details and manage your eSIM from your personal account.\n\n"
        "4️⃣ Refill \n\n"
        "If you need additional connectivity, top up your eSIM with a new data plan.")
        mess = "Back"
        dir = "en"
        act = "Buy eSim"


    keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 "+mess, callback_data="back_to_menu"),
                 InlineKeyboardButton(text="🛒 "+ act, url=f"https://travelesim.az/{dir}/")]
            ]
        )

    await bot.send_message(chat_id, info_text, reply_markup=keyboard)



@dp.callback_query(F.data == "coverage")
async def select_country(callback: types.CallbackQuery):
    await callback.answer()
    mess = "👇"
    menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🇦🇿 Azerbaijan", callback_data="country_34")],
        [InlineKeyboardButton(text="🇹🇷 Turkiye", callback_data="country_29")],
        [InlineKeyboardButton(text="🇭🇺 Hungary", callback_data="country_131")],
        [InlineKeyboardButton(text="🇷🇺 Russia", callback_data="country_295")],
        [InlineKeyboardButton(text="🇬🇪 Georgia", callback_data="country_198")],
        [InlineKeyboardButton(text="🇩🇪 Germany", callback_data="country_25")],
        [InlineKeyboardButton(text="🇦🇪 UAE", callback_data="country_166")],
        [InlineKeyboardButton(text="🇶🇦 Qatar", callback_data="country_211")],
        [InlineKeyboardButton(text="🇨🇿 Czech", callback_data="country_125")],
        [InlineKeyboardButton(text="🇬🇧 UK", callback_data="country_146")],
        [InlineKeyboardButton(text="🇸🇦 S.Arabia", callback_data="country_278")],
        [InlineKeyboardButton(text="🇮🇹 Italy", callback_data="country_180")],
        [InlineKeyboardButton(text="🇫🇷 France", callback_data="country_183")],  
        [InlineKeyboardButton(text="🇰🇿 Kazakhstan", callback_data="country_80")],
        [InlineKeyboardButton(text="🇺🇿 Uzbekistan", callback_data="country_169")],
        [InlineKeyboardButton(text="🇨🇳 China", callback_data="country_334")],
        [InlineKeyboardButton(text="🇪🇬 Egypt", callback_data="country_151")],
        [InlineKeyboardButton(text="🇲🇪 Montenegro", callback_data="country_174")],
        [InlineKeyboardButton(text="🇵🇰 Pakistan", callback_data="country_207")],
        [InlineKeyboardButton(text="🇮🇳 India", callback_data="country_228")],
        [InlineKeyboardButton(text="🇰🇬 Kyrgyzstan", callback_data="country_264")],
        [InlineKeyboardButton(text="🇺🇦 Ukraine", callback_data="country_214")]
    ]
)

    await bot.send_message(callback.from_user.id, mess, reply_markup=menu_kb)




@dp.callback_query(F.data.startswith("country_"))
async def process_coverage(callback: types.CallbackQuery):
    await callback.answer()
    country_id = callback.data.split("_")[1]  # Получаем id страны
    tariffs = await get_tariff_text_by_id(country_id, callback)  
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")]
        ]
    )
    await callback.message.delete()
    await bot.send_message(callback.from_user.id, tariffs, reply_markup=keyboard)

    



@dp.callback_query(F.data == "change_lang")
async def change_lang(callback: types.CallbackQuery):
    await callback.answer()
    await start_handler(callback.message)


async def get_tariff_text_by_id(country_id, callback):
    bundles = get_local_country_data(callback)
    country = next((b for b in bundles if b["id"] == str(country_id)), None)
    if not country:
        return "Страна с таким ID не найдена."

    user_id = callback.from_user.id
    cur = user_currencies[user_id]
    lang = user_languages[user_id]

    if lang == "lang_en":
        mess1 = "Сountry"
        mess2 = "Link"
        mess3 = "Tariffs"
    elif lang == "lang_ru":
        mess1 = "Страна"
        mess2 = "Ссылка"
        mess3 = "Тарифы"
    else:
        mess1 = "Ölkə"
        mess2 = "Link"
        mess3 = "Tariflər"


    title = country.get("title")
    link = country.get("link")
    text = f"🌍 {mess1}: {title}\n🔗 {mess2}: {link}\n\n📦 {mess3}:\n"
    for refill in country.get("refills", []):
        plan_title = refill.get("title")
        price = refill.get("price")
        text += f"• {plan_title}: {price} {str.upper(cur)} \n"
    return text



async def main():
    print("Бот запущен!")
    #await fetch_and_save_data()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
