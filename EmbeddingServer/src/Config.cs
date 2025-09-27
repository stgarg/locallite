namespace EmbeddingServer;

public record ServerConfig(
    string ModelDir,
    string ModelFile,
    string? QuantizedModelFile,
    int MaxSequenceLength,
    string ExecutionProvider,
    bool UseMeanPooling,
    bool L2Normalize,
    int InferenceBatchSize,
    string ListenHost,
    int ListenPort
)
{
    public static ServerConfig FromEnv() => new(
        ModelDir: Environment.GetEnvironmentVariable("EMB_MODEL_DIR") ?? "models/bge-small-en-v1.5",
        ModelFile: Environment.GetEnvironmentVariable("EMB_MODEL_FILE") ?? "model.onnx",
        QuantizedModelFile: Environment.GetEnvironmentVariable("EMB_MODEL_FILE_Q") ?? null,
        MaxSequenceLength: int.TryParse(Environment.GetEnvironmentVariable("EMB_MAX_SEQ"), out var msl) ? msl : 256,
        ExecutionProvider: Environment.GetEnvironmentVariable("EMB_EP") ?? "cpu", // cpu | dml
        UseMeanPooling: (Environment.GetEnvironmentVariable("EMB_POOL") ?? "mean").Equals("mean", StringComparison.OrdinalIgnoreCase),
        L2Normalize: (Environment.GetEnvironmentVariable("EMB_L2") ?? "1") != "0",
        InferenceBatchSize: int.TryParse(Environment.GetEnvironmentVariable("EMB_BATCH"), out var bs) ? bs : 16,
        ListenHost: Environment.GetEnvironmentVariable("EMB_HOST") ?? "127.0.0.1",
        ListenPort: int.TryParse(Environment.GetEnvironmentVariable("EMB_PORT"), out var p) ? p : 8080
    );
}
