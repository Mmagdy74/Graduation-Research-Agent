"""
Synthetic Data Generator for NMR Permeability Research
Generates realistic synthetic data for thesis demonstration
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict

class NMRDataGenerator:
    """Generate synthetic NMR and permeability data"""
    
    def __init__(self, n_samples=100, random_seed=42):
        self.n_samples = n_samples
        np.random.seed(random_seed)
        
    def generate_nmr_permeability_data(self) -> pd.DataFrame:
        """
        Generate synthetic NMR and permeability data
        Returns DataFrame with NMR parameters and permeability measurements
        """
        # Generate porosity (typical range 0.05 to 0.35)
        porosity = np.random.uniform(0.05, 0.35, self.n_samples)
        
        # Generate T2 geometric mean (typical range 10 to 1000 ms)
        t2_gm = np.random.lognormal(np.log(100), 0.8, self.n_samples)
        t2_gm = np.clip(t2_gm, 10, 1000)
        
        # Generate bound fluid volume (BFV) - correlated with porosity
        bfv = porosity * np.random.uniform(0.2, 0.6, self.n_samples)
        
        # Calculate free fluid index (FFI)
        ffi = porosity - bfv
        
        # Generate clay volume (typical range 0 to 0.3)
        clay_volume = np.random.uniform(0, 0.3, self.n_samples)
        
        # Generate core permeability (mD) - correlated with porosity and T2
        # Using modified Coates equation with noise
        base_perm = (porosity ** 4) * (ffi / bfv) ** 2 * 10000
        noise = np.random.lognormal(0, 0.3, self.n_samples)
        core_permeability = base_perm * noise
        core_permeability = np.clip(core_permeability, 0.01, 10000)
        
        # Generate NMR-predicted permeability using different models
        
        # Coates Model
        coates_perm = (porosity ** 4) * (ffi / bfv) ** 2 * 10000
        coates_perm = coates_perm * np.random.lognormal(0, 0.15, self.n_samples)
        coates_perm = np.clip(coates_perm, 0.01, 10000)
        
        # Timur-Coates Model
        timur_coates_perm = 0.136 * (porosity ** 4.4) / (bfv ** 2) * 10000
        timur_coates_perm = timur_coates_perm * np.random.lognormal(0, 0.2, self.n_samples)
        timur_coates_perm = np.clip(timur_coates_perm, 0.01, 10000)
        
        # SDR Model (Schlumberger Doll Research)
        sdr_perm = 4 * (porosity ** 4) * (t2_gm ** 2)
        sdr_perm = sdr_perm * np.random.lognormal(0, 0.18, self.n_samples)
        sdr_perm = np.clip(sdr_perm, 0.01, 10000)
        
        # Create DataFrame
        data = pd.DataFrame({
            'Depth_m': np.linspace(2000, 2500, self.n_samples),
            'Porosity': porosity,
            'T2_GM_ms': t2_gm,
            'BFV': bfv,
            'FFI': ffi,
            'Clay_Volume': clay_volume,
            'Core_Permeability_mD': core_permeability,
            'Coates_Permeability_mD': coates_perm,
            'Timur_Coates_Permeability_mD': timur_coates_perm,
            'SDR_Permeability_mD': sdr_perm
        })
        
        return data
    
    def generate_t2_distribution(self, n_bins=50) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic T2 distribution
        Returns (t2_times, amplitudes)
        """
        t2_times = np.logspace(-1, 4, n_bins)  # 0.1 to 10000 ms
        
        # Create bimodal distribution (clay-bound and free fluid)
        clay_peak = np.exp(-((np.log(t2_times) - np.log(3)) ** 2) / (2 * 0.5 ** 2))
        free_fluid_peak = np.exp(-((np.log(t2_times) - np.log(200)) ** 2) / (2 * 0.8 ** 2))
        
        amplitudes = 0.3 * clay_peak + 0.7 * free_fluid_peak
        amplitudes = amplitudes / np.max(amplitudes)  # Normalize
        
        return t2_times, amplitudes
    
    def calculate_statistics(self, data: pd.DataFrame) -> Dict:
        """Calculate statistical metrics for model comparison"""
        models = ['Coates', 'Timur_Coates', 'SDR']
        stats = {}
        
        for model in models:
            pred_col = f'{model}_Permeability_mD'
            
            # Calculate correlation coefficient
            correlation = np.corrcoef(
                np.log10(data['Core_Permeability_mD']), 
                np.log10(data[pred_col])
            )[0, 1]
            
            # Calculate RMSE in log space
            rmse = np.sqrt(np.mean(
                (np.log10(data['Core_Permeability_mD']) - 
                 np.log10(data[pred_col])) ** 2
            ))
            
            # Calculate mean absolute percentage error
            mape = np.mean(np.abs(
                (data['Core_Permeability_mD'] - data[pred_col]) / 
                data['Core_Permeability_mD']
            )) * 100
            
            stats[model] = {
                'correlation': correlation,
                'rmse_log': rmse,
                'mape': mape
            }
        
        return stats
    
    def generate_well_data(self, n_wells=3) -> Dict[str, pd.DataFrame]:
        """Generate data for multiple wells"""
        wells = {}
        for i in range(1, n_wells + 1):
            # Use different random seed for each well
            np.random.seed(42 + i)
            well_data = self.generate_nmr_permeability_data()
            wells[f'Well_{i}'] = well_data
        
        return wells


if __name__ == "__main__":
    # Test data generation
    generator = NMRDataGenerator(n_samples=100)
    data = generator.generate_nmr_permeability_data()
    print("✅ Generated NMR Permeability Data:")
    print(data.head())
    print(f"\nData shape: {data.shape}")
    
    stats = generator.calculate_statistics(data)
    print("\n📊 Model Statistics:")
    for model, metrics in stats.items():
        print(f"\n{model} Model:")
        print(f"  Correlation: {metrics['correlation']:.3f}")
        print(f"  RMSE (log): {metrics['rmse_log']:.3f}")
        print(f"  MAPE: {metrics['mape']:.1f}%")
