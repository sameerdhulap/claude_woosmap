from core import mcp

# Import tools so they register with MCP
import localities  # noqa
import distance  # noqa
import transit  # noqa


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
