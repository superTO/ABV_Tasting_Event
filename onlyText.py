import re
from datetime import datetime, date
from playwright.sync_api import sync_playwright, Playwright

today = datetime.now().date()
today = date(2025, 7, 19)

def parse_event_date(text_with_date: str) -> date | None:
    """
    從一段完整的文字中搜尋並解析日期。
    - 如果沒有年份，預設為今年。
    - 只有在特殊情況下(例如當前為12月,活動為1月), 才會認定為明年的活動。
    """
    
    # 主要模式: 搜尋 "M月D日" 格式
    match = re.search(r'(\d{1,2})月(\d{1,2})日', text_with_date)
    if not match:
        return None

    try:
        month, day = map(int, match.groups())
        event_date = date(today.year, month, day)

        # 只有當「現在」是年末（例如11月或12月），
        # 且「活動」是年初（例如1月或2月）時，
        # 我們才合理地假設它是明年的活動。
        if today.month >= 11 and event_date.month <= 2:
            event_date = event_date.replace(year=today.year + 1)
        
        return event_date

    except (ValueError, TypeError):
        return None

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.abv.com.tw/category/%E5%93%81%E9%A3%B2%E6%9C%83/")
    locators = page.locator('.post-title.is-large')

    try:
        count = locators.count()
        if count > 0:
            messages = []
            # print(f"找到了 {count} 個符合條件的標題：")
            for i in range(count):
                title_text = locators.nth(i).inner_text()
                # print(f"{title_text.strip()}")
                event_date  = parse_event_date(title_text.strip())
                # print(event_date)
                if event_date and event_date > today:
                    # 檢查未來的品飲會是否已發送過
                    messages.append(f"{title_text.strip()}")
                    print(f"{title_text.strip()}")
            

        else:
            print("在頁面上沒有找到 class 為 'post-title is-large' 的元素。")
    except Exception as e:
        print(f"抓取元素時發生錯誤: {e}")
    finally:
        if len(messages) == 0:
            print("本次執行沒有發現新的未來活動。")
    

    # ---------------------
    context.close()
    browser.close()


if __name__ == "__main__":
    
    with sync_playwright() as playwright:
        run(playwright)