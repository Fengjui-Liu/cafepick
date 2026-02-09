# CaféPick 技術架構文件

> 版本 1.0 | 2025 年 2 月

## 技術棧

| 層級 | 技術 | 說明 |
|------|------|------|
| Frontend | React 19 + TypeScript + Vite | 現代化前端框架 |
| UI Framework | Tailwind CSS + shadcn/ui | 快速開發響應式介面 |
| 地圖 | Leaflet + react-leaflet | 互動式地圖呈現 |
| Backend | Python + FastAPI | API 整合與資料處理 |
| Database | SQLite (MVP) → PostgreSQL + PostGIS | MVP 輕量啟動，之後可遷移 |
| 部署 | Vercel (前端) + Railway/Render (後端) | 快速部署 |

## 資料來源策略

### MVP (Phase 1)：Cafe Nomad API → 匯入自建 DB

Cafe Nomad 提供免費、無需 API key 的咖啡廳資料，包含 CaféPick 核心篩選所需的欄位：

| Cafe Nomad 欄位 | 對應功能 |
|----------------|---------|
| `wifi` | WiFi 穩定度評分 |
| `socket` | 插座數量評分 |
| `quiet` | 安靜程度評分 |
| `limited_time` | 有無限時 |
| `seat` | 通常有位 |
| `cheap` | 價格評分 |
| `tasty` | 咖啡品質評分 |
| `music` | 裝潢音樂評分 |
| `latitude` / `longitude` | 地理座標 |
| `address` | 地址 |
| `mrt` | 最近捷運站 |
| `open_time` | 營業時間 |
| `url` | 官網連結 |
| `standing_desk` | 可站立工作 |

### Phase 2：Google Maps API 補充

- 即時營業時間（更準確）
- 店家照片
- Google 評分
- 整合使用者 Google Maps 收藏清單

## 專案結構

```
cafepick/
├── frontend/                  # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/        # UI 元件
│   │   ├── pages/             # 頁面
│   │   ├── hooks/             # 自訂 hooks
│   │   ├── services/          # API 呼叫
│   │   ├── types/             # TypeScript 型別定義
│   │   └── utils/             # 工具函式
│   ├── package.json
│   └── vite.config.ts
├── backend/                   # Python + FastAPI
│   ├── app/
│   │   ├── main.py            # FastAPI 進入點
│   │   ├── models/            # 資料模型 (SQLAlchemy)
│   │   ├── routes/            # API 路由
│   │   ├── services/          # 業務邏輯（推薦演算法等）
│   │   └── database.py        # 資料庫連線設定
│   ├── data/                  # SQLite DB 檔案、種子資料
│   ├── requirements.txt
│   └── README.md
├── ARCHITECTURE.md            # 本文件
└── CafePick_PRD.docx          # 產品規劃文件
```

## MVP 範圍 (Phase 1)

1. 單一城市（台北）咖啡廳資料
2. 區域選擇 + 基本條件篩選（插座、WiFi、安靜程度、不限時、價格）
3. Leaflet 地圖視覺化呈現
4. 推薦演算法 v1：根據條件匹配度排序，推薦 1-3 間最適合的

## API 設計 (RESTful)

```
GET  /api/cafes              # 取得咖啡廳列表（支援篩選參數）
GET  /api/cafes/:id          # 取得單一咖啡廳詳情
GET  /api/cafes/recommend    # 取得推薦結果（帶篩選條件）
GET  /api/areas              # 取得可選區域列表
```

## 開發順序

1. 後端：建立 FastAPI 專案 + SQLite + 資料模型
2. 資料：匯入 Cafe Nomad 資料至資料庫
3. 後端：實作 API 端點 + 推薦邏輯
4. 前端：安裝 Tailwind + shadcn/ui + react-leaflet
5. 前端：實作頁面（區域選擇 → 條件篩選 → 推薦結果 → 地圖）
6. 整合：前後端串接 + 測試
