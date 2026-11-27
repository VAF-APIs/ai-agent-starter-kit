# Publish to GunalanVaf/ai-agent-starter-kit

The repository already exists with a README. Review company IP and obtain approval for the open-source license (MIT or Apache-2.0); add the approved LICENSE before publishing. No client data or real credentials belong in this repository. Consider keeping the repository private until approval.

1. Extract the ZIP to Downloads. In PowerShell run:

```powershell
cd $HOME\Downloads
git clone https://github.com/GunalanVaf/ai-agent-starter-kit.git
robocopy .\vaf-ai-agent-starter-kit .\ai-agent-starter-kit /E /XD .git .venv __pycache__ .pytest_cache /XF .env
cd .\ai-agent-starter-kit
```

Robocopy exit codes 0–7 normally indicate success; 8 or greater means a failure. Adjust paths if extracted elsewhere. Review files and add the approved LICENSE using GitHub or locally.

```powershell
git status
git add .
git diff --cached --stat
git diff --cached
git commit -m "Add AI Agent Starter Kit v0.1.1"
git push origin main
```

Use Git Credential Manager's browser sign-in with the office account. Do not share tokens. Verify the Actions tab and README after push. In About settings, set website https://vaf.ai/ and topics: ai-agents, agentic-ai, llm, python, fastapi, ollama, openai, document-qa, developer-tools.
