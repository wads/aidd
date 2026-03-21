---
name: retrospective
description: KPT形式の振り返りスキル。
user-invocable: true
---

# Retrospective

KPT形式の振り返りスキル。

## Arguments

- topic: 振り返りの対象（必須）
## Process

1. **Setup (準備)**
   - 振り返り対象のフェーズ/タスクを確認

2. **KPT Analysis (KPT分析)**
   - 以下の観点で振り返りを実施:
     - **Keep**: うまくいったこと、続けること
     - **Problem**: 問題だったこと、改善が必要なこと
     - **Try**: 次に試すこと、改善案

3. **Record (記録)**
   - `tasks/retrospectives/YYYY-MM-DD-[topic].md` に振り返りを記録
   - テンプレート: `docs/templates/retrospective-template.md`

4. **Extract Lessons (教訓抽出)**
   - 汎用的な教訓を `tasks/lessons.md` に追記
   - プロジェクト固有でなく、他のプロジェクトでも活用できるもの

5. **Process Improvement (プロセス改善)**
   - プロセス改善提案がある場合は人間に提示
   - 承認されたら `docs/process/*.md` に反映

## Output

- `tasks/retrospectives/YYYY-MM-DD-[topic].md` - 振り返り記録
- `tasks/lessons.md` への追記（該当する場合）
- プロセス改善提案（該当する場合）
