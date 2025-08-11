import os

from mcp import StdioServerParameters


server_list = {
    "weather": StdioServerParameters(
        command="python",
        args=["app/servers/weather_server.py"],
        env=None
    ),
    "kubernetes": StdioServerParameters(
        command="/usr/bin/npx",
        args=[
            "-y",
            "kubernetes-mcp-server@latest",
            "--kubeconfig",
            "/home/ted/.kube/config",
        ]
    ),
    "github": StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-github"
        ],
        env={
            "GITHUB_PERSONAL_ACCESS_TOKEN": os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"]
        }
    ),
}
