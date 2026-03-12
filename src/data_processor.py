"""
Shopify Product Data Processor
A comprehensive tool for processing Shopify product catalogs
"""

import json
import pandas as pd
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShopifyDataProcessor:
    """
    Advanced Shopify product data processor with validation and cleaning capabilities
    """
    
    def __init__(self):
        self.processing_stats = {
            'total_products': 0,
            'total_variants': 0,
            'errors': 0,
            'processing_start': None,
            'processing_end': None
        }
    
    def load_data(self, file_path: str) -> Dict[str, Any]:
        """
        Load and validate Shopify JSON data
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dictionary containing the loaded data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Validate basic structure
            if 'all_products' not in data:
                raise ValueError("Invalid Shopify export format")
            
            logger.info(f"Successfully loaded {len(data['all_products'])} products")
            return data
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def process_all_products(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process all products in the dataset
        
        Args:
            raw_data: Raw Shopify data
            
        Returns:
            Processed products with statistics
        """
        self.processing_stats['processing_start'] = datetime.now()
        
        processed_products = []
        
        for product in raw_data['all_products']:
            try:
                processed_product = self._process_single_product(product)
                processed_products.append(processed_product)
                
            except Exception as e:
                logger.warning(f"Error processing product {product.get('id', 'unknown')}: {str(e)}")
                self.processing_stats['errors'] += 1
                continue
        
        self.processing_stats['processing_end'] = datetime.now()
        self.processing_stats['total_products'] = len(processed_products)
        self.processing_stats['total_variants'] = sum(p['total_variants'] for p in processed_products)
        
        result = {
            'products': processed_products,
            'processing_stats': self._get_processing_stats()
        }
        
        logger.info(f"Processed {len(processed_products)} products successfully")
        return result
    
    def _process_single_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single product and its variants
        
        Args:
            product: Single product data
            
        Returns:
            Processed product information
        """
        # Extract basic product info
        processed = {
            'id': product.get('id'),
            'title': product.get('title', ''),
            'handle': product.get('handle', ''),
            'vendor': product.get('vendor', ''),
            'product_type': product.get('product_type', ''),
            'tags': product.get('tags', []),
            'created_at': product.get('created_at', ''),
            'updated_at': product.get('updated_at', ''),
            'published_at': product.get('published_at', ''),
            'total_variants': len(product.get('variants', [])),
            'variants': []
        }
        
        # Process variants
        variants = product.get('variants', [])
        processed_variants = []
        prices = []
        
        for variant in variants:
            processed_variant = self._process_variant(variant)
            processed_variants.append(processed_variant)
            
            # Collect prices for range calculation
            try:
                price = float(processed_variant.get('price', 0))
                prices.append(price)
            except (ValueError, TypeError):
                continue
        
        processed['variants'] = processed_variants
        
        # Calculate price range
        if prices:
            processed['price_range'] = {
                'min': min(prices),
                'max': max(prices),
                'average': sum(prices) / len(prices)
            }
        else:
            processed['price_range'] = {'min': 0, 'max': 0, 'average': 0}
        
        # Add availability statistics
        available_variants = sum(1 for v in processed_variants if v.get('available', False))
        processed['availability'] = {
            'total_variants': len(processed_variants),
            'available_variants': available_variants,
            'availability_rate': available_variants / len(processed_variants) if processed_variants else 0
        }
        
        return processed
    
    def _process_variant(self, variant: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single product variant
        
        Args:
            variant: Variant data
            
        Returns:
            Processed variant information
        """
        processed_variant = {
            'id': variant.get('id'),
            'title': variant.get('title', ''),
            'option1': variant.get('option1'),
            'option2': variant.get('option2'),
            'option3': variant.get('option3'),
            'sku': variant.get('sku', ''),
            'price': variant.get('price', '0.00'),
            'compare_at_price': variant.get('compare_at_price'),
            'requires_shipping': variant.get('requires_shipping', True),
            'taxable': variant.get('taxable', True),
            'available': variant.get('available', False),
            'position': variant.get('position', 0),
            'grams': variant.get('grams', 0)
        }
        
        # Process featured image if exists
        if 'featured_image' in variant and variant['featured_image']:
            processed_variant['featured_image'] = {
                'id': variant['featured_image'].get('id'),
                'src': variant['featured_image'].get('src', ''),
                'alt': variant['featured_image'].get('alt', ''),
                'width': variant['featured_image'].get('width', 0),
                'height': variant['featured_image'].get('height', 0)
            }
        
        return processed_variant
    
    def _get_processing_stats(self) -> Dict[str, Any]:
        """
        Generate comprehensive processing statistics
        
        Returns:
            Dictionary with processing statistics
        """
        if self.processing_stats['processing_start'] and self.processing_stats['processing_end']:
            processing_time = self.processing_stats['processing_end'] - self.processing_stats['processing_start']
        else:
            processing_time = None
        
        return {
            'total_products': self.processing_stats['total_products'],
            'total_variants': self.processing_stats['total_variants'],
            'errors': self.processing_stats['errors'],
            'success_rate': (self.processing_stats['total_products'] / 
                           (self.processing_stats['total_products'] + self.processing_stats['errors']) * 100 
                           if (self.processing_stats['total_products'] + self.processing_stats['errors']) > 0 else 0),
            'processing_time': str(processing_time) if processing_time else 'Unknown',
            'processing_start': self.processing_stats['processing_start'].isoformat() if self.processing_stats['processing_start'] else None,
            'processing_end': self.processing_stats['processing_end'].isoformat() if self.processing_stats['processing_end'] else None
        }
    
    def export_to_json(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Export processed data to JSON file
        
        Args:
            data: Processed data to export
            output_path: Output file path
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            logger.info(f"Data exported successfully to {output_path}")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            raise
    
    def export_to_csv(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Export processed data to CSV file for analysis
        
        Args:
            data: Processed data to export
            output_path: Output file path
        """
        try:
            # Convert to DataFrame for CSV export
            products = data['products']
            
            # Flatten the data for CSV
            flattened_data = []
            for product in products:
                base_row = {
                    'product_id': product['id'],
                    'product_title': product['title'],
                    'vendor': product['vendor'],
                    'product_type': product['product_type'],
                    'total_variants': product['total_variants'],
                    'min_price': product['price_range']['min'],
                    'max_price': product['price_range']['max'],
                    'avg_price': product['price_range']['average'],
                    'availability_rate': product['availability']['availability_rate'],
                    'created_at': product['created_at'],
                    'updated_at': product['updated_at']
                }
                
                # Add variant information
                for i, variant in enumerate(product['variants']):
                    row = base_row.copy()
                    row.update({
                        'variant_id': variant['id'],
                        'variant_title': variant['title'],
                        'sku': variant['sku'],
                        'variant_price': variant['price'],
                        'variant_available': variant['available'],
                        'variant_position': variant['position']
                    })
                    flattened_data.append(row)
            
            # Create DataFrame and export
            df = pd.DataFrame(flattened_data)
            df.to_csv(output_path, index=False)
            logger.info(f"CSV exported successfully to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            raise
    
    def generate_summary_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive summary report
        
        Args:
            data: Processed data
            
        Returns:
            Summary report dictionary
        """
        products = data['products']
        
        # Calculate statistics
        total_products = len(products)
        total_variants = sum(p['total_variants'] for p in products)
        
        # Vendor distribution
        vendors = {}
        for product in products:
            vendor = product.get('vendor', 'Unknown')
            vendors[vendor] = vendors.get(vendor, 0) + 1
        
        # Price distribution
        all_prices = []
        for product in products:
            for variant in product['variants']:
                try:
                    price = float(variant.get('price', 0))
                    all_prices.append(price)
                except (ValueError, TypeError):
                    continue
        
        return {
            'summary': {
                'total_products': total_products,
                'total_variants': total_variants,
                'average_variants_per_product': total_variants / total_products if total_products > 0 else 0,
                'unique_vendors': len(vendors),
                'price_statistics': {
                    'min_price': min(all_prices) if all_prices else 0,
                    'max_price': max(all_prices) if all_prices else 0,
                    'avg_price': sum(all_prices) / len(all_prices) if all_prices else 0
                }
            },
            'vendor_distribution': vendors,
            'processing_stats': data['processing_stats']
        }
