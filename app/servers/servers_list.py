import os

from mcp import StdioServerParameters


server_list = {
	"g-maps": StdioServerParameters(
		command="/usr/bin/npx",
		args=["-y", "@modelcontextprotocol/server-google-maps"],
		env={
			"GOOGLE_MAPS_API_KEY": os.getenv("GMAP_API_KEY")
		}
	),
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
            "/home/tbrunell/.kube/config",
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
