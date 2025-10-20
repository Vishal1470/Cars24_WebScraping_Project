"""
Fixed Cars24 Scraper - Uses multiple approaches to handle website changes
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import logging
import re
import json
from datetime import datetime
import os
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cars24_scraper_fixed.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class Cars24ScraperFixed:
    """
    Fixed Cars24 Scraper that uses multiple fallback strategies
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.scraped_data = []
        
        # Multiple selector strategies
        self.selectors = {
            'car_containers': [
                # Try multiple container patterns
                'article', 'div[class*="card"]', 'div[class*="item"]',
                'div[class*="listing"]', 'div[class*="product"]',
                'a[class*="car"]', 'div[class*="vehicle"]',
                'div.gtm-car-item', 'div._1W3mk', 'article._2Dnss'
            ],
            'car_name': [
                'h1', 'h2', 'h3', 'h4',
                '[class*="title"]', '[class*="name"]',
                'h3._2mylV', 'div._3FpCg'
            ],
            'price': [
                '[class*="price"]', '[class*="amount"]', '[class*="cost"]',
                'div._3FpCg', 'div._2p-s9',
                'span[class*="price"]', 'div[class*="price"]'
            ]
        }
    
    def setup_session(self):
        """Setup requests session with proper headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
    
    def get_page_content(self, url, max_retries=3):
        """Get page content with multiple retries and fallbacks"""
        for attempt in range(max_retries):
            try:
                logger.info(f"🌐 Fetching page (attempt {attempt + 1}): {url}")
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                # Handle encoding issues
                if response.encoding is None:
                    response.encoding = 'utf-8'
                
                logger.info(f"✅ Successfully fetched page: {url}")
                return response.text
                
            except requests.RequestException as e:
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    delay = random.uniform(2, 5)
                    logger.info(f"⏳ Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"❌ All retries failed for {url}")
        
        return None
    
    def find_car_elements_advanced(self, soup):
        """Advanced method to find car elements with multiple strategies"""
        car_elements = []
        
        logger.info("🔍 Using advanced car element detection...")
        
        # Strategy 1: Try known CSS selectors
        for selector in self.selectors['car_containers']:
            try:
                elements = soup.select(selector)
                if elements:
                    logger.info(f"✅ Found {len(elements)} elements with selector: {selector}")
                    # Filter elements that might contain car data
                    for element in elements:
                        text = element.get_text().lower()
                        if any(keyword in text for keyword in ['maruti', 'suzuki', '₹', 'km', 'car']):
                            car_elements.append(element)
                    break
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        # Strategy 2: Look for elements containing car-related keywords
        if not car_elements:
            logger.info("🔄 Trying keyword-based detection...")
            all_elements = soup.find_all(['div', 'article', 'section', 'a'])
            for element in all_elements:
                text = element.get_text().lower()
                # Check if element contains car-related content
                if (('maruti' in text or 'suzuki' in text) and 
                    ('₹' in text or 'km' in text or 'price' in text)):
                    car_elements.append(element)
            
            logger.info(f"🔄 Found {len(car_elements)} potential car elements with keyword search")
        
        # Strategy 3: Look for elements with specific data attributes
        if not car_elements:
            logger.info("🔄 Trying data attribute search...")
            data_elements = soup.find_all(attrs={"data-vehicle": True})
            car_elements.extend(data_elements)
            
            testid_elements = soup.find_all(attrs={"data-testid": True})
            for element in testid_elements:
                if 'car' in str(element.get('data-testid', '')).lower():
                    car_elements.append(element)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_elements = []
        for element in car_elements:
            element_id = id(element)
            if element_id not in seen:
                seen.add(element_id)
                unique_elements.append(element)
        
        logger.info(f"🎯 Total unique car elements found: {len(unique_elements)}")
        return unique_elements
    
    def extract_car_data_robust(self, element, location_name):
        """Robust car data extraction with multiple fallbacks"""
        try:
            # Extract car name with multiple strategies
            car_name = self.extract_car_name(element)
            
            # Skip if not Maruti Suzuki (unless we can't determine)
            if car_name and not any(brand in car_name.upper() for brand in ['MARUTI', 'SUZUKI']):
                logger.debug(f"Skipping non-Maruti car: {car_name}")
                return None
            
            # Extract other details
            price = self.extract_price(element)
            specifications = self.extract_specifications(element)
            
            car_data = {
                'car_name': car_name or 'Maruti Suzuki Car',
                'price': price or 'Price not available',
                'kilometers_driven': specifications.get('kilometers', 'KM not available'),
                'year_of_manufacture': specifications.get('year', 'Year not available'),
                'fuel_type': specifications.get('fuel_type', 'Fuel type not available'),
                'transmission': specifications.get('transmission', 'Transmission not available'),
                'location': location_name,
                'brand': 'Maruti Suzuki',
                'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'element_text_preview': element.get_text()[:100] + '...' if element.get_text() else 'No text'
            }
            
            logger.info(f"✅ Extracted: {car_data['car_name']} - {car_data['price']}")
            return car_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting car data: {e}")
            return self.create_fallback_data(location_name, str(e))
    
    def extract_car_name(self, element):
        """Extract car name with multiple fallbacks"""
        # Strategy 1: Try CSS selectors
        for selector in self.selectors['car_name']:
            try:
                name_element = element.select_one(selector)
                if name_element and name_element.get_text(strip=True):
                    name = name_element.get_text(strip=True)
                    if name and len(name) < 100:
                        return name
            except Exception:
                continue
        
        # Strategy 2: Look for text containing Maruti/Suzuki
        element_text = element.get_text()
        lines = [line.strip() for line in element_text.split('\n') if line.strip()]
        for line in lines:
            if any(brand in line.upper() for brand in ['MARUTI', 'SUZUKI']):
                return line
        
        # Strategy 3: Extract from any heading tags within the element
        headings = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings:
            if heading.get_text(strip=True):
                return heading.get_text(strip=True)
        
        return None
    
    def extract_price(self, element):
        """Extract price with multiple strategies"""
        # Strategy 1: Try CSS selectors
        for selector in self.selectors['price']:
            try:
                price_element = element.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    if price_text and any(c.isdigit() for c in price_text):
                        return self.clean_price(price_text)
            except Exception:
                continue
        
        # Strategy 2: Look for price patterns in text
        element_text = element.get_text()
        price_patterns = [
            r'[₹₹]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*)\s*[lL][aA][kK][hH]',
            r'price\s*:\s*[₹₹]?\s*(\d{1,3}(?:,\d{3})*)'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, element_text)
            if matches:
                return f"₹{matches[0]}"
        
        return None
    
    def clean_price(self, price_text):
        """Clean and format price text"""
        # Remove extra text and keep numbers
        clean_text = re.sub(r'[^\d,]', '', price_text)
        if clean_text:
            return f"₹{clean_text}"
        return price_text
    
    def extract_specifications(self, element):
        """Extract specifications with pattern matching"""
        specs = {
            'kilometers': 'KM not available',
            'year': 'Year not available',
            'fuel_type': 'Fuel type not available',
            'transmission': 'Transmission not available'
        }
        
        element_text = element.get_text()
        
        # Extract kilometers
        km_patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*[kK][mM]',
            r'(\d{1,3}(?:,\d{3})*)\s*[kK][iI][lL][oO]',
            r'odometer\s*:\s*(\d+)'
        ]
        for pattern in km_patterns:
            match = re.search(pattern, element_text)
            if match:
                specs['kilometers'] = f"{match.group(1)} km"
                break
        
        # Extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', element_text)
        if year_match:
            specs['year'] = year_match.group(0)
        
        # Extract fuel type
        if re.search(r'petrol', element_text, re.IGNORECASE):
            specs['fuel_type'] = 'Petrol'
        elif re.search(r'diesel', element_text, re.IGNORECASE):
            specs['fuel_type'] = 'Diesel'
        elif re.search(r'cng', element_text, re.IGNORECASE):
            specs['fuel_type'] = 'CNG'
        elif re.search(r'electric', element_text, re.IGNORECASE):
            specs['fuel_type'] = 'Electric'
        
        # Extract transmission
        if re.search(r'automatic', element_text, re.IGNORECASE):
            specs['transmission'] = 'Automatic'
        elif re.search(r'manual', element_text, re.IGNORECASE):
            specs['transmission'] = 'Manual'
        
        return specs
    
    def create_fallback_data(self, location_name, error_msg):
        """Create fallback data when extraction fails"""
        return {
            'car_name': f'Extraction failed: {error_msg}',
            'price': 'Check manually',
            'kilometers_driven': 'N/A',
            'year_of_manufacture': 'N/A',
            'fuel_type': 'N/A',
            'transmission': 'N/A',
            'location': location_name,
            'brand': 'Maruti Suzuki',
            'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'error': error_msg
        }
    
    def scrape_single_location(self, url, location_name):
        """Scrape a single location with comprehensive error handling"""
        logger.info(f"📍 Scraping location: {location_name}")
        
        page_content = self.get_page_content(url)
        if not page_content:
            logger.error(f"❌ Failed to get page content for {location_name}")
            return [self.create_fallback_data(location_name, "Page load failed")]
        
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Save page for debugging
            debug_filename = f"debug_{location_name}_{datetime.now().strftime('%H%M%S')}.html"
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            logger.info(f"💾 Debug page saved: {debug_filename}")
            
            # Find car elements
            car_elements = self.find_car_elements_advanced(soup)
            
            if not car_elements:
                logger.warning(f"⚠️ No car elements found on {location_name}")
                # Try to understand what's on the page
                self.analyze_page_content(soup, location_name)
                return [self.create_fallback_data(location_name, "No car elements found")]
            
            scraped_cars = []
            for i, element in enumerate(car_elements[:20]):  # Limit to first 20 elements
                car_data = self.extract_car_data_robust(element, location_name)
                if car_data:
                    scraped_cars.append(car_data)
                
                # Polite delay
                time.sleep(random.uniform(0.5, 1.5))
                
                # Progress update
                if (i + 1) % 5 == 0:
                    logger.info(f"📊 Progress: {i + 1}/{len(car_elements)} elements processed")
            
            logger.info(f"✅ Successfully processed {len(scraped_cars)} cars from {location_name}")
            return scraped_cars
            
        except Exception as e:
            logger.error(f"❌ Error scraping {location_name}: {e}")
            return [self.create_fallback_data(location_name, f"Scraping error: {e}")]
    
    def analyze_page_content(self, soup, location_name):
        """Analyze page content to understand what we're getting"""
        logger.info(f"🔍 Analyzing page content for {location_name}...")
        
        # Check page title
        title = soup.title.string if soup.title else "No title"
        logger.info(f"📄 Page title: {title}")
        
        # Check for common elements
        common_elements = {
            'forms': len(soup.find_all('form')),
            'links': len(soup.find_all('a')),
            'images': len(soup.find_all('img')),
            'scripts': len(soup.find_all('script')),
        }
        
        logger.info(f"📊 Page elements: {common_elements}")
        
        # Look for text content
        all_text = soup.get_text()
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        logger.info(f"📝 Page has {len(lines)} text lines")
        
        # Look for keywords
        keywords = ['maruti', 'suzuki', 'car', 'buy', 'sell', 'price', 'km']
        found_keywords = []
        for keyword in keywords:
            if keyword in all_text.lower():
                found_keywords.append(keyword)
        
        logger.info(f"🔑 Found keywords: {found_keywords}")
        
        # Save sample of page text
        sample_text = '\n'.join(lines[:10])  # First 10 lines
        logger.info(f"📋 Sample text:\n{sample_text}")
    
    def test_urls(self, location_urls):
        """Test if URLs are accessible and contain car content"""
        logger.info("🧪 Testing URLs...")
        
        valid_urls = {}
        
        for location_name, url in location_urls.items():
            logger.info(f"🔍 Testing: {location_name} - {url}")
            
            page_content = self.get_page_content(url)
            if not page_content:
                logger.warning(f"❌ URL not accessible: {url}")
                continue
            
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Check for car content indicators
            all_text = soup.get_text().lower()
            indicators = [
                'maruti' in all_text or 'suzuki' in all_text,
                'car' in all_text,
                'buy' in all_text or 'sell' in all_text,
                len(soup.find_all(['article', 'div'], class_=re.compile(r'car|vehicle|listing'))) > 0
            ]
            
            if any(indicators):
                valid_urls[location_name] = url
                logger.info(f"✅ URL valid: {url}")
            else:
                logger.warning(f"⚠️ URL accessible but no car content: {url}")
        
        return valid_urls
    
    def create_sample_dataset(self):
        """Create a sample dataset for demonstration"""
        logger.info("📝 Creating sample dataset for demonstration...")
        
        sample_data = []
        models = ['Swift', 'Baleno', 'Alto', 'Wagon R', 'Dzire', 'Celerio', 'Ertiga']
        locations = ['Delhi', 'Mumbai', 'Bangalore', 'Hyderabad', 'Chennai']
        fuel_types = ['Petrol', 'Diesel', 'CNG']
        transmissions = ['Manual', 'Automatic']
        
        for i in range(50):
            car = {
                'car_name': f'Maruti Suzuki {models[i % len(models)]}',
                'price': f'₹{5 + (i % 3)},{50 + (i * 100) % 50},000',
                'kilometers_driven': f'{15 + (i % 10)},{500 + (i * 100) % 500} km',
                'year_of_manufacture': f'{2018 + (i % 6)}',
                'fuel_type': fuel_types[i % len(fuel_types)],
                'transmission': transmissions[i % len(transmissions)],
                'location': locations[i % len(locations)],
                'brand': 'Maruti Suzuki',
                'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'data_source': 'sample'
            }
            sample_data.append(car)
        
        df = pd.DataFrame(sample_data)
        return df
    
    def scrape_with_fallback(self, location_urls):
        """Scrape with comprehensive fallback strategies"""
        logger.info("🚀 Starting comprehensive scraping with fallbacks...")
        
        # Test URLs first
        valid_urls = self.test_urls(location_urls)
        
        if not valid_urls:
            logger.warning("❌ No valid URLs found. Using sample data.")
            return self.create_sample_dataset()
        
        all_cars = []
        successful_locations = 0
        
        for location_name, url in valid_urls.items():
            logger.info(f"🎯 Processing: {location_name}")
            
            cars = self.scrape_single_location(url, location_name)
            
            # Check if we got any valid cars (not error entries)
            valid_cars = [car for car in cars if 'Extraction failed' not in car['car_name']]
            
            if valid_cars:
                all_cars.extend(valid_cars)
                successful_locations += 1
                logger.info(f"✅ {location_name}: {len(valid_cars)} valid cars")
            else:
                logger.warning(f"⚠️ {location_name}: No valid cars found")
            
            # Delay between locations
            time.sleep(random.uniform(2, 4))
        
        # Create DataFrame
        if all_cars:
            df = pd.DataFrame(all_cars)
            logger.info(f"🎉 Successfully scraped {len(df)} cars from {successful_locations} locations")
        else:
            logger.warning("⚠️ No cars scraped. Creating sample dataset.")
            df = self.create_sample_dataset()
        
        return df
    
    def save_to_csv(self, df, filename="cars24_data.csv"):
        """Save DataFrame to CSV"""
        try:
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"💾 Data saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving CSV: {e}")
            return False
    
    def run_complete_scraping(self):
        """Run complete scraping process"""
        logger.info("🚗 Starting Complete Cars24 Scraping Process")
        
        # Define URLs to try
        location_urls = {
            "Delhi": "https://www.cars24.com/buy-used-maruti-suzuki-cars-delhi/",
            "Mumbai": "https://www.cars24.com/buy-used-maruti-suzuki-cars-mumbai/",
            "Bangalore": "https://www.cars24.com/buy-used-maruti-suzuki-cars-bangalore/",
            "Hyderabad": "https://www.cars24.com/buy-used-maruti-suzuki-cars-hyderabad/",
            "Chennai": "https://www.cars24.com/buy-used-maruti-suzuki-cars-chennai/",
            # Alternative URLs
            "Delhi_Alt": "https://www.cars24.com/buy-used-cars-delhi/",
            "Mumbai_Alt": "https://www.cars24.com/buy-used-cars-mumbai/",
            "Bangalore_Alt": "https://www.cars24.com/buy-used-cars-bangalore/"
        }
        
        start_time = time.time()
        
        # Scrape data
        df = self.scrape_with_fallback(location_urls)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cars24_scraped_data_{timestamp}.csv"
        self.save_to_csv(df, filename)
        
        # Print summary
        duration = time.time() - start_time
        self.print_scraping_summary(df, duration, filename)
        
        return df
    
    def print_scraping_summary(self, df, duration, filename):
        """Print comprehensive scraping summary"""
        print("\n" + "="*70)
        print("🎯 CARS24 SCRAPING SUMMARY")
        print("="*70)
        
        print(f"⏰ Duration: {duration:.1f} seconds")
        print(f"📊 Total Cars: {len(df)}")
        
        if 'data_source' in df.columns and 'sample' in df['data_source'].values:
            print("📝 NOTE: Using sample data (real scraping failed)")
        else:
            print("✅ Data Source: Real scraping")
        
        if not df.empty:
            print(f"\n📍 Locations:")
            if 'location' in df.columns:
                location_counts = df['location'].value_counts()
                for location, count in location_counts.items():
                    print(f"   🚗 {location}: {count} cars")
            
            print(f"\n💰 Price Range:")
            if 'price' in df.columns:
                prices = df['price'].value_counts().head(5)
                for price, count in prices.items():
                    print(f"   ₹ {price}: {count} cars")
        
        print(f"\n💾 Data Saved: {filename}")
        print("="*70)

def main():
    """Main execution function"""
    print("🚗 FIXED CARS24 SCRAPER")
    print("="*50)
    print("This version uses multiple fallback strategies:")
    print("1. Multiple URL testing")
    print("2. Advanced element detection")
    print("3. Pattern-based data extraction")
    print("4. Sample data fallback")
    print("="*50)
    
    # Create scraper instance
    scraper = Cars24ScraperFixed()
    
    # Run complete scraping
    try:
        df = scraper.run_complete_scraping()
        
        if not df.empty:
            print("\n🎉 SCRAPING COMPLETED!")
            if 'data_source' in df.columns and 'sample' in df['data_source'].values:
                print("📝 Using sample data for demonstration purposes.")
                print("💡 Check the debug HTML files to see what the scraper encountered.")
            else:
                print(f"✅ Successfully scraped {len(df)} real cars from Cars24!")
        else:
            print("\n❌ SCRAPING FAILED")
            print("No data was collected. Check the log files for details.")
            
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        print("Please check the error message and try again.")

if __name__ == "__main__":
    main()