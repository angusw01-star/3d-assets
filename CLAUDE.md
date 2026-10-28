# 3D 設計專案

給孩子的教育遊戲與教育訓練用的 3D 模型和網頁。完整背景見 `建議方案.txt`。

## 資料夾

| 路徑 | 用途 | 進 git |
|---|---|---|
| `models/raw/` | Meshy 下載的原始檔（GLB/FBX…），Meshy 的 `meshy_output/` 紀錄也在這裡 | 否 |
| `models/optimized/` | 壓縮後的 GLB，網頁透過 jsDelivr 載入這裡的檔案 | 是 |
| `sources/` | Blender `.blend` 等工作檔 | 否 |
| `pages/` | 網頁（model-viewer 展示、Three.js 互動） | 是 |
| `scripts/` | 工具腳本（模型壓縮） | 是 |

## 做法選擇

- **機械件、精確幾何**（油封、O-ring、油壓缸剖面、魯班鎖、地球、細胞分層）：用 Three.js 程式產生（`LatheGeometry`、`ExtrudeGeometry` 等），做成參數化，不要用 AI 生成。
- **角色、怪獸、飛機、動物、器官**：用 Meshy 生成。
- 常見物件先查 Sketchfab / Poly Pizza 有沒有免費模型；CC-BY 授權要在頁面標示作者。

## Meshy 生成流程

1. 用 `.claude/skills/meshy-3d-generation` skill。輸出位置一律指定 `models/raw/`，檔名用英文小寫加連字號（例如 `models/raw/sky-plane.glb`）。
2. 生成會花 credits，開始前先跟使用者確認 prompt 與預估花費。
3. 壓縮：`npm run optimize`（處理 `models/raw/` 裡所有 `.glb`，輸出到 `models/optimized/`）。平板上每個模型控制在 2–5 MB 以內。
4. commit 並 push 後，用 jsDelivr 載入（見下方）。

注意：使用者的 Meshy 目前是免費方案，CLI/API 建立任務會被拒（402，不扣點）。升級前不要送出生成任務。

MCP server（`.mcp.json` 的 `meshy`）是備用通道，需要 Pro 方案的 API key，從環境變數 `MESHY_API_KEY` 讀取。API key 不可寫進任何檔案。

## Blender

Blender 5.2 安裝在 `C:\Program Files\Blender Foundation\Blender 5.2\`。

**主力：背景腳本**（不開視窗，穩定、可批次）
- `npm run prep -- <輸入檔> [--faces 50000] [--out 輸出.glb]`：匯入 GLB/glTF/FBX/OBJ/STL，可減面，匯出 GLB 到 `models/raw/`（減面時檔名加 `-lite`）。接著再跑 `npm run optimize`。
- 平板用的模型建議 2 萬–5 萬個三角面。
- 程式產生的遊戲道具（例如 `scripts/blender/make_sword.py` 寶劍）：`blender -b --factory-startup --python scripts/blender/make_sword.py -- models/raw/treasure-sword.glb sources/treasure-sword.blend`，再 `npm run optimize`。卡通低面數（幾千面）、原點在模型中心。
- 其他處理（拆部件、改材質、算體積…）寫成 `scripts/blender/*.py`，用 `blender -b --factory-startup --python 腳本.py -- 參數` 執行。

**選配：Blender MCP**（使用者打開 Blender，Claude 即時操作）
- `.mcp.json` 的 `blender`（套件 `mcp-for-blender`，已關閉遙測），預設在 `.claude/settings.local.json` 的 `disabledMcpjsonServers` 停用。使用者要用時，把 `blender` 從該清單移除並重開對話；用完再加回去。
- Blender 的 addon「MCP for Blender」已安裝並啟用；Blender 開啟時會在 localhost 啟動連線，也可以按 N → MCP for Blender 分頁 → Start MCP Server。
- 這台電腦的網路會攔截 TLS，uv/uvx 一律加 `--system-certs`。

## jsDelivr 載入

```
https://cdn.jsdelivr.net/gh/<GitHub帳號>/<repo>@<版本>/models/optimized/<檔名>.glb
```

- `<版本>` 正式使用時用 tag（例如 `@v1.0.0`）或 commit hash，內容固定不會被快取影響；`@main` 會被快取最多 12 小時，只適合測試。
- 更新 `@main` 後要立即生效，可開 `https://purge.jsdelivr.net/gh/<帳號>/<repo>@main/<路徑>` 清快取。
- 單檔上限 20 MB，repo 必須是 public。
- GAS 網頁不要用 HtmlService 或 Google Drive 放模型檔，一律用 jsDelivr 網址。

## 網頁

- 純展示：`pages/viewer.html`（Google `<model-viewer>`），用 `?src=` 帶模型網址。
- 互動或遊戲：`pages/three-template.html`（Three.js + GLTFLoader + MeshoptDecoder，壓縮後的 GLB 需要 MeshoptDecoder 才能讀）。
- model-viewer 讀 meshopt 壓縮檔要先設定 `meshoptDecoderLocation`（`viewer.html` 已寫好）。
- 本機預覽：`.claude/launch.json` 的 `pages`（python http.server，port 8123），網址 `http://localhost:8123/pages/...`。
- CDN 版本號要寫死，不要用 `@latest`。

## 成語遊戲（`成語/`，GAS 專案，不進 git）

- 用全域的 three.js **r128**（非 module）。r128 讀 meshopt 壓縮＋量化的 GLB 會變形，給它用的模型要另做不壓縮版：
  `node node_modules/@gltf-transform/cli/bin/cli.js optimize models/raw/X.glb models/optimized/X-r128.glb --compress false --texture-compress false`
- 載入器：`Index.html` 加了 r128 的 GLTFLoader 與 meshopt_decoder；`Scene3D.html` 的 `loadGLB()`／`glbThumb()`／`view3DItem()` 共用快取。
- 商品加 `glb` 欄位就會：商店與寶物庫顯示 3D 小圖（點了開 360° 視窗），勇者手上換成該模型（`buildHero3D`）。
- 本機測試：把 include 合併成 `tmp-preview/game.html`（不進 git）再用 `pages` 伺服器開。
- 修改前的備份在 `成語_backup_20261028/`。
