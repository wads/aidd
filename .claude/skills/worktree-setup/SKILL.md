# Worktree Setup

git worktree + topic branchセットアップスキル。

## Usage

User-invocable: `/worktree-setup`

## Arguments

- feature: 機能名（必須、branch名に使用）
- type: ブランチタイプ（省略時: feature）
  - feature, fix, refactor, docs, test

## Process

1. **Confirm (確認)**
   - 作成するbranch名を提示: `[type]/[feature]`
   - worktreeディレクトリ名を提示: `../[project]-[type]-[feature]`（プロジェクト名は自動取得）
   - 人間に確認

2. **Create Worktree**
   ```
   git worktree add ../[project]-[type]-[feature] -b [type]/[feature]
   ```

3. **Verify**
   - worktreeが正しく作成されたか確認
   - branchが正しく作成されたか確認

4. **Report**
   - 作成結果を報告
   - 作業ディレクトリのパスを表示

## Branch Naming Convention

- `feature/<description>` - 新機能
- `fix/<description>` - バグ修正
- `refactor/<description>` - リファクタリング
- `docs/<description>` - ドキュメント
- `test/<description>` - テスト追加・修正

## Notes

- worktreeは親ディレクトリに作成される
- 作業完了後は `git worktree remove` で削除
- メインのworking directoryは常にcleanに保つ
