"""
Enhanced Project Runner with Robust Error Handling
Coordinates all components with proper fallback mechanisms
"""

import pandas as pd
import json
import logging
import sys
import os
import time
from datetime import datetime
import traceback

# Import project modules
try:
    from cars24_robust_scraper import Cars24Scraper
    from data_analyzer import Cars24DataAnalyzer
    from find_correct_urls import Cars24UrlFinder
    from report_generator import ReportGenerator
except ImportError as e:
    print(f"⚠️ Module import warning: {e}")
    print("🔄 Continuing with fallback modes...")

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cars24_project.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProjectRunner:
    def __init__(self):
        self.project_start_time = datetime.now()
        self.results = {
            'project_info': {
                'name': 'Cars24 Maruti Suzuki Web Scraping',
                'start_time': self.project_start_time.isoformat(),
                'target_brand': 'Maruti Suzuki',
                'status': 'initialized'
            },
            'phases': {}
        }
        
    def ensure_directories(self):
        """Ensure all necessary directories exist"""
        directories = ['../data', '../reports', '../images', '../logs']
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"📁 Created directory: {directory}")
            except Exception as e:
                logger.warning(f"⚠️ Could not create {directory}: {e}")
    
    def phase1_url_discovery(self):
        """Phase 1: URL Discovery with fallback"""
        logger.info("🚀 PHASE 1: URL Discovery")
        
        phase_result = {
            'name': 'URL Discovery',
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        
        try:
            finder = Cars24UrlFinder()
            url_report = finder.run_complete_analysis()
            
            if url_report and url_report.get('recommended_urls'):
                location_urls = url_report['recommended_urls']
                phase_result['status'] = 'completed'
                phase_result['urls_found'] = len(location_urls)
                phase_result['urls'] = location_urls
                phase_result['method'] = 'automated_discovery'
                
                logger.info(f"✅ URL discovery completed: {len(location_urls)} URLs found")
            else:
                # Use fallback URLs
                location_urls = {
                    "Delhi": "https://www.cars24.com/buy-used-maruti-suzuki-cars-delhi/",
                    "Mumbai": "https://www.cars24.com/buy-used-maruti-suzuki-cars-mumbai/",
                    "Bangalore": "https://www.cars24.com/buy-used-maruti-suzuki-cars-bangalore/"
                }
                phase_result['status'] = 'completed_with_fallback'
                phase_result['urls_found'] = len(location_urls)
                phase_result['urls'] = location_urls
                phase_result['method'] = 'fallback'
                
                logger.info("🔄 Using fallback URLs")
            
            self.results['phases']['url_discovery'] = phase_result
            return location_urls
            
        except Exception as e:
            logger.error(f"❌ URL discovery failed: {e}")
            phase_result['status'] = 'failed'
            phase_result['error'] = str(e)
            phase_result['method'] = 'fallback'
            
            # Provide fallback URLs
            location_urls = {
                "Delhi": "https://www.cars24.com/buy-used-maruti-suzuki-cars-delhi/",
                "Mumbai": "https://www.cars24.com/buy-used-maruti-suzuki-cars-mumbai/", 
                "Bangalore": "https://www.cars24.com/buy-used-maruti-suzuki-cars-bangalore/"
            }
            phase_result['urls'] = location_urls
            
            self.results['phases']['url_discovery'] = phase_result
            return location_urls
    
    def phase2_data_scraping(self, location_urls):
        """Phase 2: Data Scraping with robust error handling"""
        logger.info("🚀 PHASE 2: Data Scraping")
        
        phase_result = {
            'name': 'Data Scraping',
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        
        try:
            scraper = Cars24Scraper()
            df = scraper.scrape_multiple_locations(location_urls)
            
            # Save raw data with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_filename = f"../data/cars24_raw_data_{timestamp}.csv"
            
            if not df.empty:
                success = scraper.save_to_csv(df, raw_filename)
                if success:
                    phase_result['status'] = 'completed'
                    phase_result['cars_scraped'] = len(df)
                    phase_result['data_file'] = raw_filename
                    phase_result['locations'] = list(location_urls.keys())
                    
                    logger.info(f"✅ Data scraping completed: {len(df)} cars")
                else:
                    phase_result['status'] = 'completed_with_warnings'
                    phase_result['cars_scraped'] = len(df)
                    phase_result['warning'] = 'Data saved but with issues'
                    
                    logger.warning("⚠️ Data saved with warnings")
            else:
                phase_result['status'] = 'completed_no_data'
                phase_result['cars_scraped'] = 0
                phase_result['warning'] = 'No cars were scraped'
                
                logger.warning("⚠️ No data was scraped")
            
            self.results['phases']['data_scraping'] = phase_result
            return df
            
        except Exception as e:
            logger.error(f"❌ Data scraping failed: {e}")
            phase_result['status'] = 'failed'
            phase_result['error'] = str(e)
            
            # Create empty DataFrame with proper structure
            df = pd.DataFrame(columns=[
                'car_name', 'price', 'kilometers_driven', 'year_of_manufacture',
                'fuel_type', 'transmission', 'location', 'brand', 'scraped_location'
            ])
            phase_result['fallback_data'] = 'empty_dataframe'
            
            self.results['phases']['data_scraping'] = phase_result
            return df
    
    def phase3_data_analysis(self, df):
        """Phase 3: Data Analysis and Cleaning"""
        logger.info("🚀 PHASE 3: Data Analysis")
        
        phase_result = {
            'name': 'Data Analysis',
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        
        try:
            if df.empty:
                phase_result['status'] = 'skipped'
                phase_result['reason'] = 'No data to analyze'
                logger.warning("⚠️ No data for analysis")
                self.results['phases']['data_analysis'] = phase_result
                return None, None
            
            analyzer = Cars24DataAnalyzer(df)
            
            # Clean data
            cleaned_df = analyzer.comprehensive_cleaning()
            
            # Generate analysis
            analysis_results = analyzer.generate_comprehensive_analysis()
            
            # Create visualizations
            viz_success = analyzer.create_visualizations()
            
            # Save cleaned data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cleaned_filename = f"../data/cars24_cleaned_data_{timestamp}.csv"
            cleaned_df.to_csv(cleaned_filename, index=False, encoding='utf-8')
            
            # Save analysis report
            report_success = analyzer.save_analysis_report()
            
            phase_result['status'] = 'completed'
            phase_result['cleaned_data_file'] = cleaned_filename
            phase_result['analysis_performed'] = True
            phase_result['visualizations_created'] = viz_success
            phase_result['report_generated'] = report_success
            
            logger.info("✅ Data analysis completed successfully")
            
            self.results['phases']['data_analysis'] = phase_result
            return cleaned_df, analysis_results
            
        except Exception as e:
            logger.error(f"❌ Data analysis failed: {e}")
            phase_result['status'] = 'failed'
            phase_result['error'] = str(e)
            
            self.results['phases']['data_analysis'] = phase_result
            return df, None
    
    def phase4_report_generation(self, df, analysis_results):
        """Phase 4: Comprehensive Report Generation"""
        logger.info("🚀 PHASE 4: Report Generation")
        
        phase_result = {
            'name': 'Report Generation',
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        
        try:
            # Generate comprehensive report
            report_gen = ReportGenerator(self.results, df, analysis_results)
            
            # Generate different report formats
            pdf_report = report_gen.generate_pdf_report()
            text_report = report_gen.generate_text_report()
            summary_report = report_gen.generate_summary_report()
            
            phase_result['status'] = 'completed'
            phase_result['pdf_report'] = pdf_report
            phase_result['text_report'] = text_report
            phase_result['summary_report'] = summary_report
            
            logger.info("✅ Report generation completed")
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            phase_result['status'] = 'failed'
            phase_result['error'] = str(e)
            
            # Create basic text report as fallback
            try:
                with open('../reports/fallback_report.txt', 'w') as f:
                    f.write(f"Fallback Project Report\nGenerated: {datetime.now()}\n")
                    f.write(f"Status: Partial completion\n")
                    f.write(f"Error in report generation: {e}\n")
                phase_result['fallback_report'] = '../reports/fallback_report.txt'
            except:
                pass
        
        self.results['phases']['report_generation'] = phase_result
    
    def phase5_finalization(self):
        """Phase 5: Project Finalization and Summary"""
        logger.info("🚀 PHASE 5: Project Finalization")
        
        # Update project completion info
        self.results['project_info']['end_time'] = datetime.now().isoformat()
        self.results['project_info']['duration_seconds'] = (
            datetime.now() - self.project_start_time
        ).total_seconds()
        
        # Determine overall project status
        phases = self.results['phases']
        statuses = [phase.get('status', 'unknown') for phase in phases.values()]
        
        if all(status == 'completed' for status in statuses):
            self.results['project_info']['status'] = 'completed'
        elif any(status == 'failed' for status in statuses):
            self.results['project_info']['status'] = 'completed_with_errors'
        else:
            self.results['project_info']['status'] = 'partially_completed'
        
        # Save final project results
        self.save_project_results()
        
        # Print final summary
        self.print_final_summary()
    
    def save_project_results(self):
        """Save comprehensive project results"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"../reports/project_results_{timestamp}.json"
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"💾 Project results saved to {results_file}")
            return results_file
            
        except Exception as e:
            logger.error(f"❌ Error saving project results: {e}")
            return None
    
    def print_final_summary(self):
        """Print comprehensive project summary"""
        print("\n" + "="*80)
        print("🎊 CARS24 WEB SCRAPING PROJECT - FINAL SUMMARY")
        print("="*80)
        
        project_info = self.results['project_info']
        phases = self.results['phases']
        
        print(f"📋 PROJECT OVERVIEW:")
        print(f"   Name: {project_info.get('name', 'N/A')}")
        print(f"   Status: {project_info.get('status', 'unknown')}")
        print(f"   Duration: {project_info.get('duration_seconds', 0):.1f} seconds")
        print(f"   Target Brand: {project_info.get('target_brand', 'N/A')}")
        
        print(f"\n📊 PHASE RESULTS:")
        for phase_name, phase_result in phases.items():
            status = phase_result.get('status', 'unknown')
            status_icon = "✅" if status == 'completed' else "⚠️" if 'completed' in status else "❌"
            print(f"   {status_icon} {phase_name}: {status}")
            
            # Phase-specific details
            if phase_name == 'data_scraping' and 'cars_scraped' in phase_result:
                print(f"      Cars Scraped: {phase_result['cars_scraped']}")
            if phase_name == 'url_discovery' and 'urls_found' in phase_result:
                print(f"      URLs Found: {phase_result['urls_found']}")
        
        print(f"\n📁 OUTPUT FILES:")
        for phase_name, phase_result in phases.items():
            if 'data_file' in phase_result:
                print(f"   📄 Data: {phase_result['data_file']}")
            if 'cleaned_data_file' in phase_result:
                print(f"   📊 Cleaned Data: {phase_result['cleaned_data_file']}")
            if 'pdf_report' in phase_result:
                print(f"   📋 PDF Report: {phase_result['pdf_report']}")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        if project_info.get('status') == 'completed':
            print("   ✅ Project completed successfully!")
            print("   📈 Check the generated reports and visualizations")
        elif project_info.get('status') == 'completed_with_errors':
            print("   ⚠️ Project completed with some errors")
            print("   🔧 Check the log files for details")
        else:
            print("   ❌ Project encountered issues")
            print("   🛠️ Review the error messages and try again")
        
        print("="*80)
    
    def run_complete_project(self):
        """Run the complete project workflow"""
        logger.info("🎯 Starting Complete Cars24 Web Scraping Project")
        logger.info(f"⏰ Start Time: {self.project_start_time}")
        
        try:
            # Setup
            self.ensure_directories()
            
            # Phase 1: URL Discovery
            location_urls = self.phase1_url_discovery()
            
            # Phase 2: Data Scraping
            df = self.phase2_data_scraping(location_urls)
            
            # Phase 3: Data Analysis
            cleaned_df, analysis_results = self.phase3_data_analysis(df)
            
            # Phase 4: Report Generation
            self.phase4_report_generation(
                cleaned_df if cleaned_df is not None else df, 
                analysis_results
            )
            
            # Phase 5: Finalization
            self.phase5_finalization()
            
            logger.info("🎊 Project execution completed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Project execution failed: {e}")
            logger.error(traceback.format_exc())
            
            # Update project status to failed
            self.results['project_info']['status'] = 'failed'
            self.results['project_info']['error'] = str(e)
            self.results['project_info']['end_time'] = datetime.now().isoformat()
            
            self.save_project_results()
            self.print_final_summary()
            
            return False

def main():
    """Main execution function"""
    print("🚀 CARS24 WEB SCRAPING PROJECT RUNNER")
    print("="*60)
    print("This will run the complete web scraping project:")
    print("1. URL Discovery")
    print("2. Data Scraping") 
    print("3. Data Analysis")
    print("4. Report Generation")
    print("5. Project Summary")
    print("="*60)
    
    # Confirm execution
    try:
        input("Press Enter to continue or Ctrl+C to cancel...")
    except KeyboardInterrupt:
        print("\n❌ Project execution cancelled")
        return
    
    # Run project
    runner = ProjectRunner()
    success = runner.run_complete_project()
    
    if success:
        print("\n🎉 PROJECT COMPLETED SUCCESSFULLY!")
        print("Check the generated files in the data, reports, and images folders.")
    else:
        print("\n⚠️ PROJECT COMPLETED WITH ERRORS")
        print("Review the log file for details and try again.")

if __name__ == "__main__":
    main()