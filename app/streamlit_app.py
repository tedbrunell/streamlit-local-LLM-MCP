from dotenv import load_dotenv
load_dotenv()

import asyncio
import streamlit as st
from ui import ui
from client import MCPClient
from servers.servers_list import server_list


st.set_page_config(layout="wide", page_title="Streamlit Client for an MCP server")

st.title("Streamlit Client for an MCP server")


async def main():
    server_params = st.selectbox("Choose your MCP server", options=server_list.keys(), index=None)
    if server_params is not None:
        st.session_state.server_params = server_list[server_params]
    if not 'tools' in st.session_state:
        st.session_state.tools = []
    if "server_params" in st.session_state:
        async with MCPClient(st.session_state.server_params) as mcp_client:
            mcp_tools = await mcp_client.get_available_tools()
            st.session_state.tools = {
                tool.name: {
                    "name": tool.name,
                    "callable": mcp_client.call_tool(tool.name),
                    "schema": {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    },
                }
                for tool in mcp_tools.tools
            }
            # Available Tools
            if "tools" in st.session_state and st.session_state['tools'] is not None and len(
                    st.session_state['tools']) > 0:
                with st.sidebar:
                    st.subheader("Available Tools")
                    with st.expander("Tool List", expanded=False):
                        for tool_name, tool_details in st.session_state.tools.items():
                            st.markdown(f"- *{tool_name}*: {tool_details['schema']['function']['description']}")

            await ui()
    else:
        await ui()


if __name__ == "__main__":
    asyncio.run(main())
