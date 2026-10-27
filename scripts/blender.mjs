// 用 Blender 背景處理模型：轉成 GLB，並可減面。
// 用法：npm run prep -- <輸入檔> [--faces 50000] [--out 輸出.glb]
//   輸入可以是 .glb .gltf .fbx .obj .stl
//   沒給 --out 時：輸出到 models/raw/<檔名>.glb；有減面則為 <檔名>-lite.glb
// 找不到 Blender 時，可設定環境變數 BLENDER_PATH 指向 blender.exe
import { existsSync, readdirSync } from 'node:fs';
import { join, parse, resolve } from 'node:path';
import { execFileSync } from 'node:child_process';

function findBlender() {
  if (process.env.BLENDER_PATH) return process.env.BLENDER_PATH;
  const base = 'C:/Program Files/Blender Foundation';
  if (existsSync(base)) {
    const dirs = readdirSync(base).sort().reverse();
    for (const d of dirs) {
      const exe = join(base, d, 'blender.exe');
      if (existsSync(exe)) return exe;
    }
  }
  return 'blender';
}

const argv = process.argv.slice(2);
const opt = (name) => {
  const i = argv.indexOf(name);
  if (i === -1) return undefined;
  const v = argv[i + 1];
  argv.splice(i, 2);
  return v;
};
const faces = Number(opt('--faces') || 0);
let out = opt('--out');
const input = argv[0];
if (!input || !existsSync(input)) {
  console.error('用法：npm run prep -- <輸入檔> [--faces 50000] [--out 輸出.glb]');
  process.exit(1);
}
if (!out) out = join('models/raw', `${parse(input).name}${faces ? '-lite' : ''}.glb`);
if (resolve(out) === resolve(input)) {
  console.error('輸出不能覆蓋輸入檔，請用 --out 指定其他檔名');
  process.exit(1);
}

const output = execFileSync(findBlender(), [
  '-b', '--factory-startup', '--python', 'scripts/blender/prep.py', '--',
  resolve(input), resolve(out), String(faces),
], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'inherit'] });
const line = output.split('\n').find((l) => l.startsWith('PREP_RESULT'));
console.log(line ? line.replace('PREP_RESULT ', '') : output);
