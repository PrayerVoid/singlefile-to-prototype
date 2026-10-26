# -*- coding: utf-8 -*-
"""
SingleFile 快照 -> 单文件静态原型 的改写脚本（模板）。
用法：按阶段 1/2 的调查结论填好下面的 CONFIG，然后 `python3 transform_template.py`。
原则：只做定点替换，不重排 DOM/CSS，强制保证视觉与交互不变。
每一步都带计数与 assert，确保"只改了该改的"。
"""
import re, sys, io

# ============================ CONFIG（按页面填写）============================
SRC = "/path/to/原型测试.html"      # 输入快照
DST = "/path/to/原型.html"          # 输出原型（新文件，勿覆盖原文件）

# 1) 脱敏·字面替换：[(原文, 占位), ...]  例：用户名、账号
LITERAL_DESENS = [
    # ("real_user", "demo_user"),
]
# 2) 脱敏·正则替换：[(pattern, repl, 说明), ...]  例：头像首字母、邮箱、手机号
REGEX_DESENS = [
    # (r"(id=username title=demo_user>\s*)R(\s*</a>)", r"\1D\2", "头像首字母"),
]
# 3) 是否移除 SingleFile 顶部来源注释（url / saved date）
REMOVE_SINGLEFILE_COMMENT = True

# 4) 瘦身：移除惰性标签（正则列表）
STRIP_PATTERNS = [
    (r"<script>\s*</script>", "空 script"),
    (r"<iframe src style=display:none></iframe>", "隐藏空 iframe"),
]

# 5) SECTION 地标：[(锚点唯一字符串, 中文名/english), ...]
#    锚点必须能在文件中唯一命中；注释紧贴锚点前插入，不加空白。
LANDMARKS = [
    # ('<style>:root{--sf-img', "资源图片库 base64（勿手改）/ asset image library"),
    # ('<div id=root-app-container', "应用根容器 / app root"),
    # ('<div class="main-area', "主内容区 / main content"),
]

# 6) 顶部结构地图文案（<html ...> 之后插入）；留空则用自动模板
PROTOTYPE_MAP = ""

# 7) HTML 根标签（用于插入 MAP 的锚点），按实际填写
HTML_OPEN_TAG = "<html lang=zh>"
# ===========================================================================

with io.open(SRC, "r", encoding="utf-8") as f:
    html = f.read()
orig_len = len(html)
report = []

def must(cond, msg):
    if not cond:
        print("ASSERT FAILED:", msg); sys.exit(1)

# --- 1) 来源注释 ---
if REMOVE_SINGLEFILE_COMMENT:
    pat = re.compile(r"<!--\s*\n?\s*Page saved with SingleFile.*?-->", re.S)
    html, n = pat.subn("", html)
    report.append("SingleFile 来源注释移除: %d" % n)

# --- 2) 字面脱敏 ---
for src, dst in LITERAL_DESENS:
    c = html.count(src)
    html = html.replace(src, dst)
    report.append("脱敏 %r -> %r: %d" % (src, dst, c))
    must(c >= 1, "脱敏串未命中: %r" % src)

# --- 3) 正则脱敏 ---
for pat, repl, desc in REGEX_DESENS:
    html, n = re.subn(pat, repl, html)
    report.append("脱敏(正则) %s: %d" % (desc, n))
    must(n >= 1, "脱敏正则未命中: %s" % desc)

# --- 4) 外链改写：所有 href=http(s) -> javascript:void(0) + data-proto-href ---
html, n_q = re.subn(r'href="(https?://[^"]*)"',
                    lambda m: 'href="javascript:void(0)" data-proto-href="%s"' % m.group(1), html)
html, n_u = re.subn(r'href=(https?://[^\s">]+)',
                    lambda m: 'href="javascript:void(0)" data-proto-href="%s"' % m.group(1), html)
report.append("外链改写 带引号=%d 无引号=%d" % (n_q, n_u))
# 真正的 href 属性（排除 data-proto-href）不应再指向 http
left = len(re.findall(r'(?<![-\w])href="?https?://', html))
must(left == 0, "仍有 %d 个 http href 未处理" % left)

# --- 5) 瘦身 ---
for pat, desc in STRIP_PATTERNS:
    html, n = re.subn(pat, "", html)
    report.append("移除 %s: %d" % (desc, n))

# --- 6) SECTION 地标（紧贴锚点前插入，无空白）---
for anchor, name in LANDMARKS:
    i = html.find(anchor)
    if i == -1:
        report.append("地标未命中(跳过): %s" % anchor[:40]); continue
    html = html[:i] + "<!-- ========== SECTION: %s ========== -->" % name + html[i:]
    report.append("地标注释: %s" % name)

# --- 7) 顶部结构地图 ---
mp = PROTOTYPE_MAP or (
    "<!--\n  ====== 原型结构地图 PROTOTYPE MAP ======\n"
    "  纯静态原型：无可运行业务 JS（唯一脚本为文末外链拦截器）。\n"
    "  用 `SECTION:` 关键字可跳转各区块。外链一律 href=\"javascript:void(0)\" + data-proto-href。\n"
    "  视觉/交互须与快照一致，勿重排已压缩的 DOM 行。\n  ======================================\n-->"
)
must(HTML_OPEN_TAG in html, "找不到 HTML 根标签: %s" % HTML_OPEN_TAG)
html = html.replace(HTML_OPEN_TAG, HTML_OPEN_TAG + mp, 1)
report.append("顶部结构地图已插入")

# --- 8) 外链跳转提示浮层 + 唯一脚本，追加文末 ---
REDIRECT = (
    "<!-- ========== SECTION: 外链跳转提示浮层 / prototype redirect overlay ========== -->\n"
    "<style id=proto-redirect-style>\n"
    ".proto-redirect-mask{position:fixed;inset:0;z-index:2147483647;display:none;"
    "align-items:center;justify-content:center;background:rgba(0,0,0,.45);font-family:inherit}\n"
    ".proto-redirect-mask.proto-open{display:flex}\n"
    ".proto-redirect-box{max-width:520px;width:90%;background:#fff;border-radius:8px;"
    "box-shadow:0 8px 32px rgba(0,0,0,.2);padding:24px 28px;color:#1f1f1f;box-sizing:border-box}\n"
    ".proto-redirect-box h3{margin:0 0 12px;font-size:16px;font-weight:600}\n"
    ".proto-redirect-box p{margin:0 0 10px;font-size:13px;line-height:1.6;color:#555}\n"
    ".proto-redirect-url{display:block;word-break:break-all;background:#f5f5f5;"
    "border:1px solid #eee;border-radius:4px;padding:8px 10px;font-size:12px;color:#2b6cb0;margin:8px 0 16px}\n"
    ".proto-redirect-box .proto-btns{text-align:right}\n"
    ".proto-redirect-box button{border:none;background:#2468f2;color:#fff;border-radius:4px;"
    "padding:7px 18px;font-size:13px;cursor:pointer}\n"
    ".proto-redirect-box button:hover{background:#1a53d0}\n"
    "</style>\n"
    "<div class=proto-redirect-mask id=protoRedirectMask>\n"
    "  <div class=proto-redirect-box role=dialog aria-modal=true>\n"
    "    <h3>原型提示 · 外部跳转已禁用</h3>\n"
    "    <p>这是一个静态原型页面，不支持跳转到外部站点。你点击的链接原本将跳转到：</p>\n"
    "    <code class=proto-redirect-url id=protoRedirectUrl></code>\n"
    "    <p>在真实环境中，该链接会打开上述地址。</p>\n"
    "    <div class=proto-btns><button type=button id=protoRedirectClose>知道了</button></div>\n"
    "  </div>\n"
    "</div>\n"
    "<!-- 唯一脚本：拦截 data-proto-href 外链点击并弹出提示 -->\n"
    "<script>\n"
    "(function(){\n"
    "  var mask=document.getElementById('protoRedirectMask');\n"
    "  var urlEl=document.getElementById('protoRedirectUrl');\n"
    "  function open(u){urlEl.textContent=u||'(未知地址)';mask.classList.add('proto-open');}\n"
    "  function close(){mask.classList.remove('proto-open');}\n"
    "  document.addEventListener('click',function(e){\n"
    "    var a=e.target.closest?e.target.closest('a[data-proto-href]'):null;\n"
    "    if(a){e.preventDefault();e.stopPropagation();open(a.getAttribute('data-proto-href'));return;}\n"
    "    if(e.target.id==='protoRedirectClose'||e.target===mask){close();}\n"
    "  },true);\n"
    "  document.addEventListener('keydown',function(e){if(e.key==='Escape')close();});\n"
    "})();\n"
    "</script>\n"
    "</body></html>\n"
)
html = html.rstrip() + "\n" + REDIRECT

with io.open(DST, "w", encoding="utf-8") as f:
    f.write(html)

print("==== TRANSFORM REPORT ====")
for r in report:
    print(" -", r)
print(" - 原始大小: %d 字节" % orig_len)
print(" - 输出大小: %d 字节" % len(html))
print(" - 输出文件: %s" % DST)


