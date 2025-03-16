"""JVM MCP Server入口点"""

from .core.server import MCPSearchServer


def main():
    """主函数"""
    server = MCPSearchServer()
    server.start()

if __name__ == "__main__":
    main() 