import argparse
import json
import re
from pathlib import Path
from datetime import datetime, date
from playwright.sync_api import sync_playwright, Playwright
from line_message import broadcast_message_api, push_message_api

# 記錄已通知活動的檔案名稱
NOTIFIED_EVENTS_FILE = Path("notified_events.json")
# today = datetime.now().date()
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

def load_notified_events() -> set:
    """
    從 JSON 檔案載入已經通知過的活動標題。
    如果檔案不存在或內容不合法，回傳一個空的集合 (set)。
    """
    if not NOTIFIED_EVENTS_FILE.exists():
        return set()
    try:
        with open(NOTIFIED_EVENTS_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except (json.JSONDecodeError, FileNotFoundError):
        return set()

def save_notified_events(notified_set: set):
    """
    過濾舊活動後將更新後的活動標題集合寫回 JSON 檔案
    """
    # 建立一個只包含未來活動的乾淨列表
    future_events = [
        event_id for event_id in notified_set 
        if (event_date := parse_event_date(event_id)) and event_date >= today
    ]
    
    with open(NOTIFIED_EVENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(future_events), f, ensure_ascii=False, indent=2)

def run(playwright: Playwright) -> None:
    notified_events_set = load_notified_events()
    # print(f"已記錄 {len(notified_events_set)} 個活動。")

    browser = playwright.chromium.launch(headless=True)
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
                    if title_text.strip() not in notified_events_set:
                        # 將未來的品飲會加入
                        messages.append(f"{title_text.strip()}")
                        # 加入到記憶中，並標記本次有找到新活動
                        notified_events_set.add(f"{title_text.strip()}")
            

        else:
            print("在頁面上沒有找到 class 為 'post-title is-large' 的元素。")
    except Exception as e:
        print(f"抓取元素時發生錯誤: {e}")
    finally:
        # 結束時，若有發現新活動，則儲存更新後的「記憶」
        if len(messages) > 0:
            print("偵測到新活動，正在將更新後的記錄寫回檔案...")
            save_notified_events(notified_events_set)
            # print(f"更新完畢。現在共記錄了 {len(notified_events_set)} 個活動。")

            # 將所有訊息合併後發送
            final_message = "\n\n".join(messages)
            ## 只傳給一個人
            # push_message_api(args.token, args.user_id, final_message)
            ## 傳給所有好友
            broadcast_message_api(args.token, final_message)
        else:
            print("本次執行沒有發現新的未來活動。")
    

    # ---------------------
    context.close()
    browser.close()

if __name__ == "__main__":
    # 使用 argparse 解析命令列參數
    parser = argparse.ArgumentParser(description="LINE Bot Message Sender")
    parser.add_argument("--token", required=True, help="LINE Channel Access Token")
    # parser.add_argument("--user_id", required=True, help="LINE User ID")

    args = parser.parse_args()
    
    with sync_playwright() as playwright:
        run(playwright)