using System.Text.Json;
using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;

var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddControllers();
builder.Services.AddSingleton<DocumentProcessor>();

var app = builder.Build();

// Configure pipeline
app.UseRouting();
app.MapControllers();

// Health endpoint
app.MapGet("/healthz", () => new { 
    status = "ok", 
    service = "DocumentProcessor",
    version = "1.0.0",
    formats = new[] { "pdf", "docx", "html", "txt" }
});

// Convert endpoint
app.MapPost("/convert", async ([FromServices] DocumentProcessor processor, ConvertRequest request) =>
{
    try
    {
        var result = await processor.ConvertToMarkdownAsync(request.FilePath, request.Format);
        return Results.Ok(new ConvertResponse 
        { 
            Success = true,
            Markdown = result.Markdown,
            Metadata = result.Metadata,
            ProcessingTimeMs = result.ProcessingTimeMs
        });
    }
    catch (Exception ex)
    {
        return Results.BadRequest(new ConvertResponse 
        { 
            Success = false, 
            Error = ex.Message 
        });
    }
});

app.Run();

// DTOs
public record ConvertRequest(string FilePath, string Format = "auto");
public record ConvertResponse(bool Success, string? Markdown = null, object? Metadata = null, int ProcessingTimeMs = 0, string? Error = null);

// Main processor class
public class DocumentProcessor
{
    public async Task<(string Markdown, object Metadata, int ProcessingTimeMs)> ConvertToMarkdownAsync(string filePath, string format)
    {
        var stopwatch = Stopwatch.StartNew();
        
        var result = format.ToLower() switch
        {
            "pdf" or "auto" when Path.GetExtension(filePath).ToLower() == ".pdf" => await ConvertPdfAsync(filePath),
            "docx" or "auto" when Path.GetExtension(filePath).ToLower() == ".docx" => await ConvertDocxAsync(filePath),
            "html" or "auto" when Path.GetExtension(filePath).ToLower() == ".html" => await ConvertHtmlAsync(filePath),
            "txt" or "auto" when Path.GetExtension(filePath).ToLower() == ".txt" => await ConvertTextAsync(filePath),
            _ => throw new NotSupportedException($"Format {format} not supported")
        };
        
        stopwatch.Stop();
        
        return (result.markdown, result.metadata, (int)stopwatch.ElapsedMilliseconds);
    }
    
    private async Task<(string markdown, object metadata)> ConvertPdfAsync(string filePath)
    {
        // Use iText7 for text-based PDFs (fastest)
        try
        {
            var text = ExtractTextFromPdf(filePath);
            var markdown = ConvertTextToMarkdown(text);
            return (markdown, new { source = "iText7", method = "text_extraction" });
        }
        catch
        {
            // Fallback to Pandoc for complex PDFs
            return await ConvertWithPandocAsync(filePath, "pdf");
        }
    }
    
    private async Task<(string markdown, object metadata)> ConvertDocxAsync(string filePath)
    {
        // Pandoc excels at DOCX conversion
        return await ConvertWithPandocAsync(filePath, "docx");
    }
    
    private async Task<(string markdown, object metadata)> ConvertHtmlAsync(string filePath)
    {
        return await ConvertWithPandocAsync(filePath, "html");
    }
    
    private async Task<(string markdown, object metadata)> ConvertTextAsync(string filePath)
    {
        var text = await File.ReadAllTextAsync(filePath);
        var markdown = ConvertTextToMarkdown(text);
        return (markdown, new { source = "direct", method = "text_processing" });
    }
    
    private async Task<(string markdown, object metadata)> ConvertWithPandocAsync(string filePath, string fromFormat)
    {
        var tempOutput = Path.GetTempFileName() + ".md";
        
        try
        {
            var args = $"-f {fromFormat} -t markdown \"{filePath}\" -o \"{tempOutput}\"";
            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = "pandoc",
                    Arguments = args,
                    UseShellExecute = false,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                }
            };
            
            process.Start();
            await process.WaitForExitAsync();
            
            if (process.ExitCode != 0)
            {
                var error = await process.StandardError.ReadToEndAsync();
                throw new Exception($"Pandoc conversion failed: {error}");
            }
            
            var markdown = await File.ReadAllTextAsync(tempOutput);
            return (markdown, new { source = "pandoc", method = fromFormat });
        }
        finally
        {
            if (File.Exists(tempOutput))
                File.Delete(tempOutput);
        }
    }
    
    private string ExtractTextFromPdf(string filePath)
    {
        // Placeholder - would use iText7
        // using iText.Kernel.Pdf;
        // using iText.Kernel.Utils;
        throw new NotImplementedException("Install iText7 package for PDF support");
    }
    
    private string ConvertTextToMarkdown(string text)
    {
        // Basic text-to-markdown conversion
        var lines = text.Split('\n');
        var markdown = new System.Text.StringBuilder();
        
        foreach (var line in lines)
        {
            var trimmed = line.Trim();
            if (string.IsNullOrEmpty(trimmed)) continue;
            
            // Simple heuristics for markdown conversion
            if (trimmed.All(c => char.IsUpper(c) || char.IsWhiteSpace(c)) && trimmed.Length < 100)
            {
                markdown.AppendLine($"# {trimmed}");
            }
            else if (trimmed.EndsWith(':') && trimmed.Length < 80)
            {
                markdown.AppendLine($"## {trimmed.TrimEnd(':')}");
            }
            else
            {
                markdown.AppendLine(trimmed);
                markdown.AppendLine();
            }
        }
        
        return markdown.ToString();
    }
}