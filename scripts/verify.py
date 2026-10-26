# -*- coding: utf-8 -*-
"""
原型产物校验：对比 SRC(原快照) 与 DST(原型) 的不变量，确认"只改了该改的"。
用法：python3 verify.py 原型测试.html 原型.html
注意：无法真正渲染像素，这里只做结构级校验，结果需如实转述给用户。
"""
import io, re, sys
from html.parser import HTMLParser

src, dst = sys.argv[1], sys.argv[2]
a = io.open(src, encoding="utf-8").read()
b = io.open(dst, encoding="utf-8").read()

def cnt(s, needle):
    return s.count(needle)

print("==== 不变量（改前 -> 改后，应相等）====")
ok = True
for m in ["xmlns=http://www.w3.org", "data:image", "data-track-name="]:
    o, n = cnt(a, m), cnt(b, m)
    flag = "OK" if o == n else "!! 不一致"
    if o != n: ok = False
    print("  %-26s %d -> %d  %s" % (m, o, n, flag))

print("==== 结构检查 ====")
for t in ["<html", "</html>", "</head>", "<body", "</body>"]:
    print("  %-10s %d" % (t, cnt(b, t)))
do, dc = len(re.findall(r"<div\b", b)), cnt(b, "</div>")
print("  <div> 开=%d 闭=%d  %s" % (do, dc, "OK" if do == dc else "!! 不平衡"))

print("==== 改写检查 ====")
proto = len(re.findall(r'\sdata-proto-href="https?://', b))
leftover = len(re.findall(r'(?<![-\w])href="?https?://', b))
print("  外链带 data-proto-href: %d" % proto)
print("  残留 http href: %d  %s" % (leftover, "OK" if leftover == 0 else "!! 有残留"))
print("  唯一业务脚本(非空 <script>): 期望 1，文末拦截器")

print("==== HTML 解析 ====")
class P(HTMLParser):
    bad = 0
    def error(self, msg):
        self.bad += 1
        print("  解析错误:", msg)
p = P()
try:
    p.feed(b); print("  解析通过" if p.bad == 0 else "  有解析错误")
except Exception as e:
    print("  解析异常:", e); ok = False

print("\n结果:", "全部通过" if ok else "存在不一致，请检查")
