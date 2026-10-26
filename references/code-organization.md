# 产物代码组织格式（硬约定）

这是本 skill 产出的单文件原型**必须遵循**的组织方式。目标：在**不改变渲染**的前提下，
让后续 AI 能"grep 一下就定位到区块、改一处就生效、改完很稳"。

## 总体骨架

```
<!DOCTYPE html> <html lang=...>
<!-- ============ PROTOTYPE MAP（结构地图 + 修改约定）============ -->
<head>
  <meta charset> <meta viewport>        ← 影响渲染的元数据保留
  <title>...</title>
  <!-- SECTION: 资源图片库 base64（勿手改）-->
  <style>:root{--sf-img-...:url("data:...")}</style>   ← base64 资源库，整块保留
  <style>...</style>  <style>...</style>  ← 其余样式块，字节不动
</head>
<body ...>
  <!-- SECTION: 应用根容器 -->
  <!-- SECTION: 左侧导航栏 -->
  <!-- SECTION: 顶栏账号区 -->
  <!-- SECTION: 主内容区 -->
  <!-- SECTION: 模态/弹窗（静态保留）-->
  <!-- SECTION: 智能助手侧边面板 -->
  ...原快照 DOM，仅做定点替换，不重排...
  <!-- SECTION: 外链跳转提示浮层 / prototype redirect overlay -->
  <style id=proto-redirect-style>...</style>
  <div class=proto-redirect-mask id=protoRedirectMask>...</div>
  <!-- 唯一脚本：拦截 data-proto-href 外链点击并弹出提示 -->
  <script>...</script>
</body></html>
```

## 五条约定

1. **单一 HTML，CSS 不拆分。** 所有样式、脚本、媒体继续内联，保持"下载即用、单文件可发"。

2. **顶部 PROTOTYPE MAP 注释。** 紧跟 `<html ...>` 后放一段注释，内容包含：
   - 一句话说明"这是静态原型、无可运行业务 JS（唯一脚本是文末外链拦截器）"；
   - 各 `SECTION:` 关键字 → 对应锚点的跳转索引；
   - 修改约定（外链写法、不要重排压缩行等）。
   让任何接手的 AI 读第一屏就知道全局。

3. **SECTION 地标注释。** 在每个关键区块前插入
   `<!-- ========== SECTION: 中文名 / english ========== -->`。
   - 统一用 `SECTION:` 前缀，方便 `grep SECTION: file.html` 一览目录。
   - **插入规则（保证视觉不变）**：
     - 在**已逐行展开**的区域，可整行插入（前后换行）；多余空白会与既有空白折叠，无影响。
     - 在**压缩成单行**的区域，注释必须**紧贴标签、不加任何空白**：
       `...></div><!-- SECTION: xxx --><div ...`（HTML 注释不产生文本节点，零风险）。

4. **base64 资源库单独标注。** 那一大段 `:root{--sf-img-...}` / data-uri 资源用
   `SECTION: 资源图片库 base64（勿手改）` 包起来，明确告诉后续 AI：这里是二进制资源，
   不要尝试阅读或格式化。

5. **外链统一改写 + 唯一脚本。**
   - 每个外链 `<a>` 改成 `href="javascript:void(0)" data-proto-href="原始地址"`，
     原地址原样保留（含已转义的 `&amp;` 等）。
   - 文末放**唯一一段** `<script>`：全局捕获点击，命中 `a[data-proto-href]` 时
     `preventDefault` 并弹出浮层，显示"原本要去的地址 + 这是原型不支持外跳"。
   - 配套一个 `#protoRedirectMask` 浮层（默认 `display:none`，`position:fixed`，
     样式放在 `#proto-redirect-style` 里，不污染原页样式）。

## 不要碰的东西（常见误伤）

- `xmlns="http://www.w3.org/..."`：SVG/XML 命名空间，**不是链接**，动了会让 SVG 失效。
- `data-track-*` 属性里的 URL：埋点，不是 href，除非用户要求脱敏来源否则保留。
- `data:` 内联资源：媒体本体，保持不变（除非用户明确要求替换头像等具体资源）。
- 任何 `white-space:pre` / `<pre>` / `<textarea>` 内部：空白敏感，绝不插注释或换行。
