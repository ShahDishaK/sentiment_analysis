from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import random
import re
import csv


# 🎭 Random User-Agent pool
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
]

# 🔧 Chrome Options Setup
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-infobars")
options.add_argument("--start-maximized")
options.add_argument(f"user-agent={random.choice(user_agents)}")

# 🕵️ Undetected Driver Launch
driver = uc.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# 📍 Step 1: Open Flipkart Search Page
url = "https://www.flipkart.com/search?q=tshirt+for+women"
driver.get(url)
time.sleep(random.uniform(3, 5))


csv_file = open("flipkart_reviews.csv", mode="w", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Brand Name", "T-shirt Name", "Review"])

# ❌ Close login popup if it appears
try:
    close_btn = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'✕')]"))
    )
    close_btn.click()
    print("✅ Closed login popup.")
except:
    print("ℹ️ No login popup found.")

# 🔗 Step 2: Collect product links
product_links = []
products = driver.find_elements(By.CLASS_NAME, "rPDeLR")
for product in products:
    href = product.get_attribute("href")
    if href and href not in product_links:
        product_links.append(href)

print(f"🛍 Collected {len(product_links)} product links from first page.")

# 🔎 Step 3: Visit each product and get reviews
for i, link in enumerate(product_links[:]):  # Limit to 3 products for demo
    print(f"\n🔗 Visiting Product {i+1}: {link}")
    driver.get(link)
    time.sleep(random.uniform(2, 4))
    brand = driver.find_elements(By.CLASS_NAME, "mEh187")
    print("brand name:",brand)
    tshirtname = driver.find_elements(By.CLASS_NAME, "VU-ZEz")
    print("t shirt name:",tshirtname)



    try:
        view_all = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'All') and contains(text(), 'reviews')]"))
        )
        current_url = driver.current_url
        driver.execute_script("arguments[0].click();", view_all)
        WebDriverWait(driver, 5).until(EC.url_changes(current_url))
        print("👉 Navigated to full reviews page.")
        time.sleep(random.uniform(2, 4))
    except Exception as e:
        print("❌ 'All reviews' span not found")
        print("Error:", str(e))


    try:
        page_container = driver.find_element(By.CLASS_NAME, "_1G0WLw")
        spans = page_container.find_elements(By.TAG_NAME, "span")
        page_numbers = [int(span.text) for span in spans if span.text.isdigit()]
        if page_numbers:
            page = max(page_numbers)
        else:
            # fallback using regex to match "1 of 53"
            text = page_container.text
            match = re.search(r'of\s+(\d+)', text)
            page = int(match.group(1)) if match else 1
        print(f"📄 Total review pages: {page}")
    except Exception as e:
        print("❌ Could not extract page numbers.")
        print("Error:", str(e))
        page = 1


    all_reviews = []

    # Build review URL
    split_link = link.split("/")
    brand_name=split_link[3].split("-")[0]
    tshirtname=" ".join(split_link[3].split("-")[2:])
    print("brand name:",brand_name)
    print("t-shirt name:",tshirtname)
    for j in range(page):
        review_divs = driver.find_elements(By.CLASS_NAME, "_11pzQk")
        print(f"🗣 Found {len(review_divs)} reviews on page {j+1}:")
        for review in review_divs:
            text = review.text.strip()
            print("brand name:",brand_name)
            print("t-shirt name:",tshirtname)
            print("-", text)
            csv_writer.writerow([brand_name, tshirtname, text])
            all_reviews.append(text)

        time.sleep(random.uniform(3, 5))

        if j < page - 1:
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
                )
                driver.execute_script("arguments[0].click();", next_button)
                print("➡️ Clicked 'Next' button.")
                time.sleep(2)
            except Exception as e:
                print("❌ Failed to click 'Next'.")
                print("Error:", str(e))
                break

# ✅ Done
driver.quit()
