namespace EmbeddingServer;

public record EmbedRequest(string? text, List<string>? texts);
public record EmbedResponse(int dimension, int count, float[][] embeddings, int[] tokensPerInput, string model, string pooling, bool normalized);
public record HealthResponse(string status, string model, int pid);
