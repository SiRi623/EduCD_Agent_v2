# “面向智慧教育认知诊断的思维链可解释智能体”的后端链路

学生答题数据 -> 简化 DINA 认知诊断 -> 知识点掌握度 -> Qwen 错因分析 -> Qwen 学情报告生成 -> 报告自检优化 -> 终端输出结果。

## 目录结构

```text
backend/
├── app.py
├── main.py
├── requirements.txt
├── data/
├── models/
├── agents/
├── tools/
└── memory/
```

## 安装依赖

建议在 `EduCD-Agent/backend` 目录下创建虚拟环境后安装依赖：

```bash
pip install -r requirements.txt
```

## 配置 DASHSCOPE_API_KEY

调用真实 Qwen 之前，请先申请 Qwen Api Key，然后配置环境变量：

```bash
set DASHSCOPE_API_KEY=你的DashScope API Key
```

程序会使用 OpenAI 兼容接口：

- base_url: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- 默认模型: `qwen3.6-plus`

如果未检测到 `DASHSCOPE_API_KEY`，或真实调用失败，系统会自动进入 mock 模式，保证 Demo 不崩溃并能输出完整诊断结果。

默认服务地址：

```text
http://127.0.0.1:5000
```

第一次请求学生报告、错因分析或完整分析时会调用 Qwen，可能较慢；后续同一学生请求会走内存缓存。可以访问 `/api/cache/clear` 清除缓存。

如果没有配置 `DASHSCOPE_API_KEY`，或 Qwen API 调用失败，系统会自动进入 mock 模式，接口不会因为大模型调用失败而崩溃。

## 数据说明

`data/questions.json` 有 8 道初中数学题，覆盖一元一次方程、等式性质、代数运算、三角形面积、二次方程、函数图像、分式运算和几何证明。

`data/responses.csv` 有 5 名学生答题记录，其中 `S001` 同时包含正确题和错误题，便于观察错因分析与报告生成效果。
