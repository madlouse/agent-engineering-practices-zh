# 0002 首页动效用 three.js WebGPURenderer + TSL

- 状态：已采纳（2026-11-04）
- 关联：动效原型 https://claude.ai/artifact/PGihowSLLCHsh3xDx14Dtd 、设计系统「动效」、PRD 决定记录

## 背景

首页要有一个有 AGI 感的主动效「叶与网」：几千个点在叶子和网之间变形。要求在 WebGPU 可用时用 GPU 计算，在旧设备上也能跑，不拖慢首屏。

## 选项

1. three.js r180 `WebGPURenderer` + TSL 节点材质：一份着色器，自动回退 WebGL2。
2. 手写 WebGPU（WGSL）加一份 WebGL2 版本：体积小，但要维护两套着色器。
3. 只用 WebGL2：兼容最好，放弃 WebGPU。

## 决定

选 1。原型已在 WebGPU（离屏渲染）和 WebGL2 两种后端上验证；用 `SpriteNodeMaterial` 实例化点，`mx_fractal_noise_float` 做有机漂移。

## 后果

- 约 260 KB gzip 的 three.js，首屏文字绘制完再加载。
- 共享 uniform 的材质不能单独销毁，场景切换时缓存。
- 还没做：Mac Safari 和中端手机的真机性能检查（每帧 ≤ 4 毫秒）。
