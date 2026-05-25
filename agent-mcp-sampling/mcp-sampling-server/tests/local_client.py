import asyncio
import os
from mcp.client.streamable_http import streamable_http_client
from mcp.client.session import ClientSession
from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult, SamplingMessage,
    TextContent
)
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Token provider for OpenAI
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")

# ---------- LLM client ----------
aoai_client = OpenAI(
    base_url=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=token_provider
)

DEPLOYMENT = os.environ["AZURE_OPENAI_DEPLOYMENT"]


def _flatten_text_content(content_blocks) -> str:
    """
    content_blocks can be:
      - TextContent
      - list[TextContent|ImageContent|AudioContent] depending on SDK/version
    """

    if content_blocks is None:
        return ""

    # Newer/strict cases: content is a single block (TextContent)
    if isinstance(content_blocks, TextContent):
        return content_blocks.text or ""

    # Some variants: content is a list of blocks
    if isinstance(content_blocks, list):        
        return "\n".join(
                    b.text for b in content_blocks
                    if isinstance(b, TextContent) and b.text
                ).strip()

    # Fallback
    return str(content_blocks)


# ---------- Sampling handler ----------
async def sampling_handler(*args) -> CreateMessageResult:
    """
    This is invoked when server calls ctx.sample()
    """

    params = args[-1]
    assert isinstance(params, CreateMessageRequestParams)

    print(">>> sampling_handler invoked")
    print(">>> params =", params)

    messages = []

    if getattr(params, "systemPrompt", None):
        messages.append({"role": "system", "content": params.systemPrompt})

    for m in params.messages:
        text = _flatten_text_content(m.content)
        if text:
            messages.append({
                "role": m.role,
                "content": text,
            })

    # print(messages)

    resp = aoai_client.chat.completions.create(
        model=DEPLOYMENT,
        messages=messages,
        temperature=params.temperature or 0.2,
        max_completion_tokens=params.maxTokens or 256,
    )

    out_text = resp.choices[0].message.content or ""


    result = CreateMessageResult(
        role="assistant",
        model=DEPLOYMENT,
        content=TextContent(type="text",text=out_text),
        stopReason="endTurn"
    )


    print(">>> returning CreateMessageResult:", result)
    print(">>> type(content) =", type(result.content))
    return result


async def mcp_tool_call_sampling():
    # Transport connect client session with read/ write streams
    async with streamable_http_client("http://localhost:8000/mcp") as (read, write, _):
        async with ClientSession(
            read,
            write,
            sampling_callback=sampling_handler,   # enables sampling
        ) as session:

            await session.initialize()

            result = await session.call_tool(
                "summarize",
                arguments={"content": "MCP sampling delegates LLM calls to clients."}
            )

            print(">>> Tool call result:", result.content[0].text)

async def mcp_tool_call():
    # Transport connect client session with read/ write streams
    async with streamable_http_client("http://localhost:8000/mcp") as (read, write, _):
        async with ClientSession(
            read,
            write,
        ) as session:

            await session.initialize()

            result = await session.call_tool(
                "add",
                arguments={"a": "1", "b": "2"}
            )

            print(">>> Tool call result:", result.content[0].text)

# ---------- Main ----------
async def main():
    await mcp_tool_call_sampling()
    await mcp_tool_call()

if __name__ == "__main__":
    asyncio.run(main())

