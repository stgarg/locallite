using System.Text;
using System.Text.RegularExpressions;

namespace EmbeddingServer;

public class BasicTokenizer
{
    private readonly bool _doLower;
    // Use verbatim strings to avoid escape issues
    private static readonly Regex _whitespace = new(@"\u000C|\s+", RegexOptions.Compiled);
    private static readonly Regex _punct = new(@"([!-/:-@\[-`{-~])", RegexOptions.Compiled); // ASCII punct (escaped [ )
    public BasicTokenizer(bool doLower = true) { _doLower = doLower; }
    public IEnumerable<string> Tokenize(string text)
    {
        if (string.IsNullOrWhiteSpace(text)) yield break;
        text = text.Replace('\u2019', '\'');
        text = _punct.Replace(text, " $1 ");
        foreach (var raw in _whitespace.Split(text))
        {
            var t = raw.Trim();
            if (t.Length == 0) continue;
            if (_doLower) t = t.ToLowerInvariant();
            yield return t;
        }
    }
}

public class WordPieceTokenizer
{
    private readonly Vocabulary _vocab;
    private readonly int _unkId;
    private readonly int _maxCharsPerToken;
    public WordPieceTokenizer(Vocabulary vocab, int maxCharsPerToken = 100) { _vocab = vocab; _unkId = vocab.UNK; _maxCharsPerToken = maxCharsPerToken; }

    public List<int> Tokenize(string token)
    {
        var chars = token.ToCharArray();
        if (chars.Length > _maxCharsPerToken) return new List<int>{ _unkId };
        var subTokens = new List<int>();
        int start = 0;
        while (start < chars.Length)
        {
            int end = chars.Length;
            int cur = -1;
            while (start < end)
            {
                var piece = new string(chars, start, end - start);
                if (start > 0) piece = "##" + piece;
                if (_vocab[piece] != _vocab.UNK) { cur = _vocab[piece]; break; }
                end--;
            }
            if (cur == -1) { subTokens.Add(_unkId); break; }
            subTokens.Add(cur);
            start = end;
        }
        return subTokens;
    }
}

public class FullTokenizer
{
    private readonly BasicTokenizer _basic;
    private readonly WordPieceTokenizer _wordPiece;
    private readonly Vocabulary _vocab;
    public FullTokenizer(Vocabulary vocab, bool doLower=true) { _vocab = vocab; _basic = new BasicTokenizer(doLower); _wordPiece = new WordPieceTokenizer(vocab); }
    public List<int> Encode(string text, int maxSeq, bool addSpecial=true)
    {
        var pieces = new List<int>();
        foreach (var tok in _basic.Tokenize(text))
            pieces.AddRange(_wordPiece.Tokenize(tok));
        if (addSpecial)
        {
            // [CLS] tokens ... [SEP]
            pieces.Insert(0, _vocab.CLS);
            pieces.Add(_vocab.SEP);
        }
        if (pieces.Count > maxSeq) // truncate tail
            pieces = pieces.Take(maxSeq).ToList();
        return pieces;
    }
}
