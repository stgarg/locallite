"""
Website Content Processor for Knowledge Base
Handles educational websites like Hamel's blog with hierarchical structure
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
from typing import Dict, List, Tuple, Optional

class WebsiteProcessor:
    def __init__(self, gemma_base_url: str = "http://localhost:8000"):
        self.gemma_base_url = gemma_base_url
        self.session = requests.Session()
        # Add a user agent to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Educational Content Processor 1.0'
        })
    
    def extract_website_content(self, url: str) -> Dict:
        """
        Extract structured content from educational website
        """
        print(f"Extracting content from: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['nav', 'footer', 'aside', 'script', 'style']):
                element.decompose()
            
            # Extract main content
            main_content = self._find_main_content(soup)
            
            # Analyze structure
            structure = self._analyze_content_structure(main_content, url)
            
            return {
                'url': url,
                'title': self._extract_title(soup),
                'main_content': main_content,
                'structure': structure,
                'metadata': self._extract_metadata(soup, url),
                'extraction_time': time.time()
            }
            
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None
    
    def _find_main_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Find the main article content"""
        # Common main content selectors
        selectors = ['main', 'article', '[role="main"]', '.content', '.post-content']
        
        for selector in selectors:
            main = soup.select_one(selector)
            if main:
                return main
        
        # Fallback: find largest text block
        body = soup.find('body')
        return body if body else soup
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract document title"""
        # Try multiple title sources
        title_sources = [
            soup.select_one('h1'),
            soup.select_one('title'),
            soup.select_one('[property="og:title"]'),
            soup.select_one('meta[name="title"]')
        ]
        
        for source in title_sources:
            if source:
                if source.name == 'meta':
                    return source.get('content', '').strip()
                return source.get_text().strip()
        
        return "Untitled Document"
    
    def _analyze_content_structure(self, content: BeautifulSoup, url: str) -> Dict:
        """Analyze hierarchical structure of content"""
        structure = {
            'sections': [],
            'qa_pairs': [],
            'code_blocks': [],
            'links': [],
            'estimated_tokens': 0
        }
        
        # Find sections by headings
        headings = content.find_all(['h1', 'h2', 'h3', 'h4'])
        current_section = None
        
        for heading in headings:
            # Extract level from heading tag name (h1, h2, etc.)
            if heading.name and len(heading.name) >= 2 and heading.name[1].isdigit():
                level = int(heading.name[1])  # h1 -> 1, h2 -> 2, etc.
            else:
                continue  # Skip invalid headings
            title = heading.get_text().strip()
            
            # Get content until next heading of same or higher level
            section_content = self._get_section_content(heading)
            
            section = {
                'level': level,
                'title': title,
                'content': section_content,
                'element': heading,
                'tokens': len(section_content.split()) * 1.3  # rough token estimate
            }
            
            # Detect Q&A patterns in this section
            qa_pairs = self._extract_qa_pairs(section_content, title)
            section['qa_pairs'] = qa_pairs
            
            structure['sections'].append(section)
            structure['qa_pairs'].extend(qa_pairs)
        
        # Extract code blocks
        code_blocks = content.find_all(['code', 'pre'])
        for code in code_blocks:
            structure['code_blocks'].append(code.get_text().strip())
        
        # Extract internal links
        links = content.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            full_url = urljoin(url, href)
            structure['links'].append({
                'text': link.get_text().strip(),
                'url': full_url,
                'internal': urlparse(url).netloc == urlparse(full_url).netloc
            })
        
        # Estimate total tokens
        full_text = content.get_text()
        structure['estimated_tokens'] = len(full_text.split()) * 1.3
        
        return structure
    
    def _get_section_content(self, heading) -> str:
        """Get all content from heading until next heading of same or higher level"""
        content_parts = []
        current = heading.next_sibling
        
        # Safe heading level extraction
        if heading.name and len(heading.name) >= 2 and heading.name[1].isdigit():
            heading_level = int(heading.name[1])
        else:
            return ""  # Invalid heading
        
        while current:
            if hasattr(current, 'name') and current.name:
                # Stop at next heading of same or higher level
                if current.name.startswith('h') and len(current.name) >= 2 and current.name[1].isdigit():
                    next_level = int(current.name[1])
                    if next_level <= heading_level:
                        break
                
                # Collect text content
                if hasattr(current, 'get_text'):
                    text = current.get_text().strip()
                    if text:
                        content_parts.append(text)
            
            current = current.next_sibling
        
        return '\n\n'.join(content_parts)
    
    def _extract_qa_pairs(self, content: str, section_title: str) -> List[Dict]:
        """Extract Q&A pairs from section content"""
        qa_pairs = []
        
        # Pattern 1: Explicit Q: and A: patterns
        lines = content.split('\n')
        current_q = None
        current_a = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Question patterns
            if (line.startswith('Q:') or line.startswith('Question:') or 
                line.endswith('?') and len(line.split()) <= 20):
                
                # Save previous Q&A if exists
                if current_q and current_a:
                    qa_pairs.append({
                        'question': current_q,
                        'answer': ' '.join(current_a).strip(),
                        'section': section_title
                    })
                
                current_q = line.replace('Q:', '').replace('Question:', '').strip()
                current_a = []
            
            # Answer patterns
            elif line.startswith('A:') or line.startswith('Answer:'):
                current_a.append(line.replace('A:', '').replace('Answer:', '').strip())
            
            # Continue answer
            elif current_q and line:
                current_a.append(line)
        
        # Save final Q&A
        if current_q and current_a:
            qa_pairs.append({
                'question': current_q,
                'answer': ' '.join(current_a).strip(),
                'section': section_title
            })
        
        return qa_pairs
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract document metadata"""
        metadata = {
            'url': url,
            'domain': urlparse(url).netloc,
            'extraction_time': time.time()
        }
        
        # Meta tags
        meta_tags = {
            'author': ['meta[name="author"]', 'meta[property="article:author"]'],
            'description': ['meta[name="description"]', 'meta[property="og:description"]'],
            'keywords': ['meta[name="keywords"]'],
            'published': ['meta[property="article:published_time"]', 'meta[name="date"]'],
            'modified': ['meta[property="article:modified_time"]']
        }
        
        for key, selectors in meta_tags.items():
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    metadata[key] = element.get('content', '').strip()
                    break
        
        return metadata
    
    def chunk_website_content(self, website_data: Dict) -> List[Dict]:
        """
        Create chunks from website content using section-based approach
        """
        chunks = []
        
        if not website_data or 'structure' not in website_data:
            return chunks
        
        url = website_data['url']
        title = website_data['title']
        structure = website_data['structure']
        metadata = website_data.get('metadata', {})
        
        # Create document-level chunk for overall summary
        full_content = website_data['main_content'].get_text() if website_data['main_content'] else ""
        
        document_chunk = {
            'chunk_id': f"{self._url_to_id(url)}_document",
            'chunk_type': 'document_summary',
            'source_url': url,
            'source_type': 'website',
            'document_title': title,
            'raw_content': full_content[:5000],  # Truncate for processing
            'section_count': len(structure['sections']),
            'qa_count': len(structure['qa_pairs']),
            'estimated_tokens': structure['estimated_tokens'],
            'metadata': metadata
        }
        chunks.append(document_chunk)
        
        # Create section-based chunks
        for i, section in enumerate(structure['sections']):
            if len(section['content']) < 100:  # Skip tiny sections
                continue
            
            section_chunk = {
                'chunk_id': f"{self._url_to_id(url)}_section_{i+1}",
                'chunk_type': 'section',
                'source_url': url,
                'source_type': 'website',
                'document_title': title,
                'section_title': section['title'],
                'section_level': section['level'],
                'section_number': i + 1,
                'raw_content': section['content'],
                'qa_pairs': section.get('qa_pairs', []),
                'estimated_tokens': section['tokens'],
                'metadata': metadata
            }
            chunks.append(section_chunk)
        
        print(f"Created {len(chunks)} chunks from {url}")
        return chunks
    
    def _url_to_id(self, url: str) -> str:
        """Convert URL to safe chunk ID"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        path = parsed.path.strip('/').replace('/', '_')
        return f"{domain}_{path}"
    
    def analyze_with_gemma(self, chunks: List[Dict]) -> List[Dict]:
        """
        Analyze chunks using Gemma with web-specific prompts
        """
        analyzed_chunks = []
        
        for chunk in chunks:
            print(f"Analyzing chunk: {chunk['chunk_id']}")
            
            try:
                if chunk['chunk_type'] == 'document_summary':
                    analysis = self._analyze_document_with_gemma(chunk)
                else:
                    analysis = self._analyze_section_with_gemma(chunk)
                
                # Add Gemma analysis to chunk
                chunk.update(analysis)
                analyzed_chunks.append(chunk)
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error analyzing chunk {chunk['chunk_id']}: {str(e)}")
                analyzed_chunks.append(chunk)  # Keep original chunk
        
        return analyzed_chunks
    
    def _analyze_document_with_gemma(self, chunk: Dict) -> Dict:
        """Analyze document-level content with Gemma"""
        prompt = f"""
Analyze this educational website for knowledge base indexing.

Title: {chunk['document_title']}
URL: {chunk['source_url']}
Sections: {chunk['section_count']}
Q&As: {chunk['qa_count']}

Content: {chunk['raw_content'][:3000]}

Provide:
1. Document Purpose (1-2 sentences)
2. Target Audience (who should read this?)
3. Key Learning Outcomes (3-5 main topics covered)
4. Difficulty Level (beginner/intermediate/advanced)
5. Prerequisites (background knowledge needed)
6. Search Keywords (10+ terms for discovery)

Format as JSON with these keys: purpose, audience, outcomes, difficulty, prerequisites, keywords
"""
        
        return self._call_gemma(prompt, "document_analysis")
    
    def _analyze_section_with_gemma(self, chunk: Dict) -> Dict:
        """Analyze section-level content with Gemma"""
        prompt = f"""
Analyze this section from an educational website.

Section: {chunk['section_title']}
Level: H{chunk['section_level']}
Q&As: {len(chunk.get('qa_pairs', []))}

Content: {chunk['raw_content'][:2000]}

Provide:
1. Section Summary (2-3 sentences)
2. Key Concepts (main topics introduced)
3. Practical Advice (actionable recommendations)
4. Related Topics (what this connects to)
5. Search Terms (keywords for finding this section)

Format as JSON with keys: summary, concepts, advice, related, terms
"""
        
        return self._call_gemma(prompt, "section_analysis")
    
    def _call_gemma(self, prompt: str, analysis_type: str) -> Dict:
        """Call Gemma API for analysis"""
        try:
            response = self.session.post(
                f"{self.gemma_base_url}/chat",
                json={
                    "message": prompt,
                    "temperature": 0.3,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                gemma_response = result.get('response', '{}')
                
                # Try to parse as JSON
                try:
                    analysis = json.loads(gemma_response)
                    return {
                        'gemma_analysis': analysis,
                        'analysis_type': analysis_type,
                        'analysis_success': True
                    }
                except json.JSONDecodeError:
                    return {
                        'gemma_analysis': {'raw_response': gemma_response},
                        'analysis_type': analysis_type,
                        'analysis_success': False
                    }
            else:
                print(f"Gemma API error: {response.status_code}")
                return {'analysis_success': False, 'error': f'API error {response.status_code}'}
                
        except Exception as e:
            print(f"Gemma analysis error: {str(e)}")
            return {'analysis_success': False, 'error': str(e)}

def test_website_processor():
    """Test the website processor"""
    processor = WebsiteProcessor()
    
    # Test with Hamel's blog
    url = "https://hamel.dev/blog/posts/evals-faq/"
    
    print("Testing Website Processor")
    print("=" * 40)
    
    # Step 1: Extract content
    print("1. Extracting website content...")
    website_data = processor.extract_website_content(url)
    
    if website_data:
        print(f"   Title: {website_data['title']}")
        print(f"   Sections: {len(website_data['structure']['sections'])}")
        print(f"   Q&As: {len(website_data['structure']['qa_pairs'])}")
        print(f"   Estimated tokens: {website_data['structure']['estimated_tokens']:.0f}")
        
        # Step 2: Create chunks
        print("\n2. Creating chunks...")
        chunks = processor.chunk_website_content(website_data)
        print(f"   Created {len(chunks)} chunks")
        
        # Show chunk summary
        for chunk in chunks[:3]:  # Show first 3
            print(f"   - {chunk['chunk_id']}: {chunk['chunk_type']}")
        
        # Step 3: Test Gemma analysis (if available)
        print("\n3. Testing Gemma analysis...")
        try:
            analyzed_chunks = processor.analyze_with_gemma(chunks[:1])  # Test with first chunk
            if analyzed_chunks and analyzed_chunks[0].get('analysis_success'):
                print("   Gemma analysis: SUCCESS")
                analysis = analyzed_chunks[0].get('gemma_analysis', {})
                if 'purpose' in analysis:
                    print(f"   Purpose: {analysis['purpose'][:100]}...")
            else:
                print("   Gemma analysis: FAILED (API not available)")
        except Exception as e:
            print(f"   Gemma analysis: ERROR - {str(e)}")
        
        return website_data, chunks
    
    else:
        print("Failed to extract website content")
        return None, None

if __name__ == "__main__":
    test_website_processor()