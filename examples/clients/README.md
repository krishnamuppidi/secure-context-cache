# Client Examples

These examples show the intended integration boundary: an application authenticates to the
gateway, requests a task-scoped optimization plan, and passes only the released capsule to a model.
The stable context precedes volatile task text so native provider prompt caching can reuse the
exact prefix. Never pass the Cognito client secret, access token, or local API key to a model.

- OpenAI uses `prompt_cache_key`.
- Anthropic places an ephemeral cache breakpoint after the stable context.
- Amazon Bedrock adds a cache checkpoint between stable context and the task.
- All three surface provider usage so it can be normalized separately from SCC estimates.

## Python

The standard-library client has no additional dependencies:

```bash
python examples/clients/python/acg_client.py \
  architecture_qa \
  README.md \
  "Explain the gateway architecture" \
  --context-block
```

For AWS, source `deploy/aws/.acg-deployment.env` first. For local API mode, set
`ACG_LOCAL_API_KEY` and `ACG_LOCAL_AGENT_ID` to the values used by the server.

`bedrock_converse.py` adds `boto3` and requires `BEDROCK_MODEL_ID`. It demonstrates fetching a
capsule before calling the Amazon Bedrock Converse API.

Additional optional examples preserve the same boundary:

- `openai_responses.py` uses the OpenAI Responses API after fetching a capsule.
- `anthropic_messages.py` uses the Anthropic Messages API after fetching a capsule.
- `langchain_context.py` supplies the bounded context block to a LangChain chat model.
- `mcp_server.py` exposes a narrow `request_context_capsule` MCP tool rather than raw source access.
- `litellm_completion.py` keeps SCC as the context boundary and uses LiteLLM for downstream routing.
- `vllm_prefix_cache.py` passes an SCC trust-scoped cache salt to a self-hosted vLLM endpoint.

Install only the SDKs used by the consuming application. These examples intentionally remain
outside the core package dependencies.

## TypeScript

`typescript/acg-client.ts` uses the Node.js 18+ built-in `fetch` implementation. Import
`getOAuthToken`, `requestCapsule`, and `buildContextBlock` into an agent application. Compile it
with the consuming application's TypeScript configuration; it intentionally has no framework
dependency.

See [Agent Integration](../../docs/AGENT_INTEGRATION.md) for complete flows and security guidance.

## Generic REST

`curl/request-capsule.sh` demonstrates a direct bearer-authenticated call. It reads credentials
from environment variables and never prints or sends them to a model.
