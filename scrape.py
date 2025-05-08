from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import requests
import os
import random

# Fungsi untuk membuat ID acak
def generate_random_id():
    return random.randint(1000, 9999)

# Fungsi untuk memberi label berdasarkan rating
def label_based_on_rating(rating):
    try:
        rating_value = int(rating)
        if rating_value == 5:
            return "Positif"
        elif rating_value == 1:
            return "Negatif"
        else:
            return "Netral"
    except ValueError:
        return "Tidak diketahui"

# Input URL toko Tokopedia
url = input("Masukkan URL toko Tokopedia: ")

if url:
    # Setup WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    data = []
    os.makedirs("gambar_produk_reytorrm", exist_ok=True)

    for i in range(50):  # Maksimal 50 halaman
        soup = BeautifulSoup(driver.page_source, "html.parser")
        containers = soup.find_all('article', class_='css-1pr2lii')

        print(f"Memproses halaman {i+1} dengan {len(containers)} produk...")

        for idx, container in enumerate(containers):
            try:
                # Ambil ulasan
                review_tag = container.find('span', {'data-testid': 'lblItemUlasan'})
                review = review_tag.text.strip() if review_tag else "Tidak ada ulasan"

                # Ambil rating
                rating_tag = container.find('div', {'data-testid': 'icnStarRating'})
                if rating_tag and 'aria-label' in rating_tag.attrs:
                    rating_text = rating_tag['aria-label'].strip().lower()
                    rating = rating_text.replace('bintang', '').strip()
                else:
                    rating = 'Tidak diketahui'

                label = label_based_on_rating(rating)

                # Nama pengguna
                user_tag = container.find('span', class_='name')
                user = user_tag.text.strip() if user_tag else 'Tidak diketahui'

                # Nama produk
                product_tag = container.find('a', class_='styProduct')
                product = product_tag.text.strip() if product_tag else 'Tidak diketahui'

                # Gambar produk
                img_tag = container.find('img', class_='_0m9NsWypn6Yr4lxFi5dknA== styPrductImage')
                img_url = img_tag.get('src') or img_tag.get('data-src') if img_tag else ''
                img_filename = ''

                # Download gambar
                if img_url and img_url.startswith('https://'):
                    try:
                        img_response = requests.get(img_url, timeout=5, stream=True)
                        content_type = img_response.headers.get('Content-Type', '')
                        if any(x in content_type for x in ['image/jpeg', 'image/png', 'image/webp']):
                            ekstensi = '.jpg' if 'jpeg' in content_type else (
                                '.png' if 'png' in content_type else '.webp'
                            )

                            # Bersihkan nama produk untuk nama file
                            safe_product_name = ''.join(c if c.isalnum() or c in [' ', '_', '-'] else '' for c in product)
                            safe_product_name = safe_product_name.replace(' ', '_')[:100]

                            img_filename = f"gambar_produk_reytorrm/{safe_product_name}_{i}_{idx}{ekstensi}"
                            with open(img_filename, 'wb') as f:
                                for chunk in img_response.iter_content(1024):
                                    f.write(chunk)
                    except Exception as e:
                        print(f"[!] Gagal download gambar: {e}")
                        img_filename = ''
                else:
                    print(f"[!] Gambar produk ke-{idx} tidak memiliki URL yang valid.")

                # Simpan data
                random_id = generate_random_id()
                data.append((random_id, user, product, rating, label, review, img_filename))

            except Exception as e:
                print(f"[!] Error parsing produk ke-{idx} di halaman {i+1}: {e}")
                continue

        # Klik tombol "Laman berikutnya"
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label^='Laman berikutnya']")
            next_button.click()
            time.sleep(3)
        except:
            print("Tidak ada tombol 'Laman berikutnya', proses berhenti.")
            break

    driver.quit()

    # Simpan ke CSV
    save_path = r"E:\Kuliah\SEMESTER 6\METOPEN\ScrapingTokopedia-main"
    os.makedirs(save_path, exist_ok=True)

    file_path = os.path.join(save_path, "Dataset.csv")
    df = pd.DataFrame(data, columns=["ID", "Pengguna", "Produk", "Rating", "Label", "Ulasan", "File Gambar"])
    df.to_csv(file_path, index=False)
    print(f"✅ Data berhasil disimpan ke {file_path}")
