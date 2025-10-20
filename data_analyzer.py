"""
Data Analyzer - Handles various data formats and provides comprehensive analysis
"""

import pandas as pd
import numpy as np
import re
import logging
from typing import Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Cars24DataAnalyzerFixed:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()
        self.cleaning_report = {}
        self.analysis_results = {}
        self.visualization_paths = []
        
    def detect_data_format(self):
        """Detect and fix data format issues"""
        logger.info("🔍 Detecting data format...")
        
        # Check if columns exist, if not try to infer
        if self.df.empty:
            logger.warning("⚠️ Empty DataFrame provided")
            return False
            
        logger.info(f"📊 Initial columns: {list(self.df.columns)}")
        logger.info(f"📊 Initial shape: {self.df.shape}")
        
        # Fix common column name issues
        column_mapping = {}
        for col in self.df.columns:
            col_lower = str(col).lower()
            if 'name' in col_lower or 'car' in col_lower:
                column_mapping[col] = 'car_name'
            elif 'price' in col_lower:
                column_mapping[col] = 'price'
            elif 'km' in col_lower or 'kilometer' in col_lower:
                column_mapping[col] = 'kilometers_driven'
            elif 'year' in col_lower:
                column_mapping[col] = 'year_of_manufacture'
            elif 'fuel' in col_lower:
                column_mapping[col] = 'fuel_type'
            elif 'transmission' in col_lower:
                column_mapping[col] = 'transmission'
            elif 'location' in col_lower:
                column_mapping[col] = 'location'
            elif 'brand' in col_lower:
                column_mapping[col] = 'brand'
        
        if column_mapping:
            self.df = self.df.rename(columns=column_mapping)
            logger.info(f"🔄 Renamed columns: {column_mapping}")
        
        # Ensure required columns exist
        required_columns = ['car_name', 'price', 'kilometers_driven', 'year_of_manufacture', 
                          'fuel_type', 'transmission', 'location']
        
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            logger.warning(f"⚠️ Missing columns: {missing_columns}")
            # Create missing columns with default values
            for col in missing_columns:
                self.df[col] = f"{col.replace('_', ' ').title()} not available"
        
        logger.info(f"✅ Final columns: {list(self.df.columns)}")
        return True
    
    def comprehensive_cleaning(self) -> pd.DataFrame:
        """Run all cleaning steps with enhanced validation"""
        logger.info("🚀 Starting comprehensive data cleaning...")
        
        try:
            # Detect and fix data format first
            if not self.detect_data_format():
                return self.df
            
            initial_count = len(self.df)
            logger.info(f"📊 Initial dataset: {initial_count} records")
            
            # Remove error entries and duplicates
            self.df = self._remove_error_entries()
            self.df = self._remove_duplicates()
            
            # Run cleaning steps
            self._clean_price_column()
            self._clean_kilometers_column()
            self._clean_year_column()
            self._clean_fuel_type()
            self._clean_transmission()
            self._standardize_locations()
            self._extract_car_models()
            
            # Final validation
            self._validate_data_quality()
            
            logger.info(f"✅ Comprehensive cleaning completed. Final: {len(self.df)} records")
            return self.df
            
        except Exception as e:
            logger.error(f"❌ Comprehensive cleaning failed: {e}")
            # Return original dataframe if cleaning fails
            return self.df
    
    def _remove_error_entries(self) -> pd.DataFrame:
        """Remove error entries from scraped data"""
        initial_count = len(self.df)
        
        if 'car_name' in self.df.columns:
            # Remove entries with extraction errors
            mask = ~self.df['car_name'].str.contains('Error|Failed|Check manually', case=False, na=False)
            self.df = self.df[mask].copy()
        
        removed_count = initial_count - len(self.df)
        if removed_count > 0:
            logger.info(f"🧹 Removed {removed_count} error entries")
        
        return self.df
    
    def _remove_duplicates(self) -> pd.DataFrame:
        """Remove duplicate entries"""
        initial_count = len(self.df)
        
        # Remove exact duplicates
        self.df = self.df.drop_duplicates()
        
        # Remove near-duplicates based on key columns
        key_columns = [col for col in ['car_name', 'price', 'location'] if col in self.df.columns]
        if key_columns:
            self.df = self.df.drop_duplicates(subset=key_columns, keep='first')
        
        removed_count = initial_count - len(self.df)
        if removed_count > 0:
            logger.info(f"🧹 Removed {removed_count} duplicate entries")
        
        return self.df
    
    def _clean_price_column(self):
        """Enhanced price cleaning with multiple formats"""
        logger.info("💰 Cleaning price column...")
        
        if 'price' not in self.df.columns:
            logger.warning("❌ Price column not found")
            return
        
        def extract_price(price_str):
            if pd.isna(price_str) or price_str in ['Not Available', 'Price Not Available', 'Check manually', 'N/A']:
                return np.nan
            
            try:
                if isinstance(price_str, str):
                    # Handle lakh and crore notations
                    if 'lakh' in price_str.lower():
                        match = re.search(r'(\d+\.?\d*)\s*lakh', price_str.lower())
                        if match:
                            return float(match.group(1)) * 100000
                    
                    if 'crore' in price_str.lower():
                        match = re.search(r'(\d+\.?\d*)\s*crore', price_str.lower())
                        if match:
                            return float(match.group(1)) * 10000000
                    
                    # Extract numeric values
                    numbers = re.findall(r'\d+', price_str.replace(',', ''))
                    if numbers:
                        return float(''.join(numbers))
                
                return np.nan
            except:
                return np.nan
        
        self.df['price_numeric'] = self.df['price'].apply(extract_price)
        
        # Filter reasonable price range (50,000 to 50,00,000)
        mask = (self.df['price_numeric'] >= 50000) & (self.df['price_numeric'] <= 5000000)
        self.df.loc[~mask, 'price_numeric'] = np.nan
        
        # Report
        cleaned_count = self.df['price_numeric'].notna().sum()
        self.cleaning_report['price'] = {
            'cleaned': cleaned_count,
            'success_rate': f"{(cleaned_count/len(self.df))*100:.1f}%",
            'average_price': f"₹{self.df['price_numeric'].mean():,.0f}" if cleaned_count > 0 else "N/A",
            'price_range': f"₹{self.df['price_numeric'].min():,.0f} - ₹{self.df['price_numeric'].max():,.0f}" if cleaned_count > 0 else "N/A"
        }
        
        logger.info(f"💰 Price cleaning: {cleaned_count}/{len(self.df)} successfully cleaned")
    
    def _clean_kilometers_column(self):
        """Enhanced kilometers cleaning with validation"""
        logger.info("📏 Cleaning kilometers column...")
        
        if 'kilometers_driven' not in self.df.columns:
            logger.warning("❌ Kilometers column not found")
            return
        
        def extract_km(km_str):
            if pd.isna(km_str) or km_str in ['Not Available', 'KM Not Available', 'N/A']:
                return np.nan
            
            try:
                if isinstance(km_str, str):
                    # Extract numbers
                    numbers = re.findall(r'\d+', km_str.replace(',', ''))
                    if numbers:
                        km_value = int(numbers[0])
                        return km_value
                return np.nan
            except:
                return np.nan
        
        self.df['km_numeric'] = self.df['kilometers_driven'].apply(extract_km)
        
        # Filter reasonable values (1 km to 500,000 km)
        mask = (self.df['km_numeric'] >= 1) & (self.df['km_numeric'] <= 500000)
        self.df.loc[~mask, 'km_numeric'] = np.nan
        
        # Report
        cleaned_count = self.df['km_numeric'].notna().sum()
        self.cleaning_report['kilometers'] = {
            'cleaned': cleaned_count,
            'success_rate': f"{(cleaned_count/len(self.df))*100:.1f}%",
            'average_km': f"{self.df['km_numeric'].mean():,.0f} km" if cleaned_count > 0 else "N/A",
            'km_range': f"{self.df['km_numeric'].min():,.0f} - {self.df['km_numeric'].max():,.0f} km" if cleaned_count > 0 else "N/A"
        }
        
        logger.info(f"📏 KM cleaning: {cleaned_count}/{len(self.df)} successfully cleaned")
    
    def _clean_year_column(self):
        """Enhanced year cleaning with validation"""
        logger.info("📅 Cleaning year column...")
        
        if 'year_of_manufacture' not in self.df.columns:
            logger.warning("❌ Year column not found")
            return
        
        def extract_year(year_str):
            if pd.isna(year_str) or year_str in ['Not Available', 'Year Not Available', 'N/A']:
                return np.nan
            
            try:
                if isinstance(year_str, str):
                    # Extract 4-digit years
                    years = re.findall(r'\b(19|20)\d{2}\b', year_str)
                    if years:
                        year_val = int(years[0])
                        # Validate year range (1990-2024)
                        if 1990 <= year_val <= 2024:
                            return year_val
                return np.nan
            except:
                return np.nan
        
        self.df['year_numeric'] = self.df['year_of_manufacture'].apply(extract_year)
        
        # Report
        cleaned_count = self.df['year_numeric'].notna().sum()
        self.cleaning_report['year'] = {
            'cleaned': cleaned_count,
            'success_rate': f"{(cleaned_count/len(self.df))*100:.1f}%",
            'year_range': f"{self.df['year_numeric'].min()} - {self.df['year_numeric'].max()}" if cleaned_count > 0 else "N/A"
        }
        
        logger.info(f"📅 Year cleaning: {cleaned_count}/{len(self.df)} successfully cleaned")
    
    def _clean_fuel_type(self):
        """Standardize fuel types with enhanced mapping"""
        logger.info("⛽ Cleaning fuel type...")
        
        if 'fuel_type' not in self.df.columns:
            logger.warning("❌ Fuel type column not found")
            return
        
        fuel_mapping = {
            'petrol': 'Petrol',
            'diesel': 'Diesel',
            'cng': 'CNG',
            'electric': 'Electric',
            'hybrid': 'Hybrid',
            'cng+petrol': 'CNG + Petrol',
            'petrol+cng': 'Petrol + CNG'
        }
        
        def standardize_fuel(fuel_str):
            if pd.isna(fuel_str) or fuel_str in ['Not Available', 'Fuel Not Available', 'N/A']:
                return 'Unknown'
            
            fuel_lower = str(fuel_str).lower().strip()
            for key, value in fuel_mapping.items():
                if key in fuel_lower:
                    return value
            
            # Try partial matches
            if 'petrol' in fuel_lower:
                return 'Petrol'
            elif 'diesel' in fuel_lower:
                return 'Diesel'
            elif 'cng' in fuel_lower:
                return 'CNG'
            elif 'electric' in fuel_lower:
                return 'Electric'
            else:
                return fuel_str.title()
        
        self.df['fuel_type_clean'] = self.df['fuel_type'].apply(standardize_fuel)
        
        fuel_distribution = self.df['fuel_type_clean'].value_counts()
        logger.info(f"⛽ Fuel distribution: {dict(fuel_distribution)}")
    
    def _clean_transmission(self):
        """Standardize transmission types"""
        logger.info("⚙️ Cleaning transmission...")
        
        if 'transmission' not in self.df.columns:
            logger.warning("❌ Transmission column not found")
            return
        
        transmission_mapping = {
            'manual': 'Manual',
            'automatic': 'Automatic',
            'amt': 'AMT',
            'cvt': 'CVT',
            'dsg': 'DSG'
        }
        
        def standardize_transmission(trans_str):
            if pd.isna(trans_str) or trans_str in ['Not Available', 'Transmission Not Available', 'N/A']:
                return 'Unknown'
            
            trans_lower = str(trans_str).lower().strip()
            for key, value in transmission_mapping.items():
                if key in trans_lower:
                    return value
            
            # Try partial matches
            if 'manual' in trans_lower:
                return 'Manual'
            elif 'automatic' in trans_lower:
                return 'Automatic'
            else:
                return trans_str.title()
        
        self.df['transmission_clean'] = self.df['transmission'].apply(standardize_transmission)
        
        transmission_distribution = self.df['transmission_clean'].value_counts()
        logger.info(f"⚙️ Transmission distribution: {dict(transmission_distribution)}")
    
    def _standardize_locations(self):
        """Standardize location names"""
        logger.info("📍 Standardizing locations...")
        
        if 'location' not in self.df.columns:
            logger.warning("❌ Location column not found")
            return
        
        location_mapping = {
            'delhi': 'Delhi',
            'new delhi': 'Delhi',
            'ncr': 'Delhi NCR',
            'mumbai': 'Mumbai',
            'bangalore': 'Bangalore',
            'bengaluru': 'Bangalore',
            'chennai': 'Chennai',
            'madras': 'Chennai',
            'hyderabad': 'Hyderabad',
            'kolkata': 'Kolkata',
            'calcutta': 'Kolkata',
            'pune': 'Pune',
            'ahmedabad': 'Ahmedabad',
            'jaipur': 'Jaipur'
        }
        
        def standardize_location(loc_str):
            if pd.isna(loc_str):
                return 'Unknown'
            
            loc_lower = str(loc_str).lower().strip()
            for key, value in location_mapping.items():
                if key in loc_lower:
                    return value
            
            return loc_str.title()
        
        self.df['location_clean'] = self.df['location'].apply(standardize_location)
        
        location_distribution = self.df['location_clean'].value_counts()
        logger.info(f"📍 Location distribution: {len(location_distribution)} locations")
    
    def _extract_car_models(self):
        """Extract car models from car names"""
        logger.info("🚗 Extracting car models...")
        
        if 'car_name' not in self.df.columns:
            logger.warning("❌ Car name column not found")
            return
        
        # Common Maruti Suzuki models
        maruti_models = [
            'Swift', 'Baleno', 'Dzire', 'Alto', 'Wagon R', 'Celerio', 'Ertiga',
            'Vitara Brezza', 'S-Cross', 'Ciaz', 'Ignis', 'S-Presso', 'XL6',
            'Omni', 'Eeco', 'Gypsy', '800', 'Zen', 'Esteem', 'Versa'
        ]
        
        def extract_model(car_name):
            if pd.isna(car_name):
                return 'Unknown'
            
            car_name_upper = str(car_name).upper()
            for model in maruti_models:
                if model.upper() in car_name_upper:
                    return model
            
            return 'Other'
        
        self.df['car_model'] = self.df['car_name'].apply(extract_model)
        
        model_distribution = self.df['car_model'].value_counts()
        logger.info(f"🚗 Model distribution: {len(model_distribution)} models")
    
    def _validate_data_quality(self):
        """Validate overall data quality"""
        logger.info("🔍 Validating data quality...")
        
        quality_metrics = {
            'total_records': len(self.df),
            'complete_records': len(self.df.dropna()),
            'price_completeness': self.df['price_numeric'].notna().mean() if 'price_numeric' in self.df.columns else 0,
            'km_completeness': self.df['km_numeric'].notna().mean() if 'km_numeric' in self.df.columns else 0,
            'year_completeness': self.df['year_numeric'].notna().mean() if 'year_numeric' in self.df.columns else 0
        }
        
        self.cleaning_report['data_quality'] = quality_metrics
        
        logger.info(f"📊 Data quality: {quality_metrics['complete_records']}/{quality_metrics['total_records']} complete records")
    
    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        logger.info("📊 Generating comprehensive analysis...")
        
        if self.df.empty:
            return {"error": "No data available for analysis"}
        
        analysis = {
            'dataset_overview': self._get_dataset_overview(),
            'price_analysis': self._analyze_prices(),
            'year_analysis': self._analyze_years(),
            'kilometer_analysis': self._analyze_kilometers(),
            'categorical_analysis': self._analyze_categorical(),
            'location_analysis': self._analyze_locations(),
            'model_analysis': self._analyze_models(),
            'cleaning_report': self.cleaning_report
        }
        
        self.analysis_results = analysis
        return analysis
    
    def _get_dataset_overview(self):
        """Get basic dataset overview"""
        return {
            'total_cars': len(self.df),
            'total_columns': len(self.df.columns),
            'data_types': self.df.dtypes.astype(str).to_dict(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'memory_usage_mb': round(self.df.memory_usage(deep=True).sum() / 1024**2, 2)
        }
    
    def _analyze_prices(self):
        """Analyze price distribution"""
        if 'price_numeric' not in self.df.columns:
            return {"error": "Price data not available"}
        
        price_data = self.df['price_numeric'].dropna()
        
        if len(price_data) == 0:
            return {"error": "No valid price data"}
        
        return {
            'count': len(price_data),
            'mean': round(price_data.mean(), 2),
            'median': round(price_data.median(), 2),
            'min': round(price_data.min(), 2),
            'max': round(price_data.max(), 2),
            'std_dev': round(price_data.std(), 2)
        }
    
    def _analyze_years(self):
        """Analyze year distribution"""
        if 'year_numeric' not in self.df.columns:
            return {"error": "Year data not available"}
        
        year_data = self.df['year_numeric'].dropna()
        
        if len(year_data) == 0:
            return {"error": "No valid year data"}
        
        return {
            'count': len(year_data),
            'oldest': int(year_data.min()),
            'newest': int(year_data.max()),
            'average': round(year_data.mean(), 1)
        }
    
    def _analyze_kilometers(self):
        """Analyze kilometer distribution"""
        if 'km_numeric' not in self.df.columns:
            return {"error": "Kilometer data not available"}
        
        km_data = self.df['km_numeric'].dropna()
        
        if len(km_data) == 0:
            return {"error": "No valid kilometer data"}
        
        return {
            'count': len(km_data),
            'average_km': round(km_data.mean(), 2),
            'median_km': round(km_data.median(), 2),
            'min_km': int(km_data.min()),
            'max_km': int(km_data.max())
        }
    
    def _analyze_categorical(self):
        """Analyze categorical variables"""
        analysis = {}
        
        if 'fuel_type_clean' in self.df.columns:
            analysis['fuel_type'] = self.df['fuel_type_clean'].value_counts().to_dict()
        
        if 'transmission_clean' in self.df.columns:
            analysis['transmission'] = self.df['transmission_clean'].value_counts().to_dict()
        
        return analysis
    
    def _analyze_locations(self):
        """Analyze location distribution"""
        if 'location_clean' in self.df.columns:
            return self.df['location_clean'].value_counts().to_dict()
        elif 'location' in self.df.columns:
            return self.df['location'].value_counts().to_dict()
        return {}
    
    def _analyze_models(self):
        """Analyze car model distribution"""
        if 'car_model' in self.df.columns:
            return self.df['car_model'].value_counts().to_dict()
        return {}
    
    def create_visualizations(self, save_path="images/"):
        """Create comprehensive visualizations"""
        try:
            os.makedirs(save_path, exist_ok=True)
            
            # Set style
            plt.style.use('seaborn-v0_8')
            
            # Create multiple visualization sets
            self._create_main_dashboard(save_path)
            
            logger.info(f"📊 All visualizations saved to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Visualization error: {e}")
            return False
    
    def _create_main_dashboard(self, save_path):
        """Create main dashboard with key metrics"""
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Cars24 Maruti Suzuki - Comprehensive Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # Price distribution
        if 'price_numeric' in self.df.columns and self.df['price_numeric'].notna().sum() > 0:
            axes[0,0].hist(self.df['price_numeric'].dropna(), bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            axes[0,0].set_title('Price Distribution', fontweight='bold')
            axes[0,0].set_xlabel('Price (₹)')
            axes[0,0].set_ylabel('Frequency')
            axes[0,0].ticklabel_format(style='plain', axis='x')
        else:
            axes[0,0].text(0.5, 0.5, 'No Price Data Available', ha='center', va='center', transform=axes[0,0].transAxes)
            axes[0,0].set_title('Price Distribution', fontweight='bold')
        
        # Year distribution
        if 'year_numeric' in self.df.columns and self.df['year_numeric'].notna().sum() > 0:
            axes[0,1].hist(self.df['year_numeric'].dropna(), bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
            axes[0,1].set_title('Year of Manufacture', fontweight='bold')
            axes[0,1].set_xlabel('Year')
            axes[0,1].set_ylabel('Frequency')
        else:
            axes[0,1].text(0.5, 0.5, 'No Year Data Available', ha='center', va='center', transform=axes[0,1].transAxes)
            axes[0,1].set_title('Year of Manufacture', fontweight='bold')
        
        # Kilometer distribution
        if 'km_numeric' in self.df.columns and self.df['km_numeric'].notna().sum() > 0:
            axes[0,2].hist(self.df['km_numeric'].dropna(), bins=20, alpha=0.7, color='orange', edgecolor='black')
            axes[0,2].set_title('Kilometers Driven', fontweight='bold')
            axes[0,2].set_xlabel('Kilometers')
            axes[0,2].set_ylabel('Frequency')
        else:
            axes[0,2].text(0.5, 0.5, 'No KM Data Available', ha='center', va='center', transform=axes[0,2].transAxes)
            axes[0,2].set_title('Kilometers Driven', fontweight='bold')
        
        # Fuel type distribution
        if 'fuel_type_clean' in self.df.columns:
            fuel_counts = self.df['fuel_type_clean'].value_counts()
            if len(fuel_counts) > 0:
                axes[1,0].pie(fuel_counts.values, labels=fuel_counts.index, autopct='%1.1f%%', startangle=90)
                axes[1,0].set_title('Fuel Type Distribution', fontweight='bold')
            else:
                axes[1,0].text(0.5, 0.5, 'No Fuel Type Data', ha='center', va='center', transform=axes[1,0].transAxes)
                axes[1,0].set_title('Fuel Type Distribution', fontweight='bold')
        else:
            axes[1,0].text(0.5, 0.5, 'No Fuel Type Data', ha='center', va='center', transform=axes[1,0].transAxes)
            axes[1,0].set_title('Fuel Type Distribution', fontweight='bold')
        
        # Transmission distribution
        if 'transmission_clean' in self.df.columns:
            trans_counts = self.df['transmission_clean'].value_counts()
            if len(trans_counts) > 0:
                trans_counts.plot(kind='bar', ax=axes[1,1], color='lightcoral')
                axes[1,1].set_title('Transmission Type', fontweight='bold')
                axes[1,1].tick_params(axis='x', rotation=45)
            else:
                axes[1,1].text(0.5, 0.5, 'No Transmission Data', ha='center', va='center', transform=axes[1,1].transAxes)
                axes[1,1].set_title('Transmission Type', fontweight='bold')
        else:
            axes[1,1].text(0.5, 0.5, 'No Transmission Data', ha='center', va='center', transform=axes[1,1].transAxes)
            axes[1,1].set_title('Transmission Type', fontweight='bold')
        
        # Location distribution
        if 'location_clean' in self.df.columns:
            loc_counts = self.df['location_clean'].value_counts().head(10)
            if len(loc_counts) > 0:
                loc_counts.plot(kind='bar', ax=axes[1,2], color='lightseagreen')
                axes[1,2].set_title('Top 10 Locations', fontweight='bold')
                axes[1,2].tick_params(axis='x', rotation=45)
            else:
                axes[1,2].text(0.5, 0.5, 'No Location Data', ha='center', va='center', transform=axes[1,2].transAxes)
                axes[1,2].set_title('Top 10 Locations', fontweight='bold')
        else:
            axes[1,2].text(0.5, 0.5, 'No Location Data', ha='center', va='center', transform=axes[1,2].transAxes)
            axes[1,2].set_title('Top 10 Locations', fontweight='bold')
        
        plt.tight_layout()
        dashboard_path = f"{save_path}comprehensive_dashboard.png"
        plt.savefig(dashboard_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.visualization_paths.append(dashboard_path)
        logger.info(f"📊 Main dashboard saved: {dashboard_path}")
    
    def save_cleaned_data(self, filename="cars24_cleaned_data.csv"):
        """Save cleaned data to CSV"""
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"💾 Cleaned data saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving cleaned data: {e}")
            return False
    
    def generate_analysis_report(self, filename="data_analysis_report.txt"):
        """Generate comprehensive analysis report"""
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            report_content = self._generate_report_text()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"📝 Analysis report saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving analysis report: {e}")
            return False
    
    def _generate_report_text(self) -> str:
        """Generate comprehensive report text"""
        report = []
        report.append("="*80)
        report.append("                 CARS24 MARUTI SUZUKI DATA ANALYSIS REPORT")
        report.append("="*80)
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total cars analyzed: {len(self.df)}")
        report.append("")
        
        # Dataset Overview
        report.append("DATASET OVERVIEW")
        report.append("-"*40)
        overview = self.analysis_results.get('dataset_overview', {})
        report.append(f"Total records: {overview.get('total_cars', 0)}")
        report.append(f"Data columns: {overview.get('total_columns', 0)}")
        report.append(f"Memory usage: {overview.get('memory_usage_mb', 0)} MB")
        report.append("")
        
        # Price Analysis
        report.append("PRICE ANALYSIS")
        report.append("-"*40)
        price_analysis = self.analysis_results.get('price_analysis', {})
        if 'error' not in price_analysis:
            report.append(f"Average price: ₹{price_analysis.get('mean', 0):,.2f}")
            report.append(f"Median price: ₹{price_analysis.get('median', 0):,.2f}")
            report.append(f"Price range: ₹{price_analysis.get('min', 0):,.2f} - ₹{price_analysis.get('max', 0):,.2f}")
            report.append(f"Standard deviation: ₹{price_analysis.get('std_dev', 0):,.2f}")
        else:
            report.append("Price data not available")
        report.append("")
        
        # Year Analysis
        report.append("YEAR ANALYSIS")
        report.append("-"*40)
        year_analysis = self.analysis_results.get('year_analysis', {})
        if 'error' not in year_analysis:
            report.append(f"Oldest car: {year_analysis.get('oldest', 0)}")
            report.append(f"Newest car: {year_analysis.get('newest', 0)}")
            report.append(f"Average year: {year_analysis.get('average', 0)}")
        else:
            report.append("Year data not available")
        report.append("")
        
        # Kilometer Analysis
        report.append("KILOMETER ANALYSIS")
        report.append("-"*40)
        km_analysis = self.analysis_results.get('kilometer_analysis', {})
        if 'error' not in km_analysis:
            report.append(f"Average kilometers: {km_analysis.get('average_km', 0):,.0f} km")
            report.append(f"Kilometer range: {km_analysis.get('min_km', 0):,.0f} - {km_analysis.get('max_km', 0):,.0f} km")
        else:
            report.append("Kilometer data not available")
        report.append("")
        
        # Location Analysis
        report.append("LOCATION DISTRIBUTION")
        report.append("-"*40)
        locations = self.analysis_results.get('location_analysis', {})
        if locations:
            for location, count in list(locations.items())[:10]:
                report.append(f"{location}: {count} cars")
        else:
            report.append("No location data available")
        report.append("")
        
        # Model Analysis
        report.append("POPULAR MODELS")
        report.append("-"*40)
        models = self.analysis_results.get('model_analysis', {})
        if models:
            for model, count in list(models.items())[:10]:
                report.append(f"{model}: {count} cars")
        else:
            report.append("No model data available")
        report.append("")
        
        # Fuel Type Distribution
        report.append("FUEL TYPE DISTRIBUTION")
        report.append("-"*40)
        categorical = self.analysis_results.get('categorical_analysis', {})
        fuel_types = categorical.get('fuel_type', {})
        if fuel_types:
            for fuel_type, count in fuel_types.items():
                report.append(f"{fuel_type}: {count} cars")
        else:
            report.append("No fuel type data available")
        report.append("")
        
        # Transmission Distribution
        report.append("TRANSMISSION DISTRIBUTION")
        report.append("-"*40)
        transmission = categorical.get('transmission', {})
        if transmission:
            for trans, count in transmission.items():
                report.append(f"{trans}: {count} cars")
        else:
            report.append("No transmission data available")
        report.append("")
        
        # Data Quality Report
        report.append("DATA QUALITY REPORT")
        report.append("-"*40)
        for column, stats in self.cleaning_report.items():
            if column != 'data_quality':
                report.append(f"{column}: {stats.get('success_rate', '0%')} successfully cleaned")
        
        quality_metrics = self.cleaning_report.get('data_quality', {})
        report.append(f"Complete records: {quality_metrics.get('complete_records', 0)}/{quality_metrics.get('total_records', 0)}")
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-"*40)
        report.append("1. Focus on locations with highest car availability")
        report.append("2. Consider popular fuel types and transmission preferences")
        report.append("3. Analyze pricing trends for different models")
        report.append("4. Monitor data quality and completeness regularly")
        report.append("5. Use insights for inventory planning and pricing strategy")
        
        return "\n".join(report)

def main():
    """Main execution function"""
    print("📊 CARS24 DATA ANALYZER - FIXED VERSION")
    print("="*50)
    
    try:
        # Find latest data file
        data_files = [f for f in os.listdir('.') if f.startswith('cars24') and f.endswith('.csv')]
        data_files.extend([f for f in os.listdir('data') if f.startswith('cars24') and f.endswith('.csv')])
        
        if not data_files:
            print("❌ No data files found")
            print("🔄 Please run the scraper first or check the data directory")
            return
        
        latest_file = sorted(data_files)[-1]
        if latest_file.startswith('data/'):
            file_path = latest_file
        else:
            file_path = f'data/{latest_file}' if os.path.exists(f'data/{latest_file}') else latest_file
        
        print(f"📁 Loading data from: {file_path}")
        df = pd.read_csv(file_path)
        
        # Initialize analyzer
        analyzer = Cars24DataAnalyzerFixed(df)
        
        # Clean data
        print("🧹 Cleaning data...")
        cleaned_df = analyzer.comprehensive_cleaning()
        
        # Analyze data
        print("📈 Analyzing data...")
        analysis_results = analyzer.generate_comprehensive_analysis()
        
        # Create visualizations
        print("📊 Creating visualizations...")
        analyzer.create_visualizations()
        
        # Save cleaned data
        print("💾 Saving cleaned data...")
        analyzer.save_cleaned_data()
        
        # Generate report
        print("📝 Generating report...")
        analyzer.generate_analysis_report()
        
        print("✅ Data analysis completed successfully!")
        
        # Print summary
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"Total cars analyzed: {len(cleaned_df)}")
        
        if 'location_clean' in cleaned_df.columns:
            locations = cleaned_df['location_clean'].nunique()
            print(f"Locations covered: {locations}")
        
        price_analysis = analysis_results.get('price_analysis', {})
        if 'error' not in price_analysis:
            print(f"Average price: ₹{price_analysis.get('mean', 0):,.0f}")
        
        print(f"Visualizations created: {len(analyzer.visualization_paths)}")
        
    except Exception as e:
        print(f"❌ Data analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()