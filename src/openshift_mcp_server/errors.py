def error_response(message: str, details: str = None) -> dict:
    resp = {"error": message}
    if details:
        resp["details"] = details
    return resp

class MCPError(Exception):
    """Base class for MCP server errors."""
    pass
