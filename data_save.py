
import os
import csv
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ✅ Setup Chrome in headless mode
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# ✅ Base URL
base_url = "https://www.adapt.io/directory/industry/financial-services"
letters = [chr(i) for i in range(ord("A"), ord("Z")+1)]

# ✅ CSV output path
output_path = r"C:\Users\HP\OneDrive\Սեղան\ACAsummer\adaptio-scraper\adaptio_companies.csv"

# ✅ Prepare CSV file
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Company Name", "Location", "Phone", "Website", "Employees", "Revenue",
        "Industry", "SIC Code", "NAICS Code", "Specialties", "Page URL"
    ])

    for letter in letters:
        page = 1
        while True:
            url = f"{base_url}/{letter}-{page}"
            print(f"🔍 Processing list page: {url}")
            try:
                driver.get(url)
                time.sleep(2)

                script = driver.find_element(By.ID, "__NEXT_DATA__")
                json_text = script.get_attribute("innerHTML")
                data = json.loads(json_text)
                props = data.get("props", {}).get("pageProps", {})
                seo_data = props.get("seoDirectoryData", {})
                companies = seo_data.get("seoListLinks", [])
                total_pages = seo_data.get("totalNumberOfPages", 1)

                if not companies:
                    break

                for comp in companies:
                    name = comp.get("name")
                    seo_url = comp.get("seoUrl")
                    company_url = f"https://www.adapt.io/company/{seo_url}"
                    print(f"➡️ Visiting company page: {company_url}")

                    try:
                        driver.get(company_url)
                        time.sleep(2)
                        script = driver.find_element(By.ID, "__NEXT_DATA__")
                        json_text = script.get_attribute("innerHTML")
                        nd = json.loads(json_text)
                        pprops = nd.get("props", {}).get("pageProps", {})
                        cdata = None
                        for key in ["companyData", "seoCompanyData", "companyInfo", "company"]:
                            if key in pprops:
                                cdata = pprops[key]
                                break

                        def get_field(field, fallback=None):
                            return cdata.get(field) if cdata and field in cdata else fallback

                        location = get_field("location") or get_field("headquarter")
                        phone = get_field("phone") or ""
                        website = get_field("website") or ""
                        employees = get_field("employeeRange") or get_field("employees") or ""
                        revenue = get_field("revenue") or get_field("revenueRange") or ""
                        industry = get_field("industry") or ""
                        sic = get_field("sic") or get_field("SIC") or ""
                        naics = get_field("naics") or ""
                        specialties = get_field("specialties") or get_field("tags") or ""
                        if isinstance(specialties, (list, tuple)):
                            specialties = ", ".join(specialties)

                        writer.writerow([
                            name, location, phone, website, employees, revenue,
                            industry, sic, naics, specialties, company_url
                        ])
                    except Exception as e:
                        print(f"⚠️ Failed to extract {company_url}: {e}")
                        continue

                if page >= total_pages:
                    break
                page += 1
                time.sleep(1)

            except Exception as e:
                print(f"❌ Error on {url}: {e}")
                break

driver.quit()
print(f"\n✅ Done. Detailed data saved to: {output_path}")
