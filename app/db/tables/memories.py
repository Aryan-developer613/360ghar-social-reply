"""Database operations for user_memories."""

from typing import Any
from supabase import Client

def create_memory(db: Client, workspace_id: int, content: str, embedding: list[float] | None = None) -> dict[str, Any]:
    """Create a new memory."""
    data = {
        "workspace_id": workspace_id,
        "content": content
    }
    if embedding:
        data["embedding"] = embedding
        
    result = db.table("user_memories").insert(data).execute()
    return result.data[0]

def list_memories(db: Client, workspace_id: int, limit: int = 50) -> list[dict[str, Any]]:
    """List memories for a workspace."""
    result = (
        db.table("user_memories")
        .select("*")
        .eq("workspace_id", workspace_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return list(result.data)

def delete_memory(db: Client, memory_id: str) -> None:
    """Delete a memory by ID."""
    db.table("user_memories").delete().eq("id", memory_id).execute()

# Note: For similarity search, we might need to use RPC (postgres function) 
# as supabase-py doesn't have native vector search operators yet.
def search_memories(db: Client, workspace_id: int, query_embedding: list[float], match_threshold: float = 0.5, match_count: int = 5) -> list[dict[str, Any]]:
    """Search memories using vector similarity."""
    try:
        # Assuming we create an RPC function named match_memories
        result = db.rpc(
            "match_memories",
            {
                "query_embedding": query_embedding,
                "match_threshold": match_threshold,
                "match_count": match_count,
                "p_workspace_id": workspace_id
            }
        ).execute()
        return list(result.data)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Vector search RPC failed: %s", e)
        return []
