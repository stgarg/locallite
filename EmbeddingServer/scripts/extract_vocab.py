import json
import sys
import os

tokenizer_path = r"C:\Learn\Code\fastembed\EmbeddingServer\models\multilingual-e5-small\tokenizer.json"
vocab_path = r"C:\Learn\Code\fastembed\EmbeddingServer\models\multilingual-e5-small\vocab.txt"

try:
    with open(tokenizer_path, 'r', encoding='utf-8') as f:
        tokenizer_data = json.load(f)
    
    # Extract vocabulary from tokenizer.json
    if 'model' in tokenizer_data and 'vocab' in tokenizer_data['model']:
        vocab_list = tokenizer_data['model']['vocab']
        
        # Create vocab.txt with tokens in order (index = line number)
        with open(vocab_path, 'w', encoding='utf-8') as f:
            for i, (token, score) in enumerate(vocab_list):
                f.write(token + '\n')
        
        print(f"Successfully created vocab.txt with {len(vocab_list)} tokens")
        print(f"First few tokens: {[token for token, _ in vocab_list[:10]]}")
        print(f"Sample tokens: {[token for token, _ in vocab_list[1000:1010]]}")
        
    else:
        print("Error: tokenizer.json does not have expected 'model.vocab' structure")
        print("Available keys:", list(tokenizer_data.keys()))
        if 'model' in tokenizer_data:
            print("Model keys:", list(tokenizer_data['model'].keys()))

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)