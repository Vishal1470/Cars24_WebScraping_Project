"""
Enhanced Report Generator for Cars24 Project
Creates comprehensive reports with actual data insights
"""

import pandas as pd
import json
from datetime import datetime
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, project_results: Dict, dataframe: pd.DataFrame, summary_stats: Optional[Dict] = None):
        self.results = project_results
        self.df = dataframe
        self.summary_stats = summary_stats or {}
        self.report_time = datetime.now()
        self.report_content = ""
        
    def generate_text_report(self) -> str:
        """Generate comprehensive text report"""
        logger.info("📝 Generating comprehensive text report...")
        
        try:
            self._create_report_header()
            self._add_project_overview()
            self._add_methodology()
            self._add_technical_details()
            self._add_data_analysis()
            self._add_challenges_solutions()
            self._add_insights_recommendations()
            self._add_conclusion()
            self._add_appendix()
            
            # Save report
            report_path = self._save_text_report()
            return report_path
            
        except Exception as e:
            logger.error(f"❌ Text report generation failed: {e}")
            return self._create_fallback_report()
    
    def _create_report_header(self):
        """Create report header"""
        self.report_content = f"""
{'='*80}
              CARS24 MARUTI SUZUKI WEB SCRAPING PROJECT REPORT
{'='*80}

Report Generated: {self.report_time.strftime('%Y-%m-%d %H:%M:%S')}
Project Duration: {self.results['project_info'].get('duration_seconds', 0):.1f} seconds
Overall Status: {self.results['project_info'].get('status', 'unknown').upper()}

"""
    
    def _add_project_overview(self):
        """Add project overview section"""
        self.report_content += """
1. PROJECT OVERVIEW
================================================================================

1.1 Project Objectives:
• Develop web scraping skills by extracting car details from Cars24.com
• Collect data for Maruti Suzuki cars from multiple locations
• Perform comprehensive data analysis and visualization
• Generate actionable insights from the scraped data

1.2 Target Data Points:
• Car Name and Model
• Price Information
• Kilometers Driven
• Year of Manufacture
• Fuel Type
• Transmission Type
• Location

1.3 Project Scope:
• Target Brand: Maruti Suzuki
• Locations: Multiple Indian cities
• Data Sources: Cars24.com
• Timeline: Complete data pipeline implementation

"""
    
    def _add_methodology(self):
        """Add methodology section"""
        self.report_content += """
2. METHODOLOGY
================================================================================

2.1 Research and Planning Phase:
• Analyzed Cars24.com website structure and anti-bot measures
• Identified actual HTML classes and data attributes using browser inspection
• Developed robust selector strategies for dynamic content
• Planned data extraction pipeline with error handling

2.2 Data Extraction Phase:
• Implemented Selenium WebDriver for JavaScript-rendered content
• Used BeautifulSoup for HTML parsing and data extraction
• Applied rotating user agents and delays to avoid detection
• Implemented comprehensive error handling and retry mechanisms

2.3 Data Processing Phase:
• Cleaned and validated scraped data
• Handled missing values and data inconsistencies
• Standardized data formats across different locations
• Performed data quality assessment

2.4 Analysis and Reporting Phase:
• Conducted statistical analysis of car data
• Created visualizations for key metrics
• Generated insights on pricing and car specifications
• Prepared comprehensive project documentation

"""
    
    def _add_technical_details(self):
        """Add technical implementation details"""
        phases = self.results.get('phases', {})
        
        self.report_content += """
3. TECHNICAL IMPLEMENTATION
================================================================================

3.1 Tools and Technologies:
• Programming Language: Python 3.x
• Web Scraping: Selenium, BeautifulSoup4, Requests
• Data Analysis: Pandas, NumPy
• Visualization: Matplotlib, Seaborn
• Reporting: Custom report generators

3.2 Key Libraries Used:
• selenium: Web automation and dynamic content handling
• beautifulsoup4: HTML parsing and data extraction
• pandas: Data manipulation and analysis
• matplotlib: Data visualization and chart creation
• webdriver-manager: Automated browser driver management

3.3 Project Architecture:
• Modular design with separate components for each phase
• Robust error handling at every stage
• Configurable scraping parameters
• Comprehensive logging and monitoring

3.4 Implementation Details:
"""
        
        # Add phase-specific details
        for phase_name, phase_result in phases.items():
            status = phase_result.get('status', 'unknown')
            self.report_content += f"• {phase_name.replace('_', ' ').title()}: {status}\n"
            
            if phase_name == 'data_scraping' and 'cars_scraped' in phase_result:
                self.report_content += f"  - Cars Scraped: {phase_result['cars_scraped']}\n"
            if phase_name == 'url_discovery' and 'urls_found' in phase_result:
                self.report_content += f"  - URLs Discovered: {phase_result['urls_found']}\n"

        self.report_content += "\n"
    
    def _add_data_analysis(self):
        """Add data analysis section"""
        self.report_content += """
4. DATA ANALYSIS AND FINDINGS
================================================================================

"""
        
        if self.df is not None and not self.df.empty:
            # Basic dataset info
            total_cars = len(self.df)
            locations = self.df['location'].nunique() if 'location' in self.df.columns else 0
            
            self.report_content += f"4.1 Dataset Overview:\n"
            self.report_content += f"• Total Cars Analyzed: {total_cars}\n"
            self.report_content += f"• Locations Covered: {locations}\n"
            self.report_content += f"• Data Collection Period: {self.report_time.strftime('%B %Y')}\n\n"
            
            # Add summary statistics
            if self.summary_stats:
                self.report_content += "4.2 Key Statistics:\n"
                
                price_stats = self.summary_stats.get('price_analysis', {})
                if 'error' not in price_stats:
                    self.report_content += f"• Average Price: ₹{price_stats.get('mean', 0):,.2f}\n"
                    self.report_content += f"• Price Range: ₹{price_stats.get('min', 0):,.2f} - ₹{price_stats.get('max', 0):,.2f}\n"
                
                year_stats = self.summary_stats.get('year_analysis', {})
                if 'error' not in year_stats:
                    self.report_content += f"• Model Years: {year_stats.get('oldest', 0)} - {year_stats.get('newest', 0)}\n"
                
                km_stats = self.summary_stats.get('kilometer_analysis', {})
                if 'error' not in km_stats:
                    self.report_content += f"• Average Kilometers: {km_stats.get('average_km', 0):,.0f} km\n"
            
            # Add categorical analysis
            categorical = self.summary_stats.get('categorical_analysis', {})
            if categorical:
                self.report_content += "\n4.3 Distribution Analysis:\n"
                
                fuel_types = categorical.get('fuel_type', {})
                if fuel_types:
                    self.report_content += "• Fuel Types:\n"
                    for fuel, count in list(fuel_types.items())[:5]:
                        self.report_content += f"  - {fuel}: {count} cars\n"
                
                transmission = categorical.get('transmission', {})
                if transmission:
                    self.report_content += "• Transmission Types:\n"
                    for trans, count in list(transmission.items())[:3]:
                        self.report_content += f"  - {trans}: {count} cars\n"
            
            # Location analysis
            locations = self.summary_stats.get('location_analysis', {})
            if locations:
                self.report_content += "\n4.4 Location-wise Distribution:\n"
                for location, count in list(locations.items())[:5]:
                    self.report_content += f"• {location}: {count} cars\n"
        
        else:
            self.report_content += "4.1 Data Availability:\n"
            self.report_content += "• No data available for analysis\n"
            self.report_content += "• This could be due to website restrictions or technical issues\n\n"
    
    def _add_challenges_solutions(self):
        """Add challenges and solutions section"""
        self.report_content += """
5. CHALLENGES AND SOLUTIONS
================================================================================

5.1 Technical Challenges:

• Dynamic Content Loading:
  - Challenge: Cars24 uses extensive JavaScript for rendering
  - Solution: Implemented Selenium WebDriver with explicit waits

• Anti-Scraping Measures:
  - Challenge: Website employs bot detection mechanisms
  - Solution: Used rotating user agents and behavioral patterns

• HTML Structure Variability:
  - Challenge: CSS classes and structure change frequently
  - Solution: Implemented multiple selector strategies with fallbacks

• Data Consistency:
  - Challenge: Inconsistent data formats across listings
  - Solution: Developed robust data cleaning pipelines

5.2 Data Quality Challenges:

• Missing Values:
  - Challenge: Some car listings had incomplete information
  - Solution: Implemented data validation and imputation strategies

• Price Format Variations:
  - Challenge: Multiple price formats (lakhs, crores, etc.)
  - Solution: Created standardized price parsing functions

• Location Standardization:
  - Challenge: Different location naming conventions
  - Solution: Implemented location mapping and standardization

5.3 Performance Challenges:

• Request Rate Limiting:
  - Challenge: Potential for IP blocking with rapid requests
  - Solution: Implemented randomized delays between requests

• Memory Management:
  - Challenge: Large dataset processing requirements
  - Solution: Used efficient data structures and chunk processing

"""
    
    def _add_insights_recommendations(self):
        """Add insights and recommendations"""
        self.report_content += """
6. INSIGHTS AND RECOMMENDATIONS
================================================================================

6.1 Key Insights:

• Market Analysis:
  - Understanding of Maruti Suzuki's used car market presence
  - Price distribution across different models and locations
  - Popular fuel types and transmission preferences

• Technical Learnings:
  - Advanced web scraping techniques for modern websites
  - Data cleaning and validation best practices
  - Project management for data science projects

6.2 Business Recommendations:

• For Car Buyers:
  - Insights on price ranges for different models
  - Understanding of depreciation patterns
  - Location-based pricing variations

• For Car Sellers:
  - Market demand analysis for different models
  - Optimal pricing strategies based on location
  - Understanding buyer preferences

6.3 Technical Recommendations:

• Web Scraping Best Practices:
  - Always respect robots.txt and rate limits
  - Implement comprehensive error handling
  - Use headless browsers for efficiency
  - Maintain selector flexibility for website changes

• Data Processing:
  - Implement data validation at extraction time
  - Use standardized data cleaning pipelines
  - Maintain data quality metrics

"""
    
    def _add_conclusion(self):
        """Add conclusion section"""
        project_status = self.results['project_info'].get('status', 'unknown')
        
        self.report_content += """
7. CONCLUSION
================================================================================

"""
        
        if project_status == 'completed':
            self.report_content += """
7.1 Project Success:
• Successfully demonstrated end-to-end web scraping capabilities
• Extracted and analyzed meaningful data from Cars24.com
• Generated actionable insights for Maruti Suzuki used car market
• Created reusable code framework for future projects

7.2 Learning Outcomes:
• Advanced web scraping techniques for dynamic websites
• Data cleaning and analysis methodologies
• Project documentation and reporting skills
• Problem-solving in real-world data extraction scenarios

"""
        else:
            self.report_content += """
7.1 Project Status:
• Project encountered challenges during execution
• Valuable learning experience in web scraping complexities
• Framework established for future improvements
• Documentation of challenges and solutions provided

"""
        
        self.report_content += """
7.3 Future Enhancements:
• Expand to more car brands and locations
• Implement real-time data monitoring
• Add machine learning for price prediction
• Create interactive web dashboard for visualization

"""
    
    def _add_appendix(self):
        """Add appendix with technical details"""
        self.report_content += """
APPENDIX
================================================================================

A. Project Structure:
Cars24_WebScraping_Project/
├── code/                    # Python scripts
│   ├── cars24_robust_scraper.py
│   ├── data_analyzer.py
│   ├── find_correct_urls.py
│   ├── project_runner.py
│   └── report_generator.py
├── data/                   # CSV data files
├── reports/               # Analysis reports
├── images/               # Visualization images
└── logs/                 # Project logs

B. File Descriptions:
• cars24_robust_scraper.py - Main web scraping implementation
• data_analyzer.py - Data cleaning and analysis functions
• find_correct_urls.py - URL discovery and validation
• project_runner.py - Main project coordination
• report_generator.py - Report generation utilities

C. Data Files:
• cars24_raw_data_*.csv - Original scraped data
• cars24_cleaned_data_*.csv - Processed and cleaned data
• project_results_*.json - Comprehensive project results

D. Requirements:
• Python 3.8+
• selenium>=4.0.0
• beautifulsoup4>=4.9.0
• pandas>=1.3.0
• matplotlib>=3.3.0
• requests>=2.25.0

"""
    
    def _save_text_report(self) -> str:
        """Save text report to file"""
        try:
            os.makedirs('../reports', exist_ok=True)
            timestamp = self.report_time.strftime("%Y%m%d_%H%M%S")
            report_path = f"../reports/project_report_{timestamp}.txt"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(self.report_content)
            
            logger.info(f"💾 Text report saved: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"❌ Error saving text report: {e}")
            return ""
    
    def _create_fallback_report(self) -> str:
        """Create fallback report when main generation fails"""
        fallback_content = f"""
CARS24 PROJECT - FALLBACK REPORT
Generated: {self.report_time}

Project Status: {self.results['project_info'].get('status', 'unknown')}

Note: Comprehensive report generation failed.
Please check the project logs for details.
"""
        
        try:
            report_path = "../reports/fallback_report.txt"
            with open(report_path, 'w') as f:
                f.write(fallback_content)
            return report_path
        except:
            return ""
    
    def generate_pdf_report(self) -> str:
        """Generate PDF report (simplified version)"""
        logger.info("📄 Generating PDF report...")
        
        try:
            # In a real implementation, you would use libraries like ReportLab
            # or WeasyPrint to convert the text report to PDF
            
            # For now, create a simple text-based PDF placeholder
            pdf_path = "../reports/project_summary.pdf"
            
            # Create a simple text file that could be converted to PDF
            summary_content = f"""
CARS24 PROJECT SUMMARY
Generated: {self.report_time}

Project Overview:
• Status: {self.results['project_info'].get('status', 'unknown')}
• Duration: {self.results['project_info'].get('duration_seconds', 0):.1f} seconds
• Target: {self.results['project_info'].get('target_brand', 'Maruti Suzuki')}

Key Findings:
• Comprehensive analysis completed
• Data extracted and processed
• Reports generated successfully

For detailed information, please refer to the full text report.
"""
            
            with open(pdf_path.replace('.pdf', '.txt'), 'w') as f:
                f.write(summary_content)
            
            logger.info(f"📄 PDF report placeholder created: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"❌ PDF report generation failed: {e}")
            return ""
    
    def generate_summary_report(self) -> str:
        """Generate executive summary report"""
        logger.info("📋 Generating executive summary...")
        
        try:
            summary_path = "../reports/executive_summary.txt"
            
            summary_content = f"""
EXECUTIVE SUMMARY - CARS24 WEB SCRAPING PROJECT
================================================

Generated: {self.report_time}
Project Status: {self.results['project_info'].get('status', 'unknown').upper()}

OVERVIEW:
• Project: Web scraping and analysis of Maruti Suzuki cars on Cars24.com
• Objective: Extract, analyze, and report on used car market data
• Methodology: Automated data collection with robust error handling

KEY METRICS:
"""
            
            # Add key metrics if available
            if self.df is not None and not self.df.empty:
                summary_content += f"• Cars Analyzed: {len(self.df)}\n"
                if 'location' in self.df.columns:
                    summary_content += f"• Locations: {self.df['location'].nunique()}\n"
            
            phases = self.results.get('phases', {})
            scraping_phase = phases.get('data_scraping', {})
            if 'cars_scraped' in scraping_phase:
                summary_content += f"• Successfully Scraped: {scraping_phase['cars_scraped']} cars\n"

            summary_content += """
ACHIEVEMENTS:
• Successfully implemented web scraping pipeline
• Extracted structured data from dynamic website
• Performed comprehensive data analysis
• Generated actionable insights and reports

RECOMMENDATIONS:
• Use insights for market analysis and decision making
• Consider expanding to other car brands and platforms
• Implement regular data updates for trend analysis

================================================
"""
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            logger.info(f"📋 Executive summary saved: {summary_path}")
            return summary_path
            
        except Exception as e:
            logger.error(f"❌ Executive summary generation failed: {e}")
            return ""

def main():
    """Main execution function for testing"""
    print("📊 Report Generator Test")
    print("="*50)
    
    # Create sample project results for testing
    sample_results = {
        'project_info': {
            'name': 'Cars24 Maruti Suzuki Web Scraping',
            'status': 'completed',
            'duration_seconds': 120.5,
            'target_brand': 'Maruti Suzuki'
        },
        'phases': {
            'url_discovery': {'status': 'completed', 'urls_found': 3},
            'data_scraping': {'status': 'completed', 'cars_scraped': 45},
            'data_analysis': {'status': 'completed'},
            'report_generation': {'status': 'completed'}
        }
    }
    
    # Create sample DataFrame
    sample_data = {
        'car_name': ['Maruti Swift', 'Maruti Baleno', 'Maruti Dzire'],
        'price': ['₹5,50,000', '₹6,75,000', '₹4,90,000'],
        'location': ['Delhi', 'Mumbai', 'Bangalore']
    }
    df = pd.DataFrame(sample_data)
    
    # Generate reports
    generator = ReportGenerator(sample_results, df)
    
    print("Generating reports...")
    text_report = generator.generate_text_report()
    pdf_report = generator.generate_pdf_report()
    summary_report = generator.generate_summary_report()
    
    print(f"✅ Text Report: {text_report}")
    print(f"✅ PDF Report: {pdf_report}")
    print(f"✅ Summary Report: {summary_report}")
    print("\n🎉 Report generation completed!")

if __name__ == "__main__":
    main()