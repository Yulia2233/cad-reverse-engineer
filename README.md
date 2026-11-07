# cad-reverse-engineer

SimpleCADAPI 2.2.7 Agent Skill（`simplecadapi`）的改版：**STEP 逆向工作流按 STEPIR v6.2 重写**，其余部分与上游 [PhySpace/SimpleCADAPI](https://github.com/PhySpace/SimpleCADAPI) `release/2.2.7` 相同。

## 改了什么

| 文件 | 改动 |
|---|---|
| `skill/references/workflows/step-reconstruction.md` | 整篇重写：固定 6 步流程（读 IR → 规划特征 → 写 notebook 主体 → 评测 → 加倒角圆角 → 只修出错单元格 → report.json）、该读和不该读的文件、网页编辑器 notebook 格式规则、2.2.7 实测 API 卡片、选边配方 |
| `skill/references/inspect/stepir.md` | 新增：STEPIR v6.2 的完整格式、每类记录怎么对应到 SimpleCAD 调用、注意事项（局部坐标系 `y = n × x`、顺时针弧交换起止点、`ext`/`cut` 方向等） |
| `skill/scripts/stepir.py` | 新增：STEPIR v6.2.2 单文件版（STEP → IR，`query face/evidence/axis/neighbours` 按需查询） |
| `skill/scripts/stepeval.py` | 新增：一条命令完成 notebook 格式检查、新进程运行、与目标比较（体积 IoU、缺失/多余区域、按 STEPIR 归一化后的面数与曲面类型完整性，不受原文件面切分方式影响），输出一行 JSON，`"ok": true` 为验收 |
| `skill/SKILL.md` | 逆向任务入口说明；STEP 逆向任务不必读 notebook 运行时、特征树约定等长文档（工作流已给出完整规则）；参考列表加入 STEPIR 与两个脚本 |
| `skill/references/README.md`、`domains/step-inspection.md` | 指向新的 IR 文档 |

## 目录

```
skill/                  源码（含按平台的条件编译块）
builds/                 编译好的版本，直接复制即可用
  simplecadapi-codex/        Codex
  simplecadapi-claudecode/   Claude Code
  simplecadapi-opencode/     OpenCode / cad-code
tools/skillbuild.py     从 skill/ 编译各平台版本（上游工具，未改）
skillproj.toml          编译配置
```

## 安装

需要 Python 3.10–3.13 与 SimpleCADAPI 2.2.7（含 OCP，脚本要用）；评测脚本另需 `manifold3d`：

```bash
pip install "simplecadapi[editor,verify]==2.2.7" manifold3d
```

把对应平台的编译版本复制到该平台的技能目录，目录名用 `simplecadapi`，例如 Codex：

```bash
cp -R builds/simplecadapi-codex ~/.codex/skills/simplecadapi
```

重新编译（修改 `skill/` 之后）：

```bash
python tools/skillbuild.py            # 全部平台
python tools/skillbuild.py --target codex
python tools/skillbuild.py --check    # 只校验
```

## 逆向流程用法

```bash
python <skill>/scripts/stepir.py target.step --out target.ir.jsonl
python <skill>/scripts/stepeval.py part.py target.step --out eval/1
```

交付物是网页编辑器格式的 marimo notebook（`sca edit part.py` 可直接打开），必须独立建模、不读取目标几何。

## 验证

用 gpt-6.1-sol（Codex CLI 与 cad-code 两种环境）测试：平面圆角件、含环面/球面角片的折弯件、回转加自由曲面的电容件、平面加倒角圆角的电池座，均在 2–9 次评测内达到 `"ok": true`（rIoU 0.9998–1.0，面数与目标一致），无生成器脚本、无调试副本、无渲染。

## 许可

Apache-2.0，与上游相同（`LICENSE`）。STEPIR 源码见 [Yulia2233/step-tools](https://github.com/Yulia2233/step-tools)。
