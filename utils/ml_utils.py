import os
import json
import pickle
import numpy as np
import pandas as pd
from django.conf import settings

class MLModelLoader:
    """
    Utility class untuk load ML models dan konfigurasi
    """
    
    def __init__(self):
        self.base_path = os.path.join(settings.BASE_DIR, 'exports')
        self.classification_path = os.path.join(self.base_path, 'classification')
        self.clustering_path = os.path.join(self.base_path, 'clustering')
        self.forecast_path = os.path.join(self.base_path, 'forecast')
        
        self._classification_model = None
        self._classification_config = None
        self._classification_scaler = None
        self._classification_imputer = None
        self._classification_mappings = None
        
        self._clustering_model = None
        self._clustering_config = None
        self._clustering_scaler = None
        self._clustering_pca = None
        
        self._forecast_model = None
        self._forecast_config = None
    
    # ==================== CLASSIFICATION ====================
    
    def load_classification_model(self):
        """Load XGBoost classification model"""
        if self._classification_model is None:
            model_path = os.path.join(self.classification_path, 'xgb_model.pkl')
            with open(model_path, 'rb') as f:
                self._classification_model = pickle.load(f)
        return self._classification_model
    
    def load_classification_config(self):
        """Load classification configuration"""
        if self._classification_config is None:
            config_path = os.path.join(self.classification_path, 'supervised_config.json')
            with open(config_path, 'r') as f:
                self._classification_config = json.load(f)
        return self._classification_config
    
    def load_classification_scaler(self):
        """Load StandardScaler for classification"""
        if self._classification_scaler is None:
            scaler_path = os.path.join(self.classification_path, 'scaler_supervised.pkl')
            with open(scaler_path, 'rb') as f:
                self._classification_scaler = pickle.load(f)
        return self._classification_scaler
    
    def load_classification_imputer(self):
        """Load SimpleImputer for classification"""
        if self._classification_imputer is None:
            imputer_path = os.path.join(self.classification_path, 'imputer_supervised.pkl')
            with open(imputer_path, 'rb') as f:
                self._classification_imputer = pickle.load(f)
        return self._classification_imputer
    
    def load_classification_mappings(self):
        """Load feature mappings for classification"""
        if self._classification_mappings is None:
            mappings_path = os.path.join(self.classification_path, 'mappings_supervised.json')
            with open(mappings_path, 'r') as f:
                self._classification_mappings = json.load(f)
        return self._classification_mappings
    
    def preprocess_classification_input(self, data):
        """
        Preprocess input data untuk classification
        
        Args:
            data: dict dengan keys: F502, F14, F5d, F1101, Years_Since_Graduation, Gap_* (11 features)
            Model expects: F502, F14_enc, F5d_enc, Years_Since_Graduation, 
                          Gap_Etika, Gap_Keahlian, Gap_English, Gap_IT, 
                          Gap_Komunikasi, Gap_Teamwork, Gap_Development
        
        Returns:
            DataFrame yang sudah dipreprocess dengan 11 features
        """
        config = self.load_classification_config()
        mappings = self.load_classification_mappings()
        
        # Model XGBoost expects these 11 features (in this exact order)
        model_features = [
            'F502', 'F14_enc', 'F5d_enc', 'Years_Since_Graduation',
            'Gap_Etika', 'Gap_Keahlian', 'Gap_English', 'Gap_IT',
            'Gap_Komunikasi', 'Gap_Teamwork', 'Gap_Development'
        ]
        
        # Build input dict according to model's expected feature order
        input_dict = {}
        
        # F502 - Waktu tunggu kerja (bulan)
        input_dict['F502'] = data.get('F502', 3.0)  # Default: 3 bulan
        
        # F14_enc - Mapping categorical F14
        f14_value = data.get('F14', '')
        input_dict['F14_enc'] = mappings['f14_map'].get(f14_value, 3)  # Default: Cukup Erat
        
        # F5d_enc - Tingkat tempat kerja (ordinal 1-5)
        input_dict['F5d_enc'] = data.get('F5d', 3.0)  # Default: 3
        
        # Years_Since_Graduation
        input_dict['Years_Since_Graduation'] = data.get('Years_Since_Graduation', 2.0) 
        
        # Competency gaps 
        input_dict['Gap_Etika'] = data.get('Gap_Etika', 0.0)
        input_dict['Gap_Keahlian'] = data.get('Gap_Keahlian', 0.0)
        input_dict['Gap_English'] = data.get('Gap_English', 0.0)
        input_dict['Gap_IT'] = data.get('Gap_IT', 0.0)
        input_dict['Gap_Komunikasi'] = data.get('Gap_Komunikasi', 0.0)
        input_dict['Gap_Teamwork'] = data.get('Gap_Teamwork', 0.0)
        input_dict['Gap_Development'] = data.get('Gap_Development', 0.0)
        
        # Convert to DataFrame with feature names (XGBoost expects this)
        X = pd.DataFrame([input_dict], columns=model_features)
        
        return X
    
    def predict_classification(self, data):
        """
        Predict menggunakan classification model
        
        Args:
            data: dict dengan keys: F502, F14, F5d, Years_Since_Graduation, Gap_*
        
        Returns:
            dict dengan prediction dan probability
        """
        model = self.load_classification_model()
        X = self.preprocess_classification_input(data)
        
        # Predict
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        
        # Get class labels from config
        config = self.load_classification_config()
        label_mapping = config.get('preprocessing', {}).get('label_mapping', {}).get('High_Salary', {})
        
        # Use label mapping (0 = "Gaji <= 5jt", 1 = "Gaji > 5jt")
        predicted_label = label_mapping.get(str(int(prediction)), f"Class {prediction}")
        
        return {
            'prediction': int(prediction),
            'predicted_label': predicted_label,
            'probabilities': {
                label_mapping.get(str(i), f"Class {i}"): float(prob) 
                for i, prob in enumerate(probabilities)
            },
            'confidence': float(max(probabilities))
        }
    
    # ==================== CLUSTERING ====================
    
    def load_clustering_model(self):
        """Load KMeans clustering model"""
        if self._clustering_model is None:
            model_path = os.path.join(self.clustering_path, 'kmeans_model.pkl')
            try:
                with open(model_path, 'rb') as f:
                    self._clustering_model = pickle.load(f)
            except (pickle.UnpicklingError, ValueError, EOFError) as e:
                raise FileNotFoundError(f"Clustering model file is corrupt or incompatible. Please regenerate the model. Error: {str(e)}")
        return self._clustering_model
    
    def load_clustering_config(self):
        """Load clustering configuration"""
        if self._clustering_config is None:
            config_path = os.path.join(self.clustering_path, 'clustering_config.json')
            with open(config_path, 'r') as f:
                self._clustering_config = json.load(f)
        return self._clustering_config
    
    def load_clustering_scaler(self):
        """Load StandardScaler for clustering"""
        if self._clustering_scaler is None:
            scaler_path = os.path.join(self.clustering_path, 'scaler.pkl')
            with open(scaler_path, 'rb') as f:
                self._clustering_scaler = pickle.load(f)
        return self._clustering_scaler
    
    def load_clustering_pca(self):
        """Load PCA for clustering"""
        if self._clustering_pca is None:
            pca_path = os.path.join(self.clustering_path, 'pca_model.pkl')
            with open(pca_path, 'rb') as f:
                self._clustering_pca = pickle.load(f)
        return self._clustering_pca
    
    def preprocess_clustering_input(self, data):
        """
        Preprocess input data untuk clustering
        
        Args:
            data: dict atau list of dict dengan keys: F502, F505, F14_enc, F5d_enc, F1101_enc
        
        Returns:
            numpy array yang sudah dipreprocess
        """
        config = self.load_clustering_config()
        scaler = self.load_clustering_scaler()
        
        # Features yang digunakan
        features = config['features_used']
        
        # Jika input single dict, convert ke list
        if isinstance(data, dict):
            data = [data]
        
        # Buat DataFrame
        input_data = []
        for item in data:
            row = [item.get(f, 0) for f in features]
            input_data.append(row)
        
        X = np.array(input_data, dtype=float)
        
        # Scale features
        X = scaler.transform(X)
        
        return X
    
    def predict_clustering(self, data):
        """
        Predict menggunakan clustering model
        
        Args:
            data: dict atau list of dict dengan keys sesuai features_used
        
        Returns:
            dict dengan cluster assignment dan PCA coordinates untuk visualisasi
        """
        model = self.load_clustering_model()
        config = self.load_clustering_config()
        pca = self.load_clustering_pca()
        X = self.preprocess_clustering_input(data)
        
        # Predict cluster
        clusters = model.predict(X)
        
        # Get PCA coordinates for visualization
        X_pca = pca.transform(X)
        
        # Get cluster labels
        cluster_labels = config.get('cluster_labels', {})
        
        # Jika input single item
        if isinstance(data, dict):
            cluster_id = int(clusters[0])
            return {
                'cluster': cluster_id,
                'cluster_label': cluster_labels.get(str(cluster_id), f"Cluster {cluster_id}"),
                'pca_coordinates': {
                    'pc1': float(X_pca[0, 0]),
                    'pc2': float(X_pca[0, 1])
                }
            }
        
        # Jika input multiple items
        results = []
        for i, cluster_id in enumerate(clusters):
            cluster_id = int(cluster_id)
            results.append({
                'cluster': cluster_id,
                'cluster_label': cluster_labels.get(str(cluster_id), f"Cluster {cluster_id}"),
                'pca_coordinates': {
                    'pc1': float(X_pca[i, 0]),
                    'pc2': float(X_pca[i, 1])
                }
            })
        
        # Get PCA variance for display
        pca_variance = pca.explained_variance_ratio_.tolist()
        
        return {
            'results': results,
            'pca_variance': pca_variance
        }
    
    def cluster_batch_data(self, dataframe):
        """
        Clustering untuk batch data (DataFrame)
        
        Args:
            dataframe: pandas DataFrame dengan kolom sesuai features_used
        
        Returns:
            DataFrame dengan kolom cluster tambahan
        """
        model = self.load_clustering_model()
        config = self.load_clustering_config()
        scaler = self.load_clustering_scaler()
        
        features = config['features_used']
        
        # Extract features
        X = dataframe[features].values
        
        # Scale
        X = scaler.transform(X)
        
        # Predict
        clusters = model.predict(X)
        
        # Add to dataframe
        result_df = dataframe.copy()
        result_df['cluster'] = clusters
        
        # Add cluster label
        cluster_labels = config.get('cluster_labels', {})
        result_df['cluster_label'] = result_df['cluster'].apply(
            lambda x: cluster_labels.get(str(x), f"Cluster {x}")
        )
        
        return result_df
    
    # ==================== FORECASTING ====================
    
    def load_forecast_model(self):
        """Load ARIMA forecast model"""
        if self._forecast_model is None:
            model_path = os.path.join(self.forecast_path, 'arima_model.pickle')
            with open(model_path, 'rb') as f:
                self._forecast_model = pickle.load(f)
        return self._forecast_model
    
    def load_forecast_config(self):
        """Load forecast configuration"""
        if self._forecast_config is None:
            config_path = os.path.join(self.forecast_path, 'forecast_config.json')
            with open(config_path, 'r') as f:
                self._forecast_config = json.load(f)
        return self._forecast_config
    
    def get_forecast_data(self):
        """
        Get forecast data dari config
        
        Returns:
            dict dengan historical dan forecast data
        """
        config = self.load_forecast_config()
        
        # Load historical data
        historical_path = os.path.join(self.forecast_path, 'historical_lulusan.csv')
        historical_df = pd.read_csv(historical_path)
        
        # Normalize column names untuk historical
        # Handle both 'Tahun Lulus' and 'Tahun'
        if 'Tahun Lulus' in historical_df.columns:
            historical_df.rename(columns={'Tahun Lulus': 'year'}, inplace=True)
        elif 'Tahun' in historical_df.columns:
            historical_df.rename(columns={'Tahun': 'year'}, inplace=True)
        
        # Handle both 'jumlah_lulusan' and other variations
        if 'jumlah_lulusan' in historical_df.columns:
            historical_df.rename(columns={'jumlah_lulusan': 'lulusan'}, inplace=True)
        
        # Load forecast data
        forecast_path = os.path.join(self.forecast_path, 'forecast_lulusan.csv')
        forecast_df = pd.read_csv(forecast_path)
        
        # Normalize column names untuk forecast
        if 'Tahun' in forecast_df.columns:
            forecast_df.rename(columns={'Tahun': 'year'}, inplace=True)
        
        # Handle both 'predicted_jumlah_lulusan' and other variations
        if 'predicted_jumlah_lulusan' in forecast_df.columns:
            forecast_df.rename(columns={'predicted_jumlah_lulusan': 'lulusan'}, inplace=True)
        
        return {
            'model_info': {
                'model_name': config['model']['model_name'],
                'arima_order': config['model']['arima_order'],
                'aic': config['model']['aic'],
                'bic': config['model']['bic']
            },
            'training_period': config['model']['training_period'],
            'historical_data': historical_df.to_dict('records'),
            'forecast_data': forecast_df.to_dict('records'),
            'forecast_years': config['model']['forecast_years'],
            'forecast_values': config['model']['forecast_values']
        }
    
    def forecast_future(self, steps=5):
        """
        Generate forecast untuk steps ke depan
        
        Args:
            steps: jumlah periode ke depan yang ingin di-forecast
        
        Returns:
            dict dengan forecast results
        """
        model = self.load_forecast_model()
        config = self.load_forecast_config()
        
        # Get last year from training
        last_year = config['model']['training_period']['end_year']
        
        # Forecast
        forecast_result = model.forecast(steps=steps)
        
        # Generate years
        forecast_years = [last_year + i + 1 for i in range(steps)]
        
        return {
            'forecast_years': forecast_years,
            'forecast_values': forecast_result.tolist(),
            'model_info': {
                'arima_order': config['model']['arima_order'],
                'aic': config['model']['aic'],
                'bic': config['model']['bic']
            }
        }


# Singleton instance
ml_loader = MLModelLoader()
