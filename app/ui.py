import json
import os
from typing import List

import streamlit as st
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

gpt_client = AsyncOpenAI(
    api_key=os.getenv("API_KEY", ""),
    base_url=os.getenv("API_ENDPOINT")
)

async def ui():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        # skip tool calls
        if message["role"] == "tool" or 'tool_calls' in message:
            continue
        else:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Thinking..."):
            response, messages = await agent_loop(st.session_state.tools, gpt_client, st.session_state.messages)
            st.session_state.messages = messages
            with st.chat_message("assistant"):
                st.markdown(response)


async def agent_loop(tools: dict, llm_client: AsyncOpenAI, messages: List[dict]):
    first_response = await llm_client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages,
        tools=([t["schema"] for t in tools.values()] if len(tools) > 0 else None),
        temperature=0,
    )

    stop_reason = (
        "tool_calls"
        if first_response.choices[0].message.tool_calls is not None
        else first_response.choices[0].finish_reason
    )

    if stop_reason == "tool_calls":
        for tool_call in first_response.choices[0].message.tool_calls:
            arguments = (
                json.loads(tool_call.function.arguments)
                if isinstance(tool_call.function.arguments, str)
                else tool_call.function.arguments
            )
            tool_result = await tools[tool_call.function.name]["callable"](**arguments)
            messages.append(
                first_response.choices[0].message.to_dict()
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": json.dumps(tool_result),
                }
            )

            with st.chat_message("assistant"):
                st.markdown(f"""Using tool:```{tool_call.function.name}({arguments})```to answer this question.""")

            # with st.chat_message("assistant"):
            #     st.markdown(f"Tool response: {tool_result}")

            messages.append(
                {
                    "role": "assistant",
                    "content": f"""Using tool:```{tool_call.function.name}({arguments})```to answer this question."""
                }
            )

        new_response = await llm_client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
        )

    elif stop_reason == "stop":
        new_response = first_response

    else:
        raise ValueError(f"Unknown stop reason: {stop_reason}")

    messages.append(
        {"role": "assistant", "content": new_response.choices[0].message.content}
    )

    return new_response.choices[0].message.content, messages
