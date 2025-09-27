#!/usr/bin/env python3
"""
Script to process documents and save extracted content to files.
"""

import os
import json
from datetime import datetime
from pathlib import Path
import sys

# Add the ai-gateway src path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-gateway', 'src'))

try:
    from processors.document_processor import DocumentProcessor
except ImportError:
    try:
        # Alternative import if running from different location
        import sys
        sys.path.insert(0, 'ai-gateway/src')
        from processors.document_processor import DocumentProcessor
    except ImportError as e:
        print(f"❌ Error importing DocumentProcessor: {e}")
        print("Make sure you're running from the correct directory")
        sys.exit(1)

def save_extracted_content(file_path, output_dir=None):
    """
    Process a document and save the extracted content to files.
    
    Args:
        file_path (str): Path to the document to process
        output_dir (str): Directory to save extracted content (optional)
    
    Returns:
        dict: Processing results with saved file paths
    """
    if output_dir is None:
        # Create output directory based on input filename
        base_name = Path(file_path).stem
        output_dir = f"extracted_content_{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Process the document
    processor = DocumentProcessor()
    result = processor.process_document(file_path)
    
    saved_files = {}
    
    if result['status'] == 'success':
        # Save full text
        full_text_file = os.path.join(output_dir, "full_text.txt")
        with open(full_text_file, 'w', encoding='utf-8') as f:
            f.write(result['full_text'])
        saved_files['full_text'] = full_text_file
        
        # Save page-by-page text
        if result.get('pages'):
            pages_dir = os.path.join(output_dir, "pages")
            os.makedirs(pages_dir, exist_ok=True)
            
            for i, page_data in enumerate(result['pages'], 1):
                page_file = os.path.join(pages_dir, f"page_{i:03d}.txt")
                with open(page_file, 'w', encoding='utf-8') as f:
                    # Handle different page data structures
                    if isinstance(page_data, dict):
                        f.write(page_data.get('text', str(page_data)))
                    else:
                        f.write(str(page_data))
                saved_files[f'page_{i}'] = page_file
        
        # Save metadata and analysis
        metadata_file = os.path.join(output_dir, "metadata.json")
        metadata = {
            'source_file': file_path,
            'processing_timestamp': datetime.now().isoformat(),
            'total_pages': result.get('total_pages', 0),
            'total_characters': result.get('total_characters', 0),
            'file_size': result.get('file_size', 0),
            'format': result.get('format', 'unknown')
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        saved_files['metadata'] = metadata_file
        
        # Save Polars DataFrame as CSV if available
        if result.get('pages_dataframe') is not None:
            try:
                csv_file = os.path.join(output_dir, "analysis.csv")
                result['pages_dataframe'].write_csv(csv_file)
                saved_files['analysis_csv'] = csv_file
            except Exception as csv_error:
                # If CSV export fails, save as JSON instead
                json_file = os.path.join(output_dir, "analysis.json")
                df_dict = result['pages_dataframe'].to_dict(as_series=False)
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(df_dict, f, indent=2)
                saved_files['analysis_json'] = json_file
                print(f"⚠️  CSV export failed, saved as JSON instead: {csv_error}")
        
        print(f"✅ Content extracted and saved to: {output_dir}")
        print(f"   📄 Full text: {saved_files['full_text']}")
        print(f"   📊 Analysis: {saved_files.get('analysis_csv') or saved_files.get('analysis_json', 'N/A')}")
        print(f"   📋 Metadata: {saved_files['metadata']}")
        if result.get('pages'):
            print(f"   📑 Pages: {len(result['pages'])} files in {pages_dir}")
        
        return {
            'status': 'success',
            'output_directory': output_dir,
            'saved_files': saved_files,
            'total_pages': result.get('total_pages', 0),
            'total_characters': result.get('total_characters', 0)
        }
    
    else:
        print(f"❌ Failed to process document: {result.get('error', 'Unknown error')}")
        return {
            'status': 'failed',
            'error': result.get('error', 'Unknown error')
        }

def main():
    """Main function to handle command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python save_extracted_content.py <document_path> [output_dir]")
        print("\nExample:")
        print(r'  python save_extracted_content.py "C:\Users\gargs\Downloads\4722_Math_model_paper.docx (10).pdf"')
        return
    
    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        result = save_extracted_content(file_path, output_dir)
        
        if result['status'] == 'success':
            print(f"\n🎉 Successfully processed document!")
            print(f"   📂 Output directory: {result['output_directory']}")
            print(f"   📄 Total pages: {result['total_pages']}")
            print(f"   📊 Total characters: {result['total_characters']:,}")
        
    except Exception as e:
        print(f"❌ Error processing document: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()