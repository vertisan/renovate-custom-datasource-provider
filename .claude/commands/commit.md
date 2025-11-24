---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Bash(git log:*)
argument-hint: [message] | --no-verify | --amend
description: Create well-formatted commits with conventional commit format
---

# Smart Git Commit

Create well-formatted commit: $ARGUMENTS

## Current Repository State

- Git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Staged changes: !`git diff --cached --stat`
- Unstaged changes: !`git diff --stat`
- Recent commits: !`git log --oneline -5`

## What This Command Does

1. Checks which files are staged with `git status`
2. If 0 files are staged, automatically adds all modified and new files with `git add`
3. Performs a `git diff` to understand what changes are being committed
4. Analyzes the diff to determine if multiple distinct logical changes are present
5. If multiple distinct changes are detected, suggests breaking the commit into multiple smaller commits
6. For each commit (or the single commit if not split), creates a commit message using conventional commit format

## Best Practices for Commits

- **Verify before committing**: Ensure code is linted, builds correctly, and documentation is updated
- **Atomic commits**: Each commit should contain related changes that serve a single purpose
- **Split large changes**: If changes touch multiple concerns, split them into separate commits
- **Conventional commit format**: Use the format `<type>: <description>` where type is one of:
  - `feat`: A new feature
  - `fix`: A bug fix
  - `docs`: Documentation changes
  - `style`: Code style changes (formatting, etc)
  - `refactor`: Code changes that neither fix bugs nor add features
  - `perf`: Performance improvements
  - `test`: Adding or fixing tests
  - `chore`: Changes to the build process, tools, etc.
- **Present tense, imperative mood**: Write commit messages as commands (e.g., "add feature" not "added feature")
- **Concise first line**: Keep the first line under 72 characters
- **Briefly and eloquently**: Don't add the entire changelog into commit - just make a short summary about stated changes

## Guidelines for Splitting Commits

When analyzing the diff, consider splitting commits based on these criteria:

1. **Different concerns**: Changes to unrelated parts of the codebase
2. **Different types of changes**: Mixing features, fixes, refactoring, etc.
3. **File patterns**: Changes to different types of files (e.g., source code vs documentation)
4. **Logical grouping**: Changes that would be easier to understand or review separately
5. **Size**: Very large changes that would be clearer if broken down

## Examples

Good commit messages:

- feat: Add user authentication system
- fix: Resolve memory leak in rendering process
- docs: Update API documentation with new endpoints
- refactor: Simplify error handling logic in parser
- fix: Resolve linter warnings in component files
- chore: Improve developer tooling setup process
- feat: Implement business logic for transaction validation
- fix: Address minor styling inconsistency in header
- fix: Patch critical security vulnerability in auth flow
- style: Reorganize component structure for better readability
- fix: Remove deprecated legacy code
- feat: Add input validation for user registration form
- fix: Resolve failing CI pipeline tests
- feat: Implement analytics tracking for user engagement
- fix: Strengthen authentication password requirements
- feat: Improve form accessibility for screen readers
- ci: Added CI process for running tests

Example of splitting commits:

- First commit: feat: Add new solc version type definitions
- Second commit: docs: Update documentation for new solc versions
- Third commit: chore: Update package.json dependencies
- Fourth commit: feat: Add type definitions for new API endpoints
- Fifth commit: feat: Improve concurrency handling in worker threads
- Sixth commit: fix: Resolve linting issues in new code
- Seventh commit: test: Add unit tests for new solc version features
- Eighth commit: fix: Update dependencies with security vulnerabilities

## Command Options

- `--no-verify`: Skip running the any possible checks (lint, build, generate:docs)

## Important Notes

- If specific files are already staged, the command will only commit those files
- If no files are staged, it will automatically stage all modified and new files
- The commit message will be constructed based on the changes detected
- Before committing, the command will review the diff to identify if multiple commits would be more appropriate
- If suggesting multiple commits, it will help you stage and commit the changes separately
- Always reviews the commit diff to ensure the message matches the changes
