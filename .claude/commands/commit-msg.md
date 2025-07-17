Generate a conventional commit message for the current staged changes.

Analyze the git diff of staged files and create a commit message following conventional commits specification:

**Format:** `<type>(<scope>): <description>`

**Types:**

- feat: new feature
- fix: bug fix
- docs: documentation
- style: formatting, missing semicolons, etc.
- refactor: code change that neither fixes a bug nor adds a feature
- test: adding or correcting tests
- chore: maintenance tasks
- ci: continuous integration changes
- revert: reverts a previous commit

**Scopes:**

- api: Lua API and Python API communication
- log: Logging and Replay functionality
- bot: Python bot framework and base classes
- examples: Example bots and usage samples
- dev: Development tools and environment

**Workflow:**

1. Run `git status` to see overall repository state. If there are are no staged changes, exit.
2. Run `git diff --staged` to analyze the actual changes
3. Run `git diff --stat --staged` for summary of changed files
4. Run `git log --oneline -10` to review recent commit patterns
5. Choose appropriate type and scope based on changes
6. Write concise description (50 chars max for first line)
7. Include body if changes are complex
8. Return the generated commit message enclosed in triple backticks

**Notes**

- Do not include emojis in the commit message.
- Do not include `🤖 Generated with [Claude Code](https://claude.ai/code)` in the commit message.
- If the list is empty, do not add any co-authors
- Include in the body of the commit message the following line as last line: `# Co-Authored-By: Claude <noreply@anthropic.com>`
