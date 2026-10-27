// 壓縮 models/raw/ 裡的 GLB，輸出到 models/optimized/。
// 用法：npm run optimize            處理全部
//       npm run optimize -- a.glb   只處理指定檔案（models/raw/ 下的檔名）
import { readdirSync, statSync, existsSync } from 'node:fs';
import { join, basename } from 'node:path';
import { execFileSync } from 'node:child_process';

const RAW = 'models/raw';
const OUT = 'models/optimized';
const MAX_MB = 5;
const CLI = 'node_modules/@gltf-transform/cli/bin/cli.js';

const files = process.argv.length > 2
  ? process.argv.slice(2).map((f) => basename(f))
  : readdirSync(RAW).filter((f) => f.toLowerCase().endsWith('.glb'));

if (files.length === 0) {
  console.log(`${RAW}/ 裡沒有 .glb 檔`);
  process.exit(0);
}

const mb = (p) => (statSync(p).size / 1024 / 1024).toFixed(2);

for (const f of files) {
  const src = join(RAW, f);
  const dst = join(OUT, f);
  if (!existsSync(src)) {
    console.error(`找不到 ${src}`);
    continue;
  }
  execFileSync(process.execPath, [
    CLI, 'optimize', src, dst,
    '--compress', 'meshopt',
    '--texture-compress', 'webp',
    '--texture-size', '1024',
  ], { stdio: 'inherit' });
  const size = mb(dst);
  const warn = size > MAX_MB ? `  ⚠ 超過 ${MAX_MB} MB，考慮減面或縮小貼圖` : '';
  console.log(`${f}: ${mb(src)} MB → ${size} MB${warn}`);
}
