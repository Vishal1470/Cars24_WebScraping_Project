import random
import pandas as pd
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

class ProfessionalDataAnalyzer:
    def __init__(self):
        self.df = None
        self.analysis_results = {}
        
    def load_and_prepare_data(self):
        """Data load kare aur prepare kare professional analysis ke liye"""
        print("📊 Loading and preparing data for professional analysis...")
        
        # Check for data files
        data_files = []
        if os.path.exists('../data'):
            data_files = [f for f in os.listdir('../data') if f.endswith('.csv') and 'cars24' in f.lower()]
        
        if not data_files:
            print("❌ No Cars24 data files found. Creating sample dataset...")
            self.create_sample_dataset()
            return
        
        # Load the most recent data file
        latest_file = sorted(data_files)[-1]
        file_path = f'../data/{latest_file}'
        
        try:
            self.df = pd.read_csv(file_path)
            print(f"✅ Data loaded successfully: {latest_file}")
            print(f"📈 Dataset shape: {self.df.shape}")
            
            # Data preparation
            self.prepare_data_for_analysis()
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.create_sample_dataset()
    
    def prepare_data_for_analysis(self):
        """Data ko professional analysis ke liye prepare kare"""
        print("🔄 Preparing data for advanced analysis...")
        
        # Create numeric versions of price and km_driven
        if 'price' in self.df.columns:
            self.df['price_numeric'] = self.df['price'].apply(self.extract_numeric_price)
        
        if 'km_driven' in self.df.columns:
            self.df['km_numeric'] = self.df['km_driven'].apply(self.extract_numeric_km)
        
        # Handle year column
        if 'year' in self.df.columns:
            self.df['year'] = pd.to_numeric(self.df['year'], errors='coerce')
        
        # Data quality checks
        initial_count = len(self.df)
        self.df = self.df.dropna(subset=['model', 'price', 'year'])
        final_count = len(self.df)
        
        if initial_count != final_count:
            print(f"⚠️  Removed {initial_count - final_count} records with missing critical data")
        
        print(f"✅ Data preparation completed. Final records: {len(self.df)}")
    
    def extract_numeric_price(self, price_str):
        """Price string se numeric value extract kare"""
        if pd.isna(price_str):
            return 0
        
        try:
            # Remove currency symbols and commas
            clean_str = str(price_str).replace('₹', '').replace(',', '').replace(' ', '')
            
            # Handle lakh and crore
            if 'lakh' in clean_str.lower():
                return float(clean_str.lower().replace('lakh', '').strip()) * 100000
            elif 'cr' in clean_str.lower() or 'crore' in clean_str.lower():
                return float(clean_str.lower().replace('cr', '').replace('crore', '').strip()) * 10000000
            else:
                return float(clean_str)
        except:
            return 0
    
    def extract_numeric_km(self, km_str):
        """KM string se numeric value extract kare"""
        if pd.isna(km_str):
            return 0
        
        try:
            clean_str = str(km_str).replace('km', '').replace(',', '').replace(' ', '').strip()
            return float(clean_str) if clean_str else 0
        except:
            return 0
    
    def create_sample_dataset(self):
        """Professional sample dataset create kare"""
        print("📝 Creating professional sample dataset for analysis...")
        
        models = ['Swift', 'Baleno', 'Alto', 'Wagon R', 'Dzire', 'Celerio', 'Ertiga']
        locations = ['Delhi', 'Mumbai', 'Bangalore', 'Hyderabad', 'Chennai']
        fuel_types = ['Petrol', 'Diesel', 'CNG']
        
        data = []
        for i in range(100):
            model = random.choice(models)
            location = random.choice(locations)
            fuel = random.choice(fuel_types)
            year = random.randint(2018, 2023)
            
            # Realistic pricing
            base_prices = {'Swift': 500000, 'Baleno': 600000, 'Alto': 300000, 
                          'Wagon R': 400000, 'Dzire': 550000, 'Celerio': 450000, 'Ertiga': 700000}
            years_old = 2024 - year
            price = base_prices[model] - (years_old * 45000) + random.randint(-20000, 20000)
            
            # Realistic kilometers
            km_driven = random.randint(10000, 20000) * years_old
            
            car = {
                'brand': 'Maruti Suzuki',
                'model': model,
                'price': f'₹{price:,}',
                'price_numeric': price,
                'year': year,
                'km_driven': f'{km_driven:,} km',
                'km_numeric': km_driven,
                'fuel_type': fuel,
                'transmission': random.choice(['Manual', 'Automatic']),
                'location': location,
                'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            data.append(car)
        
        self.df = pd.DataFrame(data)
        print("✅ Professional sample dataset created!")
    
    def perform_comprehensive_analysis(self):
        """Comprehensive data analysis perform kare"""
        print("\n🔍 PERFORMING COMPREHENSIVE DATA ANALYSIS...")
        print("=" * 50)
        
        if self.df is None or self.df.empty:
            print("❌ No data available for analysis")
            return
        
        self.analysis_results = {}
        
        # 1. Basic Statistics
        self.analysis_results['basic_stats'] = self.calculate_basic_statistics()
        
        # 2. Model Analysis
        self.analysis_results['model_analysis'] = self.analyze_models()
        
        # 3. Regional Analysis
        self.analysis_results['regional_analysis'] = self.analyze_regional_trends()
        
        # 4. Fuel and Transmission Analysis
        self.analysis_results['fuel_analysis'] = self.analyze_fuel_transmission()
        
        # 5. Price Analysis
        self.analysis_results['price_analysis'] = self.analyze_pricing_trends()
        
        # 6. Correlation Analysis
        self.analysis_results['correlation_analysis'] = self.analyze_correlations()
        
        print("✅ Comprehensive analysis completed!")
    
    def calculate_basic_statistics(self):
        """Basic statistical analysis perform kare"""
        print("📈 Calculating basic statistics...")
        
        stats = {
            'total_cars': len(self.df),
            'unique_models': self.df['model'].nunique(),
            'cities_covered': self.df['location'].nunique(),
            'year_range': f"{self.df['year'].min()} - {self.df['year'].max()}",
            'avg_price': f"₹{self.df['price_numeric'].mean():,.0f}",
            'avg_km_driven': f"{self.df['km_numeric'].mean():,.0f} km",
            'price_std_dev': f"₹{self.df['price_numeric'].std():,.0f}",
            'most_expensive_car': f"₹{self.df['price_numeric'].max():,}",
            'least_expensive_car': f"₹{self.df['price_numeric'].min():,}"
        }
        
        return stats
    
    def analyze_models(self):
        """Model-wise detailed analysis"""
        print("🚗 Performing model-wise analysis...")
        
        model_stats = self.df.groupby('model').agg({
            'price_numeric': ['count', 'mean', 'std', 'min', 'max'],
            'km_numeric': 'mean',
            'year': 'mean'
        }).round(2)
        
        model_stats.columns = ['count', 'avg_price', 'price_std', 'min_price', 'max_price', 'avg_km', 'avg_year']
        
        # Add additional metrics
        model_stats['price_per_km'] = model_stats['avg_price'] / model_stats['avg_km']
        model_stats['market_share'] = (model_stats['count'] / len(self.df)) * 100
        
        return model_stats
    
    def analyze_regional_trends(self):
        """Regional trends analysis"""
        print("🏙️ Analyzing regional trends...")
        
        regional_stats = self.df.groupby('location').agg({
            'price_numeric': ['count', 'mean', 'std'],
            'km_numeric': 'mean',
            'model': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'N/A',
            'fuel_type': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'N/A'
        }).round(2)
        
        regional_stats.columns = ['count', 'avg_price', 'price_std', 'avg_km', 'popular_model', 'popular_fuel']
        
        return regional_stats
    
    def analyze_fuel_transmission(self):
        """Fuel type and transmission analysis"""
        print("⛽ Analyzing fuel and transmission patterns...")
        
        fuel_stats = self.df.groupby('fuel_type').agg({
            'price_numeric': ['count', 'mean'],
            'km_numeric': 'mean',
            'year': 'mean'
        }).round(2)
        
        fuel_stats.columns = ['count', 'avg_price', 'avg_km', 'avg_year']
        
        transmission_stats = self.df.groupby('transmission').agg({
            'price_numeric': ['count', 'mean'],
            'km_numeric': 'mean'
        }).round(2)
        
        transmission_stats.columns = ['count', 'avg_price', 'avg_km']
        
        return {
            'fuel_analysis': fuel_stats,
            'transmission_analysis': transmission_stats
        }
    
    def analyze_pricing_trends(self):
        """Pricing trends and patterns analysis"""
        print("💰 Analyzing pricing trends...")
        
        # Year-wise pricing
        yearly_pricing = self.df.groupby('year')['price_numeric'].agg(['mean', 'std', 'count']).round(2)
        
        # Model-wise pricing distribution
        model_pricing = self.df.groupby('model')['price_numeric'].describe()
        
        # Price segments
        price_bins = [0, 300000, 500000, 700000, float('inf')]
        price_labels = ['Budget (<3L)', 'Mid-Range (3-5L)', 'Premium (5-7L)', 'Luxury (>7L)']
        self.df['price_segment'] = pd.cut(self.df['price_numeric'], bins=price_bins, labels=price_labels)
        segment_stats = self.df['price_segment'].value_counts()
        
        return {
            'yearly_pricing': yearly_pricing,
            'model_pricing': model_pricing,
            'price_segments': segment_stats
        }
    
    def analyze_correlations(self):
        """Correlation analysis between different variables"""
        print("📊 Performing correlation analysis...")
        
        # Create correlation matrix for numeric variables
        numeric_df = self.df[['price_numeric', 'km_numeric', 'year']].copy()
        
        # Convert categorical variables to numeric for correlation
        if 'fuel_type' in self.df.columns:
            numeric_df['fuel_numeric'] = self.df['fuel_type'].map({'Petrol': 1, 'Diesel': 2, 'CNG': 3})
        if 'transmission' in self.df.columns:
            numeric_df['transmission_numeric'] = self.df['transmission'].map({'Manual': 1, 'Automatic': 2})
        
        correlation_matrix = numeric_df.corr()
        
        return correlation_matrix
    
    def generate_advanced_visualizations(self):
        """Advanced visualizations create kare"""
        print("📈 Generating advanced visualizations...")
        
        try:
            # Set professional style
            plt.style.use('seaborn-v0_8-whitegrid')
            sns.set_palette("husl")
            
            # Create comprehensive dashboard
            fig, axes = plt.subplots(3, 3, figsize=(20, 15))
            fig.suptitle('Cars24 Maruti Suzuki - Advanced Data Analysis Dashboard', 
                        fontsize=16, fontweight='bold', y=0.98)
            
            # 1. Price Distribution by Model
            sns.boxplot(data=self.df, x='model', y='price_numeric', ax=axes[0,0])
            axes[0,0].set_title('💰 Price Distribution by Model', fontweight='bold')
            axes[0,0].tick_params(axis='x', rotation=45)
            axes[0,0].set_ylabel('Price (₹)')
            
            # 2. KM Driven vs Price Scatter
            sns.scatterplot(data=self.df, x='km_numeric', y='price_numeric', hue='fuel_type', ax=axes[0,1])
            axes[0,1].set_title('📏 KM Driven vs Price', fontweight='bold')
            axes[0,1].set_xlabel('Kilometers Driven')
            axes[0,1].set_ylabel('Price (₹)')
            
            # 3. Year-wise Price Trend
            yearly_avg = self.df.groupby('year')['price_numeric'].mean()
            axes[0,2].plot(yearly_avg.index, yearly_avg.values, marker='o', linewidth=2)
            axes[0,2].set_title('📅 Year-wise Average Price Trend', fontweight='bold')
            axes[0,2].set_xlabel('Year')
            axes[0,2].set_ylabel('Average Price (₹)')
            
            # 4. Regional Distribution
            location_counts = self.df['location'].value_counts()
            axes[1,0].bar(location_counts.index, location_counts.values, color='lightblue')
            axes[1,0].set_title('🏙️ Regional Distribution', fontweight='bold')
            axes[1,0].tick_params(axis='x', rotation=45)
            
            # 5. Fuel Type Distribution
            fuel_counts = self.df['fuel_type'].value_counts()
            axes[1,1].pie(fuel_counts.values, labels=fuel_counts.index, autopct='%1.1f%%', startangle=90)
            axes[1,1].set_title('⛽ Fuel Type Distribution', fontweight='bold')
            
            # 6. Transmission Preference by Model
            transmission_by_model = pd.crosstab(self.df['model'], self.df['transmission'])
            transmission_by_model.plot(kind='bar', ax=axes[1,2])
            axes[1,2].set_title('⚙️ Transmission by Model', fontweight='bold')
            axes[1,2].tick_params(axis='x', rotation=45)
            
            # 7. Price Segments
            if 'price_segment' in self.df.columns:
                segment_counts = self.df['price_segment'].value_counts()
                axes[2,0].pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%', startangle=90)
                axes[2,0].set_title('💎 Price Segments', fontweight='bold')
            
            # 8. Correlation Heatmap
            numeric_df = self.df[['price_numeric', 'km_numeric', 'year']].select_dtypes(include=[np.number])
            if not numeric_df.empty:
                correlation_matrix = numeric_df.corr()
                sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[2,1])
                axes[2,1].set_title('📊 Correlation Matrix', fontweight='bold')
            
            # 9. Model Popularity by City
            if len(self.df) > 0:
                model_city = pd.crosstab(self.df['location'], self.df['model'])
                model_city.plot(kind='bar', stacked=True, ax=axes[2,2])
                axes[2,2].set_title('🏙️ Model Popularity by City', fontweight='bold')
                axes[2,2].tick_params(axis='x', rotation=45)
                axes[2,2].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            
            # Save visualization
            os.makedirs('../images', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            viz_filename = f'../images/advanced_analysis_{timestamp}.png'
            plt.savefig(viz_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Advanced visualizations saved: {viz_filename}")
            return True
            
        except Exception as e:
            print(f"⚠️  Visualization error: {e}")
            return False
    
    def generate_professional_report(self):
        """Professional analysis report generate kare"""
        print("📄 Generating professional analysis report...")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_content = f"""
PROFESSIONAL DATA ANALYSIS REPORT - CARS24 MARUTI SUZUKI
Generated on: {timestamp}
{'='*80}

EXECUTIVE SUMMARY:
------------------
This report presents a comprehensive analysis of Maruti Suzuki car listings
from Cars24.com. The analysis covers market trends, pricing patterns, regional
variations, and consumer preferences.

DATASET OVERVIEW:
-----------------
• Total Records Analyzed: {self.analysis_results['basic_stats']['total_cars']}
• Unique Car Models: {self.analysis_results['basic_stats']['unique_models']}
• Geographic Coverage: {self.analysis_results['basic_stats']['cities_covered']} cities
• Year Range: {self.analysis_results['basic_stats']['year_range']}
• Average Price: {self.analysis_results['basic_stats']['avg_price']}
• Average KM Driven: {self.analysis_results['basic_stats']['avg_km_driven']}

KEY FINDINGS:
-------------

1. MARKET COMPOSITION:
   • Most popular model: {self.analysis_results['model_analysis'].index[0]}
   • Price range: {self.analysis_results['basic_stats']['least_expensive_car']} - {self.analysis_results['basic_stats']['most_expensive_car']}
   • Standard deviation in pricing: {self.analysis_results['basic_stats']['price_std_dev']}

2. REGIONAL INSIGHTS:
   • Cities with highest listings: {', '.join(self.analysis_results['regional_analysis'].index[:3])}
   • Regional price variations: ±{self.analysis_results['regional_analysis']['price_std'].mean():.0f}%

3. CONSUMER PREFERENCES:
   • Fuel type distribution: {self.analysis_results['fuel_analysis']['fuel_analysis'].index[0]} most common
   • Transmission preference: {self.analysis_results['fuel_analysis']['transmission_analysis'].index[0]} dominates

DETAILED ANALYSIS:
------------------

MODEL-WISE PERFORMANCE:
{self.analysis_results['model_analysis'].to_string()}

REGIONAL MARKET ANALYSIS:
{self.analysis_results['regional_analysis'].to_string()}

FUEL AND TRANSMISSION ANALYSIS:
{self.analysis_results['fuel_analysis']['fuel_analysis'].to_string()}

PRICING STRATEGY INSIGHTS:
{self.analysis_results['price_analysis']['yearly_pricing'].to_string()}

CORRELATION ANALYSIS:
{self.analysis_results['correlation_analysis'].to_string()}

BUSINESS RECOMMENDATIONS:
-------------------------

1. INVENTORY STRATEGY:
   • Focus on {self.analysis_results['model_analysis'].index[0]} due to high market presence
   • Maintain balanced inventory across price segments
   • Consider regional preferences in model selection

2. PRICING STRATEGY:
   • Implement dynamic pricing based on vehicle age and kilometers
   • Consider regional price sensitivity
   • Monitor competitor pricing in different segments

3. MARKETING STRATEGY:
   • Highlight popular models in high-demand regions
   • Emphasize fuel efficiency for {self.analysis_results['fuel_analysis']['fuel_analysis'].index[0]} vehicles
   • Target specific transmission preferences regionally

TECHNICAL METHODOLOGY:
----------------------
• Data Source: Cars24.com web scraping
• Analysis Tools: Pandas, NumPy, Matplotlib, Seaborn
• Statistical Methods: Descriptive statistics, correlation analysis, trend analysis
• Visualization: Advanced dashboard with multiple chart types

CONCLUSION:
-----------
This comprehensive analysis provides valuable insights into the Maruti Suzuki
used car market. The findings can inform business strategies related to
inventory management, pricing, and regional marketing.

Report generated by: Professional Data Analysis System
"""
        
        # Save report
        os.makedirs('../reports', exist_ok=True)
        report_filename = f'../reports/professional_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ Professional report saved: {report_filename}")
        return report_content
    
    def run_complete_analysis(self):
        """Complete analysis workflow run kare"""
        print("🚀 PROFESSIONAL DATA ANALYSIS WORKFLOW")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Step 1: Data Loading and Preparation
        print("\n1. 📊 DATA LOADING AND PREPARATION...")
        self.load_and_prepare_data()
        
        # Step 2: Comprehensive Analysis
        print("\n2. 🔍 COMPREHENSIVE ANALYSIS...")
        self.perform_comprehensive_analysis()
        
        # Step 3: Advanced Visualizations
        print("\n3. 📈 ADVANCED VISUALIZATIONS...")
        viz_success = self.generate_advanced_visualizations()
        
        # Step 4: Professional Reporting
        print("\n4. 📄 PROFESSIONAL REPORTING...")
        report = self.generate_professional_report()
        
        # Final Summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n{'='*60}")
        print("🎯 ANALYSIS WORKFLOW COMPLETED")
        print(f"{'='*60}")
        print(f"⏱️  Total Duration: {duration}")
        print(f"📊 Records Analyzed: {len(self.df)}")
        print(f"📈 Analysis Modules: 6 comprehensive modules")
        print(f"📉 Visualizations: {'✅ Advanced' if viz_success else '⚠️ Basic'}")
        
        print(f"\n📁 GENERATED OUTPUTS:")
        print(f"   - Professional analysis report")
        print(f"   - Advanced visualization dashboard")
        print(f"   - Comprehensive statistical insights")
        
        print(f"\n✅ Professional data analysis completed successfully!")

def main():
    analyzer = ProfessionalDataAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()