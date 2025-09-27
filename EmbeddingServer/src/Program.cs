using EmbeddingServer;
using System.Text.Json;

var cfg = ServerConfig.FromEnv();

if (args.Length > 0 && (args[0] == "--help" || args[0] == "-h" || args[0] == "help"))
{
    Console.WriteLine("FastEmbed Text Embedding Server");
    Console.WriteLine("===============================");
    Console.WriteLine();
    Console.WriteLine("USAGE:");
    Console.WriteLine("  EmbeddingServer.exe [COMMAND] [OPTIONS]");
    Console.WriteLine();
    Console.WriteLine("COMMANDS:");
    Console.WriteLine("  (no args)              Start REST API server (default)");
    Console.WriteLine("  --text \"your text\"     Get embedding for single text");
    Console.WriteLine("  --health               Check if server can start successfully");
    Console.WriteLine("  --help, -h, help       Show this help message");
    Console.WriteLine();
    Console.WriteLine("EXAMPLES:");
    Console.WriteLine("  EmbeddingServer.exe");
    Console.WriteLine("    → Starts server at http://localhost:8080");
    Console.WriteLine();
    Console.WriteLine("  EmbeddingServer.exe --text \"Hello world\"");
    Console.WriteLine("    → Returns JSON with embedding vector");
    Console.WriteLine();
    Console.WriteLine("  EmbeddingServer.exe --health");
    Console.WriteLine("    → Returns 'healthy' if model loads successfully");
    Console.WriteLine();
    Console.WriteLine("CONFIGURATION (Environment Variables):");
    Console.WriteLine("  EMB_MODEL_DIR          Model directory (default: models/bge-small-en-v1.5)");
    Console.WriteLine("  EMB_MODEL_FILE         Model filename (default: model.onnx)");
    Console.WriteLine("  EMB_HOST               Listen host (default: 127.0.0.1)");
    Console.WriteLine("  EMB_PORT               Listen port (default: 8080)");
    Console.WriteLine("  EMB_MAX_SEQ            Max sequence length (default: 256)");
    Console.WriteLine("  EMB_BATCH              Inference batch size (default: 16)");
    Console.WriteLine();
    Console.WriteLine("API ENDPOINTS:");
    Console.WriteLine("  GET  /healthz          Health check");
    Console.WriteLine("  POST /embed            Embed text(s)");
    Console.WriteLine();
    Console.WriteLine("For complete documentation, see INSTRUCTIONS.md");
    return;
}

if (args.Length > 0 && args[0] == "--text")
{
    var text = string.Join(" ", args.Skip(1));
    if (string.IsNullOrWhiteSpace(text))
    {
        Console.WriteLine("Error: No text provided. Usage: --text \"your text here\"");
        return;
    }
    
    try
    {
        using var engine = new EmbeddingEngine(cfg);
        var res = engine.EmbedBatch(new[]{ text });
        Console.WriteLine(JsonSerializer.Serialize(new {
            dimension = res.Dimension,
            vector = res.Vectors[0]
        }, new JsonSerializerOptions { WriteIndented = true }));
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error: {ex.Message}");
        Environment.Exit(1);
    }
    return;
}

if (args.Length > 0 && args[0] == "--health")
{
    try
    {
        using var engine = new EmbeddingEngine(cfg);
        Console.WriteLine("healthy");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"unhealthy: {ex.Message}");
        Environment.Exit(1);
    }
    return;
}

// Only proceed to web app if no CLI commands were handled
var builder = WebApplication.CreateBuilder(Array.Empty<string>()); // Don't pass args to avoid interference
builder.WebHost.UseUrls($"http://{cfg.ListenHost}:{cfg.ListenPort}");

// Add CORS support for web interface
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// Enable CORS
app.UseCors();

EmbeddingEngine? engineSingleton = null;
EmbeddingEngine GetEngine() => engineSingleton ??= new EmbeddingEngine(cfg);

app.MapGet("/healthz", () =>
{
    try {
        var eng = GetEngine();
        var mock = Environment.GetEnvironmentVariable("EMB_MOCK") == "1";
        return Results.Json(new { status = "ok", model = cfg.ModelFile, pid = Environment.ProcessId, mock, dimension = eng.Dimension, executionProvider = cfg.ExecutionProvider });
    } catch (Exception ex) {
        return Results.Json(new { status="error", error=ex.Message });
    }
});

app.MapPost("/embed", async (HttpContext http) =>
{
    using var doc = await JsonDocument.ParseAsync(http.Request.Body);
    string? single = null; List<string>? batch = null;
    if (doc.RootElement.TryGetProperty("text", out var tEl) && tEl.ValueKind == JsonValueKind.String)
        single = tEl.GetString();
    if (doc.RootElement.TryGetProperty("texts", out var tsEl) && tsEl.ValueKind == JsonValueKind.Array)
        batch = tsEl.EnumerateArray().Where(e=>e.ValueKind==JsonValueKind.String).Select(e=>e.GetString() ?? "").ToList();
    var inputs = batch ?? (single is not null ? new List<string>{ single } : new List<string>());
    if (inputs.Count == 0) return Results.BadRequest(new { error="Provide 'text' or 'texts'" });
    var eng = GetEngine();
    var result = eng.EmbedBatch(inputs);
    var resp = new EmbedResponse(result.Dimension, inputs.Count, result.Vectors, result.TokensPerInput, cfg.ModelFile, cfg.UseMeanPooling?"mean":"cls", cfg.L2Normalize);
    return Results.Json(resp);
});

app.Run();

// Needed for WebApplicationFactory (tests)
public partial class Program { }

