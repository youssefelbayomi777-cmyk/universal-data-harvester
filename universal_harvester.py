"""
UNIVERSAL DATA HARVESTING UNIT
Advanced hybrid scraping system with AI collaboration
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the Universal Data Harvester"""
    print("🚀 Universal Data Harvesting Unit")
    print("=" * 50)
    print("Advanced Web Scraping with AI Collaboration")
    print("=" * 50)
    
    # Example usage
    config = HarvestConfig(
        target_url="https://example.com",
        use_ai_assistance=True,
        stealth_mode=False,
        output_format="json"
    )
    
    print(f"🎯 Target: {config.target_url}")
    print(f"🤖 AI Assistance: {config.use_ai_assistance}")
    print(f"🛡️ Stealth Mode: {config.stealth_mode}")
    print(f"📊 Output Format: {config.output_format}")
    
    print("\n✅ Universal Data Harvester is ready!")
    print("📖 Documentation: https://github.com/youssefelbayomi777-cmyk/universal-data-harvester")
    print("🚀 Start scraping with your target URL")

if __name__ == "__main__":
    main()

@dataclass
class HarvestConfig:
    """Configuration for data harvesting operations"""
    target_url: str
    max_retries: int = 3
    delay_range: tuple = (1, 3)
    use_ai_assistance: bool = True
    stealth_mode: bool = False
    output_format: str = "json"

class AIAssistant:
    """AI-powered assistant for dynamic scraping logic generation"""
    
    def __init__(self):
        self.patterns = {
            'product_selectors': [
                '.product-item',
                '[data-product]',
                '.product-card',
                '.item'
            ],
            'price_selectors': [
                '.price',
                '[data-price]',
                '.cost',
                '.amount'
            ],
            'image_selectors': [
                'img[src]',
                '.product-image img',
                '[data-image]'
            ]
        }
    
    async def analyze_site_structure(self, html_content: str) -> Dict[str, Any]:
        """Analyze HTML structure and recommend extraction strategy"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Detect site type
        site_indicators = {
            'shopify': 'shopify.com' in html_content.lower(),
            'wordpress': 'wp-content' in html_content.lower(),
            'magento': 'magento' in html_content.lower(),
            'custom': True
        }
        
        # Recommend selectors based on content analysis
        recommendations = {
            'site_type': 'custom',
            'product_selectors': [],
            'pagination_selectors': ['.next', '.pagination a'],
            'api_endpoints': [],
            'requires_javascript': self._detect_js_requirements(soup)
        }
        
        # AI-powered selector generation
        for category, selectors in self.patterns.items():
            valid_selectors = []
            for selector in selectors:
                if soup.select(selector):
                    valid_selectors.append(selector)
            recommendations[category] = valid_selectors
        
        return recommendations
    
    def _detect_js_requirements(self, soup: BeautifulSoup) -> bool:
        """Detect if site requires JavaScript rendering"""
        js_indicators = [
            soup.find('script', src=re.compile(r'react|angular|vue')),
            soup.find('div', {'data-react': True}),
            soup.find('ng-'),
            len(soup.find_all('script')) > 10
        ]
        return any(js_indicators)

class RobustSession:
    """Enhanced session with stealth capabilities and retry logic"""
    
    def __init__(self, stealth_mode: bool = False):
        self.stealth_mode = stealth_mode
        self.session = requests.Session()
        self._setup_headers()
    
    def _setup_headers(self):
        """Setup realistic browser headers"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        if self.stealth_mode:
            headers.update({
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            })
        
        self.session.headers.update(headers)
    
    async def get_with_retry(self, url: str, max_retries: int = 3) -> requests.Response:
        """Make HTTP request with intelligent retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < max_retries - 1:
                    delay = random.uniform(2, 5)
                    await asyncio.sleep(delay)
                else:
                    raise

class DataValidator:
    """AI-powered data validation and quality assurance"""
    
    def __init__(self):
        self.quality_thresholds = {
            'completeness': 0.8,
            'accuracy': 0.9,
            'consistency': 0.85
        }
    
    async def validate_with_ai(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data using AI-powered quality checks"""
        validation_results = {
            'is_valid': True,
            'quality_score': 0.0,
            'issues': [],
            'recommendations': []
        }
        
        # Completeness check
        completeness = self._check_completeness(data)
        validation_results['completeness'] = completeness
        
        # Consistency check
        consistency = self._check_consistency(data)
        validation_results['consistency'] = consistency
        
        # Calculate overall quality score
        validation_results['quality_score'] = (completeness + consistency) / 2
        
        # Determine if data meets quality thresholds
        validation_results['is_valid'] = all([
            validation_results['quality_score'] >= self.quality_thresholds['completeness'],
            consistency >= self.quality_thresholds['consistency']
        ])
        
        return validation_results
    
    def _check_completeness(self, data: Dict[str, Any]) -> float:
        """Check data completeness"""
        if 'products' not in data:
            return 0.0
        
        products = data['products']
        if not products:
            return 0.0
        
        required_fields = ['id', 'title', 'price']
        total_fields = len(required_fields) * len(products)
        complete_fields = 0
        
        for product in products:
            for field in required_fields:
                if field in product and product[field]:
                    complete_fields += 1
        
        return complete_fields / total_fields if total_fields > 0 else 0.0
    
    def _check_consistency(self, data: Dict[str, Any]) -> float:
        """Check data consistency"""
        if 'products' not in data:
            return 0.0
        
        products = data['products']
        if len(products) < 2:
            return 1.0
        
        # Check price format consistency
        price_formats = set()
        for product in products:
            if 'price' in product:
                price_formats.add(type(product['price']).__name__)
        
        consistency_score = 1.0 / len(price_formats) if price_formats else 0.0
        return consistency_score

class UniversalHarvester:
    """Main harvesting system with AI collaboration"""
    
    def __init__(self, config: HarvestConfig):
        self.config = config
        self.ai_agent = AIAssistant()
        self.session = RobustSession(config.stealth_mode)
        self.validator = DataValidator()
        self.harvest_stats = {
            'start_time': None,
            'end_time': None,
            'pages_processed': 0,
            'data_extracted': 0,
            'errors': 0
        }
    
    async def harvest_site(self) -> Dict[str, Any]:
        """Main harvesting method"""
        logger.info(f"Starting harvest of {self.config.target_url}")
        self.harvest_stats['start_time'] = datetime.now()
        
        try:
            # Step 1: Analyze site structure
            response = await self.session.get_with_retry(self.config.target_url)
            site_structure = await self.ai_agent.analyze_site_structure(response.text)
            
            # Step 2: Extract data using AI-recommended strategy
            if site_structure['site_type'] == 'shopify' or 'api' in site_structure:
                data = await self._extract_api_data(site_structure)
            else:
                data = await self._extract_html_data(response.text, site_structure)
            
            # Step 3: AI-powered validation
            validation_results = await self.validator.validate_with_ai(data)
            data['validation'] = validation_results
            
            # Step 4: Normalize and format output
            normalized_data = self._normalize_output(data)
            
            self.harvest_stats['end_time'] = datetime.now()
            self.harvest_stats['data_extracted'] = len(normalized_data.get('products', []))
            
            logger.info(f"Harvest completed successfully. Extracted {self.harvest_stats['data_extracted']} items")
            return normalized_data
            
        except Exception as e:
            logger.error(f"Hararvest failed: {str(e)}")
            self.harvest_stats['errors'] += 1
            raise
    
    async def _extract_api_data(self, site_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data using API endpoints"""
        # Implementation for API-based extraction
        return {'products': [], 'source': 'api', 'method': 'hybrid'}
    
    async def _extract_html_data(self, html_content: str, site_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data using HTML parsing with AI assistance"""
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        
        # Use AI-recommended selectors
        product_selectors = site_structure.get('product_selectors', ['.product-item'])
        
        for selector in product_selectors:
            items = soup.select(selector)
            for item in items:
                product = self._extract_product_data(item, site_structure)
                if product:
                    products.append(product)
        
        return {
            'products': products,
            'source': 'html',
            'method': 'ai_assisted',
            'selectors_used': product_selectors
        }
    
    def _extract_product_data(self, item_element, site_structure: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract single product data using AI-recommended selectors"""
        try:
            product = {
                'id': self._extract_id(item_element),
                'title': self._extract_text(item_element, ['h1', 'h2', 'h3', '.title']),
                'price': self._extract_price(item_element, site_structure),
                'description': self._extract_text(item_element, ['.description', '.summary']),
                'images': self._extract_images(item_element),
                'url': self._extract_url(item_element)
            }
            
            # Remove empty fields
            return {k: v for k, v in product.items() if v}
            
        except Exception as e:
            logger.warning(f"Error extracting product data: {str(e)}")
            return None
    
    def _extract_id(self, element) -> Optional[str]:
        """Extract product ID"""
        # Try various ID extraction methods
        id_selectors = ['[data-id]', '[data-product-id]', '.id']
        for selector in id_selectors:
            found = element.select_one(selector)
            if found:
                return found.get('data-id') or found.get('data-product-id') or found.text.strip()
        return None
    
    def _extract_text(self, element, selectors: List[str]) -> Optional[str]:
        """Extract text content using multiple selectors"""
        for selector in selectors:
            found = element.select_one(selector)
            if found:
                return found.get_text(strip=True)
        return None
    
    def _extract_price(self, element, site_structure: Dict[str, Any]) -> Optional[str]:
        """Extract price information"""
        price_selectors = site_structure.get('price_selectors', ['.price'])
        
        for selector in price_selectors:
            found = element.select_one(selector)
            if found:
                price_text = found.get_text(strip=True)
                # Clean and normalize price
                price = re.search(r'[\d,]+\.?\d*', price_text)
                return price.group() if price else price_text
        
        return None
    
    def _extract_images(self, element) -> List[str]:
        """Extract image URLs"""
        images = []
        img_selectors = ['img[src]', '[data-image]']
        
        for selector in img_selectors:
            found_images = element.select(selector)
            for img in found_images:
                src = img.get('src') or img.get('data-src')
                if src:
                    images.append(src)
        
        return images
    
    def _extract_url(self, element) -> Optional[str]:
        """Extract product URL"""
        link = element.find('a', href=True)
        return link['href'] if link else None
    
    def _normalize_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and format output data"""
        normalized = {
            'harvest_metadata': {
                'target_url': self.config.target_url,
                'harvest_time': datetime.now().isoformat(),
                'processing_stats': self.harvest_stats,
                'ai_assisted': self.config.use_ai_assistance,
                'stealth_mode': self.config.stealth_mode
            },
            'data': data,
            'quality_metrics': data.get('validation', {})
        }
        
        return normalized

# Example usage and demonstration
async def main():
    """Demonstration of the Universal Harvester"""
    
    # Configuration for DNM.EG e-commerce site
    config = HarvestConfig(
        target_url="https://dnm.eg",
        use_ai_assistance=True,
        stealth_mode=False,
        output_format="json"
    )
    
    # Initialize harvester
    harvester = UniversalHarvester(config)
    
    # Perform harvest
    try:
        result = await harvester.harvest_site()
        
        # Save results
        with open('harvest_results.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Harvest completed successfully!")
        print(f"Products extracted: {len(result['data'].get('products', []))}")
        print(f"Quality score: {result['quality_metrics'].get('quality_score', 0):.2f}")
        
    except Exception as e:
        print(f"Harvest failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
