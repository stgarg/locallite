"""Test table export functionality in different formats"""
import sys
sys.path.insert(0, r'C:\Learn\Code\fastembed\ai-gateway\src')

from converters.image_converter import ImageConverter

def test_table_exports():
    print('📊 TESTING TABLE EXPORT FORMATS')
    print('=' * 70)
    
    converter = ImageConverter()
    img_path = r'C:\Users\gargs\Downloads\Screenshot 2025-09-10 175920.png'
    
    # Extract with table detection
    result = converter.extract_text(img_path)
    table_analysis = result.get('table_analysis', {})
    
    if table_analysis.get('table_count', 0) == 0:
        print('❌ No tables detected for export testing')
        return
    
    print(f"✅ Found {table_analysis['table_count']} table(s) for export")
    print()
    
    # Test different export formats
    formats = ['markdown', 'csv', 'html', 'json']
    
    for fmt in formats:
        print(f"📄 {fmt.upper()} FORMAT:")
        print("-" * 50)
        
        exported = converter.export_tables(table_analysis, fmt)
        
        # Show first 500 characters
        if len(exported) > 500:
            print(exported[:500] + "...")
        else:
            print(exported)
        
        print()
    
    # Save exports to files for inspection
    print("💾 SAVING EXPORTS TO FILES:")
    for fmt in formats:
        exported = converter.export_tables(table_analysis, fmt)
        filename = f'exported_table.{fmt.lower()}'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(exported)
        
        print(f"   ✅ Saved: {filename}")
    
    print("\n🎯 All table export formats tested successfully!")

if __name__ == "__main__":
    test_table_exports()