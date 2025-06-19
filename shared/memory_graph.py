import networkx as nx
from datetime import datetime
from langchain_community.embeddings import OpenAIEmbeddings

class MemoryGraph:
    """Hybrid memory structure combining vector search with symbolic edges."""

    def __init__(self, vector_store, embedding_model=None):
        self.vector_store = vector_store
        self.graph = nx.DiGraph()
        self.embedding_model = embedding_model or OpenAIEmbeddings()

    def add_memory(self, text, metadata=None, salience=1.0):
        """Add a memory node with associated vector and metadata."""
        node_id = str(len(self.graph))
        timestamp = datetime.utcnow().isoformat()
        data = {
            "text": text,
            "timestamp": timestamp,
            "salience": salience,
        }
        if metadata:
            data.update(metadata)
        self.graph.add_node(node_id, **data)
        self.vector_store.add_texts([text], metadatas=[{"node_id": node_id, **data}])
        return node_id

    def link_memories(self, src_id, dst_id, label=None):
        """Create a symbolic edge between two memories."""
        self.graph.add_edge(src_id, dst_id, label=label)

    def query(self, text, after=None, k=5):
        """Retrieve relevant memories with optional temporal filtering."""
        docs_and_scores = self.vector_store.similarity_search_with_score(text, k=k)
        results = []
        for doc, score in docs_and_scores:
            meta = doc.metadata
            ts = meta.get("timestamp")
            if after and ts and ts <= after.isoformat():
                continue
            results.append((meta.get("node_id"), doc.page_content, score))
        return results

    def prune(self, min_salience=0.3):
        """Remove memories below a salience threshold."""
        to_remove = [n for n, d in self.graph.nodes(data=True) if d.get("salience", 0) < min_salience]
        if not to_remove:
            return
        self.graph.remove_nodes_from(to_remove)
        self.vector_store.delete(to_remove)

    def multi_hop_context(self, start_id, hops=2):
        """Gather text from multi-hop neighbors starting from a node."""
        context = []
        visited = {start_id}
        frontier = [(start_id, 0)]
        while frontier:
            node, depth = frontier.pop(0)
            context.append(self.graph.nodes[node]["text"])
            if depth >= hops:
                continue
            for nbr in self.graph.neighbors(node):
                if nbr not in visited:
                    visited.add(nbr)
                    frontier.append((nbr, depth + 1))
        return "\n".join(context)
