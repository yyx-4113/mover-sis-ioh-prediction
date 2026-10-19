# GitHub 复现包发布操作手册（中文）

> 适用仓库：`yyx-4113/mover-sis-ioh-prediction`
> 用途：将每份科研稿件的「分析代码 + 配置 + 审计追踪 + 聚合产物」落盘为公开实名仓库，
> 供数据可用性声明引用，并附 release tag 以支持可复现核查。

## 一、首次创建仓库

1. 确认已登录 `gh`（账户 `yyx-4113`，具备 `repo` scope）：
   ```
   gh auth status
   ```
2. 在本地项目根目录初始化并提交（`.gitignore` 已排除患者级派生 CSV 与 `.workbuddy/`）：
   ```
   git init
   git add -A
   git commit -m "init: MOVER/SIS IOH prediction reproduction package"
   git branch -M main
   ```
3. 创建公开仓库并一次性推送：
   ```
   gh repo create yyx-4113/mover-sis-ioh-prediction --public --source=. --remote=origin --push
   ```

## 二、打 tag 与 release

每次稿件进入「可投稿」状态，打一个语义化 tag 并在数据可用性声明中引用：

```
git tag v1.0.0
git push origin v1.0.0
gh release create v1.0.0 --title "v1.0.0" --notes "Reproduction package for manuscript v0.1 (BMC Anesthesiology submission)."
```

- 标签命名：`v<主>.<次>.<修订>`，与稿件版本对应。
- release notes 写明对应稿件版本与关键变更。

## 三、更新正文数据可用性声明

推送后，将 `manuscript/manuscript_v0.1.md` 中数据可用性段落的占位 URL 改为：

```
https://github.com/yyx-4113/mover-sis-ioh-prediction (release v1.0.0)
```

并删除遗留的 `> ⚠️ TODO` 元注释块。**声明必须与仓库实际状态相符**：
若仓库尚未创建或 tag 未打，不得声称已可用（比照 2026-09-27 教训）。

## 四、后续更新

- 任何 s2→s3→s4 重跑导致数字变化后：重新生成 `MANIFEST.csv`、重新打 tag、更新正文引用。
- 患者级派生文件（`s1_anchor.csv` / `s1_labels.csv` / `s1_labels_postanchor.csv` /
  `s2_features.csv`）**永不纳入仓库**（DUA 限制）。
- 切勿推送 `.workbuddy/`（含项目记忆）。

## 五、核验清单

- [ ] `gh repo view yyx-4113/mover-sis-ioh-prediction` 可访问
- [ ] release tag 存在且正文引用一致
- [ ] `MANIFEST.csv` 校验和与本地一致
- [ ] 患者级 CSV 不在仓库
- [ ] `.workbuddy/` 不在仓库
