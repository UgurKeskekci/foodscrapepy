import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_page(query, page):
    if page == 1:
        url = f'https://www.fatsecret.com.tr/kaloriler-beslenme/search?q={query}'
    else:
        url = f'https://www.fatsecret.com.tr/kaloriler-beslenme/search?q={query}&pg={page-1}'
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f'Sayfa {page} yüklenemedi.')
        return []

    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.select('table.generic.searchResult tr')
    print(f'Sayfa {page} - Bulunan satır sayısı: {len(rows)}')

    foods = []

    for item in rows:
        name_element = item.select_one('a.prominent')
        brand_element = item.select_one('a.brand')
        details_element = item.select_one('div.smallText.greyText.greyLink')

        if name_element and details_element:
            name = name_element.get_text(strip=True)
            brand = brand_element.get_text(strip=True).strip('()') if brand_element else None
            details = details_element.get_text(strip=True)

            print(f'İşleniyor: {name} - {brand} - {details}')

            try:
                portion, nutrition = details.split(' - ', 1)
                nutrition_parts = nutrition.split('|')

                if len(nutrition_parts) == 4:
                    calories = re.search(r'Kaloriler: ([\d,]+)', nutrition_parts[0])
                    fat = re.search(r'Yağ: ([\d,]+)g', nutrition_parts[1])
                    carbs = re.search(r'Karb: ([\d,]+)g', nutrition_parts[2])
                    protein = re.search(r'Prot: ([\d,]+)g', nutrition_parts[3])

                    if all([calories, fat, carbs, protein]):
                        food_data = {
                            'name': name,
                            'brand': brand,
                            'portion': portion.replace('her ', '').strip(),
                            'nutrition': {
                                'calories': float(calories.group(1).replace(',', '.')),
                                'fat': float(fat.group(1).replace(',', '.')),
                                'carbs': float(carbs.group(1).replace(',', '.')),
                                'protein': float(protein.group(1).replace(',', '.'))
                            }
                        }
                        foods.append(food_data)
                    else:
                        print(f'Besin değerleri geçersiz: {nutrition_parts}')
                else:
                    print(f'Besin değerleri eksik veya hatalı: {nutrition_parts}')
            except ValueError as ve:
                print(f'Hatalı veri ayrıştırma: {details} - Hata: {ve}')
    return foods

def scrape_data(query, num_pages):
    try:
        all_foods = []
        for page in range(1, num_pages + 1):
            print(f'Sayfa {page} işleniyor...')
            foods = scrape_page(query, page)
            all_foods.extend(foods)

        print('Veriler işleniyor, JSON dosyasına kaydediliyor...')
        with open('food21s.json', 'w', encoding='utf-8') as f:
            json.dump(all_foods, f, ensure_ascii=False, indent=4)
        print('Veriler JSON dosyasına kaydedildi.')

    except Exception as e:
        print(f'Hata: {e}')

scrape_data('tavuk', 21)  # 'pirinç' araması için 3 sayfa veriyi çek
