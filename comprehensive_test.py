import sys
import os
import importlib
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import random

class ComprehensiveProjectTester:
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        
    def print_header(self, message):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"🧪 {message}")
        print(f"{'='*60}")
    
    def print_result(self, test_name, passed, message=None):
        """Print test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   📝 {message}")
        self.test_results[test_name] = passed
    
    def test_directory_structure(self):
        """Test project directory structure"""
        self.print_header("Testing Directory Structure")
        
        required_dirs = ['../data', '../reports', '../images', '../logs']
        for directory in required_dirs:
            if os.path.exists(directory):
                self.print_result(f"directory_{os.path.basename(directory)}", True, f"Found: {directory}")
            else:
                self.print_result(f"directory_{os.path.basename(directory)}", False, f"Missing: {directory}")
                # Create missing directory
                try:
                    os.makedirs(directory, exist_ok=True)
                    print(f"   🔧 Created: {directory}")
                except Exception as e:
                    print(f"   ⚠️ Failed to create {directory}: {e}")
    
    def test_python_environment(self):
        """Test Python environment"""
        self.print_header("Testing Python Environment")
        
        # Python version
        python_version = sys.version_info
        version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
        self.print_result("python_version", True, f"Python {version_str}")
        
        # Current directory
        current_dir = os.getcwd()
        self.print_result("current_directory", True, f"Working in: {current_dir}")
        
        # Script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.print_result("script_directory", True, f"Script location: {script_dir}")
    
    def test_required_libraries(self):
        """Test all required libraries"""
        self.print_header("Testing Required Libraries")
        
        required_libraries = [
            'selenium', 'beautifulsoup4', 'pandas', 'matplotlib',
            'seaborn', 'requests', 'numpy', 'webdriver_manager',
            're', 'json', 'time', 'random', 'datetime', 'os', 'sys'
        ]
        
        for lib_name in required_libraries:
            try:
                if lib_name in ['re', 'json', 'time', 'random', 'datetime', 'os', 'sys']:
                    # Built-in modules
                    importlib.import_module(lib_name)
                    self.print_result(f"library_{lib_name}", True)
                else:
                    # External modules
                    importlib.import_module(lib_name)
                    self.print_result(f"library_{lib_name}", True)
            except ImportError as e:
                self.print_result(f"library_{lib_name}", False, f"Missing: {e}")
            except Exception as e:
                self.print_result(f"library_{lib_name}", False, f"Error: {e}")
    
    def test_web_connectivity(self):
        """Test web connectivity to required URLs"""
        self.print_header("Testing Web Connectivity")
        
        test_urls = {
            "Cars24 Main": "https://www.cars24.com",
            "Cars24 Used Cars": "https://www.cars24.com/buy-used-cars/",
            "Google": "https://www.google.com"
        }
        
        for site_name, url in test_urls.items():
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.print_result(f"web_{site_name.lower().replace(' ', '_')}", True, f"HTTP {response.status_code}")
                else:
                    self.print_result(f"web_{site_name.lower().replace(' ', '_')}", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.print_result(f"web_{site_name.lower().replace(' ', '_')}", False, f"Error: {e}")
    
    def test_data_operations(self):
        """Test data creation and manipulation"""
        self.print_header("Testing Data Operations")
        
        try:
            # Create sample data
            sample_data = []
            for i in range(10):
                car = {
                    'brand': 'Maruti Suzuki',
                    'model': random.choice(['Swift', 'Baleno', 'Alto', 'Wagon R']),
                    'price': f'₹{random.randint(300000, 800000):,}',
                    'year': random.randint(2018, 2023),
                    'km_driven': f'{random.randint(10000, 80000):,} km',
                    'fuel_type': random.choice(['Petrol', 'Diesel', 'CNG']),
                    'transmission': random.choice(['Manual', 'Automatic']),
                    'location': random.choice(['Delhi', 'Mumbai', 'Bangalore']),
                    'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                sample_data.append(car)
            
            # Create DataFrame
            df = pd.DataFrame(sample_data)
            self.print_result("dataframe_creation", True, f"Created DataFrame with {len(df)} records")
            
            # Save to CSV
            os.makedirs('../data', exist_ok=True)
            csv_path = '../data/test_sample_data.csv'
            df.to_csv(csv_path, index=False)
            self.print_result("csv_export", True, f"Saved to: {csv_path}")
            
            # Read back from CSV
            df_read = pd.read_csv(csv_path)
            self.print_result("csv_import", len(df_read) == len(df), f"Read back {len(df_read)} records")
            
            # Basic data analysis
            price_stats = df_read.describe() if 'price' in df_read.columns else "No numeric columns"
            self.print_result("basic_analysis", True, "Basic analysis completed")
            
        except Exception as e:
            self.print_result("data_operations", False, f"Error: {e}")
    
    def test_file_operations(self):
        """Test file creation and management"""
        self.print_header("Testing File Operations")
        
        try:
            # Test file creation
            test_files = ['../data/test_file.txt', '../reports/test_report.txt', '../images/test_info.txt']
            
            for file_path in test_files:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Test file created at {datetime.now()}")
                self.print_result(f"file_creation_{os.path.basename(file_path)}", True, f"Created: {file_path}")
            
            # Test file deletion
            for file_path in test_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.print_result(f"file_deletion_{os.path.basename(file_path)}", True, f"Cleaned: {file_path}")
            
        except Exception as e:
            self.print_result("file_operations", False, f"Error: {e}")
    
    def test_individual_scripts(self):
        """Test individual script files"""
        self.print_header("Testing Script Files")
        
        script_files = [
            'cars24_robust_scraper.py',
            'data_analysis.py', 
            'report_generator.py',
            'complete_project.py'
        ]
        
        for script_file in script_files:
            if os.path.exists(script_file):
                try:
                    # Try to import the script to check for syntax errors
                    with open(script_file, 'r', encoding='utf-8') as f:
                        script_content = f.read()
                    
                    # Basic syntax check by compiling
                    compile(script_content, script_file, 'exec')
                    self.print_result(f"script_{script_file}", True, f"Syntax OK: {script_file}")
                    
                except SyntaxError as e:
                    self.print_result(f"script_{script_file}", False, f"Syntax error: {e}")
                except Exception as e:
                    self.print_result(f"script_{script_file}", False, f"Error: {e}")
            else:
                self.print_result(f"script_{script_file}", False, f"Missing: {script_file}")
    
    def test_selenium_functionality(self):
        """Test Selenium WebDriver functionality"""
        self.print_header("Testing Selenium WebDriver")
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Test basic imports
            self.print_result("selenium_imports", True, "Selenium modules imported successfully")
            
            # Test ChromeDriver manager
            try:
                chrome_driver_path = ChromeDriverManager().install()
                self.print_result("chromedriver_manager", True, f"ChromeDriver path: {chrome_driver_path}")
            except Exception as e:
                self.print_result("chromedriver_manager", False, f"ChromeDriver error: {e}")
            
            # Test browser options creation
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode for testing
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            self.print_result("browser_options", True, "Browser options configured")
            
        except Exception as e:
            self.print_result("selenium_setup", False, f"Selenium setup error: {e}")
    
    def run_quick_functionality_test(self):
        """Run quick functionality test without dependencies"""
        self.print_header("Quick Functionality Test")
        
        try:
            # Test core Python functionality
            test_list = [1, 2, 3, 4, 5]
            test_sum = sum(test_list)
            self.print_result("python_basics", test_sum == 15, "Basic Python operations working")
            
            # Test pandas functionality
            test_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            df_sum = test_df['A'].sum()
            self.print_result("pandas_basics", df_sum == 6, "Pandas basic operations working")
            
            # Test file operations
            test_content = "Quick test content"
            with open('../data/quick_test.txt', 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            with open('../data/quick_test.txt', 'r', encoding='utf-8') as f:
                read_content = f.read()
            
            os.remove('../data/quick_test.txt')
            self.print_result("file_io", read_content == test_content, "File I/O operations working")
            
        except Exception as e:
            self.print_result("quick_test", False, f"Quick test error: {e}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.print_header("Test Results Summary")
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        failed_tests = total_tests - passed_tests
        
        print(f"Overall: {passed_tests}/{total_tests} tests passed")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Print detailed results
        for test_name, passed in self.test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name}")
        
        # Calculate duration
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print(f"\n⏱️ Test Duration: {duration}")
        
        # Recommendations
        if failed_tests > 0:
            print(f"\n⚠️ SOME TESTS FAILED! Please fix the issues above.")
            print(f"\n🔧 Common solutions:")
            print(f"• Run: pip install selenium beautifulsoup4 pandas matplotlib seaborn webdriver-manager")
            print(f"• Check internet connection")
            print(f"• Verify directory permissions")
            print(f"• Update Chrome browser to latest version")
        else:
            print(f"\n🎉 ALL TESTS PASSED! Your environment is ready for the project.")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🧪 RUNNING COMPREHENSIVE PROJECT TESTS")
        print("=" * 60)
        
        # Run all test suites
        self.test_directory_structure()
        self.test_python_environment()
        self.test_required_libraries()
        self.test_web_connectivity()
        self.test_data_operations()
        self.test_file_operations()
        self.test_individual_scripts()
        self.test_selenium_functionality()
        self.run_quick_functionality_test()
        
        # Generate final report
        self.generate_test_report()

def main():
    tester = ComprehensiveProjectTester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()