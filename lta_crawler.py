
from utils import *
import json
# import pdb

async def run(year=None, month=None): 

    year = str(year); month = str(month)
    results = []

    async with async_playwright() as pw: 
        executable_path = r"C:\Users\ginee.leow\AppData\Local\ms-playwright\chromium-1200\chrome-win64\chrome.exe" # laptop
        browser = await pw.chromium.launch(
            executable_path=executable_path, 
            headless=False, timeout=3000
        )
        
        context = await browser.new_context(
            viewport = { 
                "width": 1920, "height": 1080 
            }, 
            user_agent=draw_one_userAgent(), 
        )
        page = await context.new_page()

        url = f"https://onemotoring.lta.gov.sg/content/onemotoring/home/buying/upfront-vehicle-costs/open-market-value--omv-.html"
        await page.goto(url)

        # navigate year > month
        await page.get_by_role("link", name=year, exact=True).click()
        await page.get_by_role("link", name=month, exact=True).click()

        # now get all make in specified year-month
        MAKES = await page.eval_on_selector_all(
            "#omv_make a",
            "elements => elements.map(e => e.textContent.trim())"
        )

        for MAKE in MAKES: 

            asyncio.sleep(10)

            await page.goto(url)

            # navigate year > month > make
            await page.get_by_role("link", name=year, exact=True).click()
            await page.get_by_role("link", name=month, exact=True).click()
            await page.get_by_role("link", name=MAKE, exact=True).click()

            # now get all models for given make
            await page.wait_for_selector("#omv_model")

            models = await page.eval_on_selector_all(
                "#omv_model li a",
                "elements => elements.map(e => e.textContent.trim())"
            )

            # for each model, get avg omv
            for model in set(models): 
                # there exist duplicate listings within a make, hence .first() to consider only first occurence of such duplicate listings
                try: await page.get_by_role("link", name=model).click()
                except: await page.get_by_role("link", name=model).first.click()
                await page.wait_for_selector(".omvAmount")
                AVG_OMV = await page.text_content(".omvAmount")
                AVG_OMV = AVG_OMV.strip().replace("S$","").replace(",","") # leave as string, but remove unnecessary string

                print(year, month, MAKE, model, AVG_OMV)

                results.append({
                    "year": year, 
                    "month": month, 
                    "make": MAKE, 
                    "model": model, 
                    "avg_omv": AVG_OMV
                })

        await context.close()
        await browser.close()
        
    # return listings
    with open(f"../data/{year}-{month}.json", "w") as f: 
        json.dump( {"listings": results}, f )


if __name__ == "__main__": 

    # YEARS = range(2002,2026)
    YEARS = range(2022,2026)
    MONTHS = range(1,13)

    for YEAR in YEARS: 
        for MONTH in MONTHS: 
            if ( YEAR == 2022 ) and ( MONTH == 1 ): continue
            try: 
                results = asyncio.run( run(year=YEAR, month=MONTH) )
            except: 
                print("error")
                continue

