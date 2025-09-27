"""
Website Processing Strategy for Knowledge Base Creation
Handles websites like Hamel's blog with hierarchical Q&A structure
"""
import requests
from pathlib import Path
from urllib.parse import urlparse
import json
import re

def analyze_website_structure(url):
    """
    Analyze website content structure for optimal chunking
    Based on analysis of https://hamel.dev/blog/posts/evals-faq/
    """
    print(f'🌐 WEBSITE PROCESSING STRATEGY')
    print('=' * 60)
    print(f'Target: {url}')
    
    # Website characteristics we discovered
    website_analysis = {
        'content_type': 'educational_blog_post',
        'structure_type': 'hierarchical_faq',
        'total_sections': 7,
        'total_qa_pairs': 41,
        'estimated_tokens': 35000,  # Very long content
        'chunking_strategy': 'section_based_with_qa_pairs',
        
        'content_hierarchy': {
            'document_level': 'Complete FAQ about AI Evals',
            'section_level': 'Getting Started, Error Analysis, etc.',
            'subsection_level': 'Individual Q&A pairs',
            'detail_level': 'Explanations, examples, code snippets'
        },
        
        'processing_approach': {
            'method': 'hierarchical_chunking',
            'chunk_boundaries': 'respect_qa_structure',
            'context_preservation': 'maintain_section_relationships',
            'gemma_analysis': 'per_section_and_overall_summary'
        }
    }
    
    return website_analysis

def design_website_chunking_strategy():
    """Design chunking strategy specifically for website content"""
    print(f'\n📋 WEBSITE CHUNKING STRATEGY')
    print('=' * 50)
    
    chunking_strategies = {
        '1. Section-Based Chunking (Recommended)': {
            'description': 'Chunk by major sections (Getting Started, Error Analysis, etc.)',
            'chunk_size': '4,000-8,000 tokens per section',
            'advantages': [
                'Preserves topical coherence',
                'Natural content boundaries', 
                'Manageable for Gemma analysis',
                'Good for concept-based search'
            ],
            'chunk_example': {
                'chunk_id': 'hamel_evals_faq_section_1',
                'title': 'Getting Started & Fundamentals',
                'content': 'Contains 6 Q&A pairs about LLM eval basics',
                'estimated_tokens': 6500,
                'context': 'Part of comprehensive AI evals FAQ'
            }
        },
        
        '2. Q&A Pair Chunking': {
            'description': 'Each individual Q&A as separate chunk',
            'chunk_size': '500-1,500 tokens per Q&A',
            'advantages': [
                'Precise granularity for search',
                'Easy to update individual answers',
                'Good for specific question matching'
            ],
            'disadvantages': [
                'Loses section context',
                'More chunks to manage (41 chunks)',
                'May fragment related concepts'
            ]
        },
        
        '3. Hybrid Approach (Best of Both)': {
            'description': 'Section-level chunks + Q&A metadata',
            'implementation': [
                'Primary chunks: 7 sections',
                'Metadata: Individual Q&A topics and keywords',
                'Cross-references: Related questions within/across sections'
            ]
        }
    }
    
    for strategy, details in chunking_strategies.items():
        print(f'\n{strategy}:')
        print(f'   📝 {details["description"]}')
        if 'chunk_size' in details:
            print(f'   📐 Size: {details["chunk_size"]}')
        if 'advantages' in details:
            print(f'   ✅ Advantages:')
            for adv in details['advantages']:
                print(f'      • {adv}')
        if 'disadvantages' in details:
            print(f'   ❌ Disadvantages:')
            for dis in details['disadvantages']:
                print(f'      • {dis}')

def design_gemma_prompts_for_websites():
    """Design Gemma prompts specifically for website content analysis"""
    print(f'\n🧠 GEMMA WEBSITE ANALYSIS PROMPTS')  
    print('=' * 50)
    
    prompts = {
        'section_analysis_prompt': """
Analyze this section from an educational website about AI evaluations.

Content: {section_content}
Source: {source_url} 
Section: {section_title}

Provide:
1. Section Summary: What does this section teach?
2. Key Concepts: Main topics and terminology introduced
3. Practical Advice: Actionable recommendations provided
4. Prerequisites: What should readers know before this section?
5. Related Topics: What other concepts does this connect to?
6. Search Keywords: Terms someone might search to find this content

Focus on making the content searchable for concept-based queries.
""",

        'document_level_prompt': """
Analyze this complete educational resource about AI evaluations.

Document: {document_title}
Source: {source_url}
Sections: {section_list}

Provide:
1. Document Purpose: What problem does this solve?
2. Target Audience: Who should read this?
3. Learning Progression: How do sections build on each other?
4. Key Frameworks: Main methodologies or approaches taught
5. Practical Applications: Real-world use cases covered
6. Knowledge Prerequisites: What background knowledge is assumed?
7. Related Resources: What other content would complement this?

Create an executive summary suitable for knowledge base discovery.
""",

        'qa_extraction_prompt': """
Extract and enhance Q&A pairs from this website section.

Content: {section_content}

For each Q&A pair found:
1. Question: The original question (cleaned up)
2. Answer Summary: 2-3 sentence summary of the answer
3. Key Points: Bullet points of main advice/information
4. Context: Why this question matters
5. Related Questions: Other questions this answer touches on
6. Searchable Terms: Keywords for finding this Q&A

Make each Q&A pair independently understandable and searchable.
"""
    }
    
    for prompt_name, prompt_text in prompts.items():
        print(f'\n📝 {prompt_name.upper()}:')
        print('-' * 30)
        print(prompt_text.strip())

def design_lancedb_schema_for_websites():
    """Design LanceDB schema optimized for website content"""
    print(f'\n💾 LANCEDB SCHEMA FOR WEBSITE CONTENT')
    print('=' * 50)
    
    schema = {
        'chunk_id': 'hamel_evals_faq_section_1',
        'source_url': 'https://hamel.dev/blog/posts/evals-faq/',
        'source_type': 'website',
        'content_type': 'educational_blog_post',
        'domain': 'ai_evaluations',
        
        # Hierarchical structure
        'document_title': 'Frequently Asked Questions About AI Evals',
        'section_title': 'Getting Started & Fundamentals', 
        'section_number': 1,
        'subsection_count': 6,
        
        # Original content
        'raw_html': '<h1>Getting Started...</h1>...',
        'clean_text': 'Getting Started & Fundamentals...',
        'qa_pairs': [
            {
                'question': 'What are LLM Evals?',
                'answer': 'LLM evaluations are...',
                'keywords': ['llm', 'evaluation', 'testing']
            }
        ],
        
        # Gemma analysis
        'gemma_summary': 'This section introduces fundamental concepts...',
        'key_concepts': ['llm_evaluations', 'error_analysis', 'minimum_viable_setup'],
        'practical_advice': ['Start with error analysis', 'Use domain experts', '...'],
        'target_audience': 'AI engineers and product managers',
        'difficulty_level': 'beginner',
        
        # Context and relationships
        'prerequisites': ['basic_llm_knowledge'],
        'related_sections': ['section_2_error_analysis', 'section_3_methodology'],
        'document_context': 'Comprehensive FAQ covering all aspects of AI evals',
        
        # Embeddings for search
        'content_embedding': [0.1, 0.2, ...],  # Raw content
        'concept_embedding': [0.3, 0.4, ...],  # Gemma summary
        'qa_embeddings': [[0.5, 0.6, ...], [0.7, 0.8, ...]],  # Individual Q&As
        
        # Metadata
        'author': 'Hamel Husain',
        'publication_date': '2025-09-22',
        'word_count': 2500,
        'estimated_reading_time': '10 minutes',
        'processing_timestamp': '2025-09-24T17:00:00',
        'update_frequency': 'occasional'  # vs papers which are static
    }
    
    print('📋 SCHEMA STRUCTURE:')
    for key, value in schema.items():
        if isinstance(value, list) and len(value) > 3:
            print(f'   {key}: [...] ({len(value)} items)')
        elif isinstance(value, str) and len(value) > 50:
            print(f'   {key}: "{value[:50]}..."')
        else:
            print(f'   {key}: {value}')

def compare_website_vs_pdf_processing():
    """Compare website processing with our PDF approach"""
    print(f'\n📊 WEBSITE vs PDF PROCESSING COMPARISON')
    print('=' * 60)
    
    comparison = [
        ['Aspect', 'PDF Processing', 'Website Processing', 'Key Difference'],
        ['─' * 15, '─' * 15, '─' * 18, '─' * 15],
        ['Content Access', 'File upload', 'URL fetching', 'Network vs local'],
        ['Structure', 'Page-based', 'Section/HTML-based', 'Semantic vs physical'],
        ['Content Type', 'Mixed (text+images)', 'Primarily text+links', 'Media richness'],
        ['Updates', 'Static document', 'May change over time', 'Versioning needs'],
        ['Chunking', 'Page boundaries', 'Section/topic boundaries', 'Natural vs arbitrary'],
        ['Context Size', 'Large (9MB PDF)', 'Very large (35K tokens)', 'Similar challenges'],
        ['Navigation', 'Linear pages', 'Hierarchical structure', 'Link relationships'],
        ['Metadata', 'Page numbers', 'URLs, authors, dates', 'Web-specific info']
    ]
    
    for row in comparison:
        print(f'{row[0]:<15} | {row[1]:<15} | {row[2]:<18} | {row[3]:<15}')
    
    print(f'\n🎯 KEY INSIGHTS:')
    print(f'✅ Websites have better semantic structure (sections vs pages)')
    print(f'✅ Natural chunking boundaries (headings, Q&As)')
    print(f'✅ Rich metadata (authors, dates, links)')
    print(f'⚠️ Need to handle dynamic content updates')
    print(f'⚠️ More complex content extraction (HTML parsing)')

def next_implementation_steps():
    """Outline next steps for website processing"""
    print(f'\n🚀 WEBSITE PROCESSING IMPLEMENTATION')
    print('=' * 50)
    
    steps = [
        "1. 📡 CONTENT EXTRACTION:",
        "   → Use requests + BeautifulSoup for HTML parsing",
        "   → Extract main content (filter nav, ads, footers)",
        "   → Preserve structure (headings, links, lists)",
        "   → Handle JavaScript-rendered content if needed",
        "",
        "2. 🏗️ STRUCTURE ANALYSIS:",
        "   → Detect content hierarchy (h1, h2, h3 tags)",
        "   → Identify natural chunk boundaries",
        "   → Extract Q&A pairs, code blocks, examples",
        "   → Map internal links and references",
        "",
        "3. 🧠 GEMMA PROCESSING:",
        "   → Section-level analysis with web-specific prompts",
        "   → Document-level summary including web context",
        "   → Q&A extraction and enhancement",
        "   → Related topic identification",
        "",
        "4. 💾 LANCEDB STORAGE:",
        "   → Web-optimized schema with URL, author, date",
        "   → Hierarchical relationships preservation",
        "   → Update tracking for dynamic content",
        "   → Cross-reference linking for related content"
    ]
    
    for step in steps:
        print(step)

def main():
    """Main analysis function for website processing"""
    print('🌐 WEBSITE PROCESSING STRATEGY DESIGN')
    print('Based on analysis of Hamel\'s AI Evals FAQ\n')
    
    analysis = analyze_website_structure('https://hamel.dev/blog/posts/evals-faq/')
    design_website_chunking_strategy()
    design_gemma_prompts_for_websites()
    design_lancedb_schema_for_websites()
    compare_website_vs_pdf_processing()
    next_implementation_steps()
    
    print(f'\n🎯 CONCLUSION:')
    print(f'Websites like Hamel\'s blog are excellent candidates for our pipeline!')
    print(f'✅ Rich hierarchical structure (better than PDFs)')
    print(f'✅ Natural chunking boundaries (sections, Q&As)')
    print(f'✅ High-quality educational content')
    print(f'✅ Perfect for concept-based search')
    print(f'\nWebsites may actually be EASIER than PDFs to process!')

if __name__ == "__main__":
    main()