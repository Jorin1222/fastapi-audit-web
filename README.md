
# FastAPI Audit Certification Web App

這是一套基於 FastAPI 開發的稽核認證計算 Web 應用，支援廢車處理月報 HTML 上傳、自動解析、稽核認證量與補貼費計算、緩發條件偵測、公司名稱顯示與報表下載等功能。

## 🔧 功能特色

- 上傳多個 HTML 月報
- 自動計算稽核認證量與補貼費
- 偵測緩發條件（ASR、廢塑膠等）
- 顯示再生料明細與比率
- 黑暗模式 + 主題切換
- 一鍵匯出 Excel、CSV、JSON（選配）
- 公司名稱自動擷取

---

## 🚀 快速部署到 Render

### 1. 登入 Render
前往 [https://render.com](https://render.com) 並登入 GitHub 帳號

### 2. 建立 Web Service
- 點選 `New` → `Web Service`
- 選擇本 Repo
- 確認啟用 `render.yaml` 設定部署參數

### 3. 完成部署
Render 會自動建置並啟動服務  
完成後會提供一組網址，例如：

```
https://fastapi-audit-app.onrender.com
```

---

## 🧾 使用方式

### 安裝套件（如需本機測試）

```bash
pip install -r requirements.txt
```

### 啟動本機伺服器

```bash
uvicorn main:app --reload
```

然後開啟：`http://127.0.0.1:8000`

---

## 📁 專案結構

```
.
├── main.py
├── utils.py
├── requirements.txt
├── render.yaml
└── templates/
    └── index.html
```

---

## 👤 作者
由 [你自己] 製作，可自由擴充與客製化！
