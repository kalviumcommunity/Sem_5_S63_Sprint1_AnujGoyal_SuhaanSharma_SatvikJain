# 🤝 Team Collaboration & Git Workflow Guidelines

## 👥 Project Team
- **Anuj Goyal**
- **Suhaan Sharma**
- **Satvik Jain**

**Project:** Learning Behaviour & Course Completion Analytics

---

## 🌿 1. Git Branching Strategy

Our team uses a structured Git Flow adapted for the 50-concept sprint roadmap:

```text
main (Production / Stable Releases)
  │
  └── develop (Integration Branch)
        │
        ├── feature/01-environment-setup
        ├── feature/02-github-workflow
        ├── feature/03-python-workflow
        ├── ...
        ├── fix/data-null-imputation
        └── docs/architecture-updates
```

### 🏷️ Branch Types and Naming Conventions

| Branch Type | Format / Pattern | Example | Purpose |
| :--- | :--- | :--- | :--- |
| **Main** | `main` | `main` | Production-ready, verified codebase |
| **Develop** | `develop` | `develop` | Active integration branch for sprint merges |
| **Feature** | `feature/<concept-num>-<short-description>` | `feature/02-github-workflow` | Implementing specific sprint concepts |
| **Bugfix** | `fix/<issue-id>-<short-description>` | `fix/14-null-handling` | Resolving bugs or broken tests |
| **Docs** | `docs/<description>` | `docs/api-reference` | Documentation and architecture updates |
| **Refactor** | `refactor/<module-name>` | `refactor/pipeline-cleanup` | Code restructuring without feature changes |

---

## 🔄 2. Step-by-Step Feature Branch Lifecycle

1. **Sync with Base Branch:**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create a Feature Branch:**
   ```bash
   git checkout -b feature/<concept-number>-<name>
   ```

3. **Develop & Implement:**
   - Preserve existing functionality from previous concepts.
   - Write clean, modular Python code with type hints and docstrings.
   - Follow PEP8 styling guidelines.

4. **Run Local Validation (Mandatory):**
   ```bash
   # 1. Run unit tests
   python -m pytest

   # 2. Verify main pipeline entry point
   python main.py

   # 3. Verify Streamlit dashboard (if UI touched)
   streamlit run dashboard/app.py
   ```

5. **Stage & Commit:**
   ```bash
   git add <modified-files>
   git commit -m "<type>: <concise description>"
   ```

6. **Push Branch & Open PR:**
   ```bash
   git push -u origin feature/<concept-number>-<name>
   ```

---

## 💬 3. Commit Message Standards (Conventional Commits)

All commits must follow the **Conventional Commits** standard:

```text
<type>(<optional scope>): <description>

[optional body]
```

### Common Types:
- `feat:` A new feature or sprint concept implementation (e.g., `feat: add behavioral risk scoring model`)
- `fix:` A bug fix in pipeline or dashboard (e.g., `fix: resolve division by zero in quiz progress`)
- `docs:` Documentation updates (e.g., `docs: establish github team workflow`)
- `test:` Adding or updating tests (e.g., `test: add unit tests for session cleaning`)
- `refactor:` Code changes that neither fix a bug nor add a feature
- `chore:` Maintenance tasks, dependency updates, or git configurations
- `ci:` GitHub Actions / workflow updates

---

## 🔍 4. Pull Request & Code Review Process

1. **Title Format:** `feat(concept-<num>): <description>` (e.g., `feat(concept-02): establish github team workflow`)
2. **Use the PR Template:** Complete all sections in the pull request checklist.
3. **Peer Review:**
   - At least **one team member** (Anuj, Suhaan, or Satvik) must review and approve before merging.
   - Verify that all unit tests pass and code preserves previous concepts.
4. **Merge Strategy:**
   - **Squash and Merge** or **Rebase and Merge** to maintain a clean linear commit history.
5. **Post-Merge Cleanup:**
   - Delete feature branches on remote once merged to keep the repository clean.

---

## 🛡️ 5. Conflict Resolution & Syncing

If another team member pushed updates to the base branch:

```bash
# Fetch latest remote changes
git fetch origin

# Rebase your feature branch on top of updated base
git rebase origin/main

# If conflicts occur, resolve them in VS Code, then:
git add <resolved-files>
git rebase --continue
```
