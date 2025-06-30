import aiohttp
import asyncio
import json


async def fetch_and_save_data():


    lang_list = ["az", "ru", "en"]
    cur_list = ["azn", "usd"]

    for i in range(len(lang_list)):
        for j in range(len(cur_list)):
            url = f"https://myaccount.travelesim.az/api/v2/country_bundles?all&lang={lang_list[i]}&currency={cur_list[j]}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Сохраняем в файл
                        with open(f"country_data_{lang_list[i]}_{cur_list[j]}.json", "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                            print("✅ Данные успешно обновлены!")
                    else:
                        print("❌ Ошибка запроса:", response.status)
            

# Для запуска вручную:
if __name__ == "__main__":
    asyncio.run(fetch_and_save_data())
