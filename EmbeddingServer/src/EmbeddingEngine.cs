using Microsoft.ML.OnnxRuntime;
using Microsoft.ML.OnnxRuntime.Tensors;
using System.Numerics;

namespace EmbeddingServer;

public class EmbeddingEngine : IDisposable
{
    private readonly InferenceSession? _session;
    private readonly ServerConfig _cfg;
    private readonly Vocabulary _vocab;
    private readonly FullTokenizer _tokenizer;
    private readonly int _hiddenSize;
    private readonly bool _mock;
    public int Dimension => _hiddenSize;

    public EmbeddingEngine(ServerConfig cfg)
    {
        _cfg = cfg;
        _mock = (Environment.GetEnvironmentVariable("EMB_MOCK") == "1");
        if (_mock)
        {
            _hiddenSize = int.TryParse(Environment.GetEnvironmentVariable("EMB_MOCK_DIM"), out var d) ? d : 384;
            // Create mock vocab and tokenizer for testing
            var mockVocabPath = Path.Combine(cfg.ModelDir, "vocab.txt");
            if (File.Exists(mockVocabPath))
            {
                _vocab = Vocabulary.Load(mockVocabPath);
            }
            else
            {
                // Use a default vocab if none exists
                throw new FileNotFoundException("vocab.txt required for mock mode", mockVocabPath);
            }
            _tokenizer = new FullTokenizer(_vocab, doLower: true);
            _session = null;
            return;
        }
        var modelPath = Path.Combine(cfg.ModelDir, cfg.QuantizedModelFile ?? cfg.ModelFile);
        if (!File.Exists(modelPath)) throw new FileNotFoundException("Model file not found", modelPath);
        
        // Load vocabulary and tokenizer
        var vocabPath = Path.Combine(cfg.ModelDir, "vocab.txt");
        _vocab = Vocabulary.Load(vocabPath);
        _tokenizer = new FullTokenizer(_vocab, doLower: true);
    var opts = new Microsoft.ML.OnnxRuntime.SessionOptions();
        opts.LogSeverityLevel = OrtLoggingLevel.ORT_LOGGING_LEVEL_WARNING;
        if (cfg.ExecutionProvider.Equals("dml", StringComparison.OrdinalIgnoreCase))
        {
            try { opts.AppendExecutionProvider_DML(); } catch { /* fallback silently */ }
        }
        _session = new InferenceSession(modelPath, opts);
        var firstOut = _session.OutputMetadata.First();
        var dims = firstOut.Value.Dimensions;
        _hiddenSize = dims.Last();
    }

    public record EmbeddingResult(float[][] Vectors, int Dimension, int[] TokensPerInput);

    public EmbeddingResult EmbedBatch(IEnumerable<string> inputs)
    {
        var inputList = inputs.ToList();
        if (_mock)
        {
            var rnd = new Random(42);
            var vecs = new float[inputList.Count][];
            var tokensPer = new int[inputList.Count];
            for (int i=0;i<inputList.Count;i++)
            {
                // pseudo token count approx by splitting whitespace
                tokensPer[i] = Math.Min(_cfg.MaxSequenceLength, (inputList[i].Split(' ', StringSplitOptions.RemoveEmptyEntries).Length + 2));
                var v = new float[_hiddenSize];
                // deterministic-ish hashing
                int hash = inputList[i].GetHashCode();
                var local = new Random(hash);
                for (int d=0; d<_hiddenSize; d++) v[d] = (float)(local.NextDouble() - 0.5);
                if (_cfg.L2Normalize)
                {
                    double norm = 0; for (int d=0; d<_hiddenSize; d++) norm += v[d]*v[d];
                    norm = Math.Sqrt(norm) + 1e-12; for (int d=0; d<_hiddenSize; d++) v[d] = (float)(v[d]/norm);
                }
                vecs[i] = v;
            }
            return new EmbeddingResult(vecs, _hiddenSize, tokensPer);
        }
        if (_session is null) throw new InvalidOperationException("Engine misconfigured.");
        
        var tokenIdsList = new List<List<int>>(inputList.Count);
        int maxSeq = _cfg.MaxSequenceLength;
        
        // Tokenize all input texts
        foreach (var text in inputList)
            tokenIdsList.Add(_tokenizer.Encode(text, maxSeq));
        
        int actualMax = tokenIdsList.Max(l => l.Count);
        var inputIds = new DenseTensor<long>(new[] { inputList.Count, actualMax });
        var attention = new DenseTensor<long>(new[] { inputList.Count, actualMax });
        
        int padToken = _vocab.PAD;
        
        for (int i=0;i<inputList.Count;i++)
        {
            var row = tokenIdsList[i];
            for (int j=0;j<actualMax;j++)
            {
                long val = j < row.Count ? row[j] : padToken;
                inputIds[i, j] = val;
                attention[i, j] = j < row.Count ? 1 : 0;
            }
        }
        var inputsOrt = new List<Microsoft.ML.OnnxRuntime.NamedOnnxValue>
        {
            Microsoft.ML.OnnxRuntime.NamedOnnxValue.CreateFromTensor("input_ids", inputIds),
            Microsoft.ML.OnnxRuntime.NamedOnnxValue.CreateFromTensor("attention_mask", attention)
        };
        if (_session.InputMetadata.ContainsKey("token_type_ids"))
        {
            var typeIds = new DenseTensor<long>(new[] {inputList.Count, actualMax});
            inputsOrt.Add(Microsoft.ML.OnnxRuntime.NamedOnnxValue.CreateFromTensor("token_type_ids", typeIds));
        }
        using var results = _session.Run(inputsOrt);
        var lastHidden = results.First().AsTensor<float>();
        var vectors = new float[inputList.Count][];
        for (int b=0;b<inputList.Count;b++)
        {
            var sum = new float[_hiddenSize];
            int validCount = 0;
            for (int t=0;t<actualMax;t++)
            {
                if (attention[b,t] == 0) continue;
                validCount++;
                int baseIdx = (b * actualMax + t) * _hiddenSize;
                for (int h=0;h<_hiddenSize;h++)
                {
                    sum[h] += lastHidden.GetValue(baseIdx + h);
                }
            }
            for (int h=0; h<_hiddenSize; h++) sum[h] /= Math.Max(1, validCount);
            if (_cfg.L2Normalize)
            {
                double norm = 0;
                for (int h=0; h<_hiddenSize; h++) norm += sum[h]*sum[h];
                norm = Math.Sqrt(norm) + 1e-12;
                for (int h=0; h<_hiddenSize; h++) sum[h] = (float)(sum[h]/norm);
            }
            vectors[b] = sum;
        }
        return new EmbeddingResult(vectors, _hiddenSize, tokenIdsList.Select(l=>l.Count).ToArray());
    }

    public void Dispose() 
    {
        _session?.Dispose();
    }
}
