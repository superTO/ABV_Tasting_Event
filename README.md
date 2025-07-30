# ABV-Tasting-Event-Scraper

## 說明
每天爬取ABV品飲會活動資訊，如果活動還沒發生，發送LINE訊息通知。
並將記錄儲存在 notified_events.json，避免重複發送。

## 安裝虛擬環境套件

## 1. environment.yml 
conda env create -f environment.yml --prefix .venv

## 2. pyproject.toml
pip install -e .

- 如果你還需要安裝開發用的套件 (例如 pytest, black)
- 假設你在 pyproject.toml 中定義了 [project.optional-dependencies] 的 "dev"
pip install -e .[dev]

## 3. requirements.txt
pip install -r requirements.txt

## keepalive.yml

原因: Scheduled workflows are disabled automatically after 60 days of repository inactivity.
解決辦法: 固定每個月1號, 在 keepalive 分支建立空的 commit 並 push, 以此來規避60天程式碼沒有更新的問題.

## 使用 conda env export 匯出虛擬環境
```
conda env export > environment.yml
```