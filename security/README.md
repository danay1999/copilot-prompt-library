# Security Prompts

Repository-independent GitHub Copilot prompts for security and compliance workflows. Each prompt discovers *your* repository first and grounds every finding in *your* real code evidence — nothing here is tied to a specific service or stack.

## Prompts

| Prompt | Purpose | Primary output |
| ------ | ------- | -------------- |
| [`ThreatModel.prompt.md`](./ThreatModel.prompt.md) | Full STRIDE threat-model pipeline: component enumeration → data-flow diagrams → STRIDE analysis → Azure security-principle evaluation → Microsoft Threat Modeling Tool (`.tm7`) file. | A set of Markdown artifacts plus a `.tm7` model and a TMT walkthrough guide. |
| [`RaiCompliance.prompt.md`](./RaiCompliance.prompt.md) | Generate a Responsible-AI (RAI) security & compliance posture doc for an AI/LLM service: use cases, layered content/data/access controls, honest risk assessment, incident response + a real kill switch, and an AI bug bar. | A `rai-compliance.md` posture doc where every control is grounded in code, not aspirational. |
| [`AiDataFlowClassification.prompt.md`](./AiDataFlowClassification.prompt.md) | Trace an AI feature's data end-to-end (source → prompt → model → response/storage), classify every input, and verify nothing sensitive leaks through prompts, responses, logs, or caches. | An `ai-data-flow-security.md` assessment with an input-classification table and evidence-backed leak boundaries. |
| [`PrivacyDataInventory.prompt.md`](./PrivacyDataInventory.prompt.md) | Build the data inventory a privacy review (e.g., a data-use request or privacy impact assessment) needs: every data element collected, processed in-memory, stored, and shared — each classified and cited to code. | A `privacy-data-inventory.md` with per-source/store/outbound tables and a source-code map. |
| [`SecureCodeReview.prompt.md`](./SecureCodeReview.prompt.md) | Review a pull request for security and correctness regressions at high signal: derive the repo's invariants and established controls first, then check the security control families (injection, secrets/crypto, identity & least privilege, error disclosure, AI/prompt-injection, dependency hygiene) — suppressing anything linters already enforce. | One consolidated review: line-anchored, severity-tagged, evidence-cited findings within a 5–10 budget. |


## How to use

1. Copy the prompt file into your own repository under `.github/prompts/`.
2. In an editor with GitHub Copilot (e.g., VS Code) or the Copilot CLI, invoke the prompt by name and supply the inputs listed at the top of the file (e.g., `ServiceName`).
3. The agent executes the phases sequentially, presenting each as a trackable to-do and writing outputs to the paths described.
4. Review, adjust any service-specific references (work-item IDs, cluster/store names) to match your team, and commit the results.


