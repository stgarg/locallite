using System.Collections.Concurrent;

namespace EmbeddingServer;

public class Vocabulary
{
    private readonly Dictionary<string,int> _token2Id;
    public readonly string[] Id2Token;
    public int Count => _token2Id.Count;
    public int CLS => _token2Id.GetValueOrDefault("[CLS]", _token2Id.GetValueOrDefault("<s>"));
    public int SEP => _token2Id.GetValueOrDefault("[SEP]", _token2Id.GetValueOrDefault("</s>"));
    public int PAD => _token2Id.GetValueOrDefault("[PAD]", _token2Id.GetValueOrDefault("<pad>"));
    public int UNK => _token2Id.GetValueOrDefault("[UNK]", _token2Id.GetValueOrDefault("<unk>"));

    private Vocabulary(Dictionary<string,int> map, string[] reverse) { _token2Id = map; Id2Token = reverse; }

    public static Vocabulary Load(string vocabPath)
    {
        var lines = File.ReadAllLines(vocabPath);
        var map = new Dictionary<string,int>(lines.Length);
        for (int i=0;i<lines.Length;i++) map[lines[i]] = i;
        return new Vocabulary(map, lines);
    }

    public int this[string token] => _token2Id.TryGetValue(token, out var id) ? id : UNK;
}
