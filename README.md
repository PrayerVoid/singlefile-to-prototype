# singlefile-to-prototype

把「下载 / SingleFile 保存的网页」（通常是内联了 base64、DOM/CSS 被压缩成几行的大 `.html`）
改造成一个**可维护的单文件静态原型**：脱敏、断外链、瘦身、结构化，并且**强制保证视觉与交互和快照一致**。

这是一个 [Comate](https://comate.baidu.com) / Claude 风格的 Skill。

## 它做什么

- **脱敏**：按需移除账号/身份、来源元数据等敏感信息。
- **断外链**：所有外链改为 `href="javascript:void(0)" + data-proto-href`，点击弹出"原型不支持外跳"提示浮层。
- **瘦身**：移除惰性标签（空 `<script>`、隐藏空 `<iframe>` 等）。
- **结构化**：顶部结构地图注释 + 可 grep 的 `SECTION:` 地标，方便后续快速定位修改。
- 始终保持**单一 HTML 文件**，CSS 不拆分。

## 核心原则

只做**定点替换**，绝不重排已压缩的 DOM/CSS —— 任何空白变动都可能改变渲染。
可读性靠注释地标实现，不靠 pretty-print。

## 结构

```
singlefile-to-prototype/
├── SKILL.md                         # 工作流主文件（含并行 subagent 策略）
├── references/
│   └── code-organization.md         # 产物代码组织格式（硬约定）
└── scripts/
    ├── transform_template.py        # 参数化改写脚本模板，填 CONFIG 即用
    └── verify.py                     # 不变量校验脚本
```

## 用法

1. 阅读 `SKILL.md`，按工作流并行侦察、与用户确认脱敏/外链等决策。
2. 复制 `scripts/transform_template.py`，填好顶部 `CONFIG`，运行生成原型。
3. 用 `scripts/verify.py 原快照.html 原型.html` 做结构级不变量校验。

详见 `references/code-organization.md`。
