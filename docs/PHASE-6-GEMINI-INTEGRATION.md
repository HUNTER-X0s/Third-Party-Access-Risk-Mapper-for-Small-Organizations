# AccessGuard Phase 6 — Google Gemini Integration Guide

## 1. Configured Gemini Model & SDK

- **Default Pinned Model**: `gemini-3.6-flash`
- **Configurable Setting**: `GEMINI_MODEL` in `backend/app/core/config.py`.
- **Alternative High-Throughput Model**: `gemini-3.5-flash-lite`
- **SDK & Protocol**: Google GenAI REST API via `httpx.AsyncClient` with `responseMimeType: "application/json"`.

---

## 2. Environment Configuration

To enable live Gemini integration, export the API key in your server environment:

```bash
export GEMINI_API_KEY="AIzaSy..."
export GEMINI_MODEL="gemini-3.6-flash"
```

*Security Requirement: `GEMINI_API_KEY` MUST NEVER be committed to source code or returned in API responses.*

---

## 3. Provider Switching Architecture

```python
# Provider interface allows seamless switching in future phases:
class AIProvider(ABC):
    async def analyze(self, system_instruction, user_question, structured_context) -> AIAnalysisResponse:
        ...
```
Supported implementations:
- `GeminiProvider` (Active)
- `MockProvider` (Offline / Testing)
