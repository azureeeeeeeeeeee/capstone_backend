from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.serializers import (
    ClassificationInputSerializer,
    ClassificationOutputSerializer,
    ClusteringInputSerializer,
    ClusteringOutputSerializer,
    ClusteringBatchOutputSerializer,
    ForecastOutputSerializer,
    ForecastCustomSerializer
)
from utils.ml_utils import ml_loader
import traceback

@swagger_auto_schema(
    method='post',
    tags=['Machine Learning - Classification'],
    operation_description="""
    Predict job satisfaction or employment status classification based on survey responses.
    """,
    request_body=ClassificationInputSerializer,
    responses={
        200: openapi.Response("Classification result", ClassificationOutputSerializer),
        400: "Invalid input data",
        500: "Internal server error"
    }
)
@api_view(['POST'])
@permission_classes([AllowAny]) 
def classification_predict(request):
    """
    Endpoint untuk prediksi menggunakan classification model (XGBoost)
    Public endpoint - dapat diakses tanpa authentication (untuk alumni)
    """
    try:
        serializer = ClassificationInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid input', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        input_data = serializer.validated_data
        result = ml_loader.predict_classification(input_data)
        
        output_serializer = ClassificationOutputSerializer(data=result)
        if output_serializer.is_valid():
            return Response(output_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_200_OK)
            
    except FileNotFoundError as e:
        return Response(
            {'error': 'Model files not found', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'error': 'Prediction failed', 'details': str(e), 'traceback': traceback.format_exc()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='get',
    tags=['Machine Learning - Classification'],
    operation_description="Get classification model information and configuration",
    responses={
        200: "Model configuration",
        500: "Internal server error"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def classification_info(request):
    """
    Endpoint untuk mendapatkan informasi tentang classification model
    """
    try:
        config = ml_loader.load_classification_config()
        mappings = ml_loader.load_classification_mappings()
        
        return Response({
            'model_type': 'XGBoost Classifier',
            'features': config['preprocessing']['features'],
            'target_mapping': config.get('target_mapping', {}),
            'categorical_mappings': mappings,
            'preprocessing': {
                'scaler': config['preprocessing']['scaler']['type'],
                'imputer': config['preprocessing']['imputer']['type']
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': 'Failed to load model info', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='post',
    tags=['Machine Learning - Clustering'],
    operation_description="""
    Assign survey respondent(s) to clusters based on their employment characteristics.
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'F502': openapi.Schema(type=openapi.TYPE_NUMBER, description='Gaji'),
            'F505': openapi.Schema(type=openapi.TYPE_NUMBER, description='Jam kerja'),
            'F14_enc': openapi.Schema(type=openapi.TYPE_NUMBER, description='Encoded F14'),
            'F5d_enc': openapi.Schema(type=openapi.TYPE_NUMBER, description='Encoded F5d'),
            'F1101_enc': openapi.Schema(type=openapi.TYPE_NUMBER, description='Encoded F1101'),
        }
    ),
    responses={
        200: openapi.Response("Clustering result", ClusteringOutputSerializer),
        400: "Invalid input data",
        500: "Internal server error"
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def clustering_predict(request):
    """
    Endpoint untuk clustering menggunakan KMeans model
    Mendukung single prediction dan batch prediction
    """
    try:
        input_data = request.data
        
        if isinstance(input_data, list):
            for item in input_data:
                serializer = ClusteringInputSerializer(data=item)
                if not serializer.is_valid():
                    return Response(
                        {'error': 'Invalid input in batch', 'details': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            serializer = ClusteringInputSerializer(data=input_data)
            if not serializer.is_valid():
                return Response(
                    {'error': 'Invalid input', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        result = ml_loader.predict_clustering(input_data)
        
        return Response(result, status=status.HTTP_200_OK)
            
    except FileNotFoundError as e:
        return Response(
            {'error': 'Model files not found', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'error': 'Clustering failed', 'details': str(e), 'traceback': traceback.format_exc()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='get',
    tags=['Machine Learning - Clustering'],
    operation_description="Get clustering model information and configuration",
    responses={
        200: "Model configuration",
        500: "Internal server error"
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def clustering_info(request):
    """
    Endpoint untuk mendapatkan informasi tentang clustering model
    """
    try:
        config = ml_loader.load_clustering_config()
        
        return Response({
            'model_type': config['model_type'],
            'n_clusters': config['n_clusters'],
            'features_used': config['features_used'],
            'scaler_type': config['scaler_type'],
            'cluster_labels': config['cluster_labels'],
            'preprocessing_steps': config['preprocessing_steps']
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': 'Failed to load model info', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    tags=['Machine Learning - Forecasting'],
    operation_description="""
    Get graduate forecast data using ARIMA model.
    """,
    responses={
        200: openapi.Response("Forecast data", ForecastOutputSerializer),
        500: "Internal server error"
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def forecast_get(request):
    """
    Endpoint untuk mendapatkan data forecast yang sudah ada
    """
    try:
        result = ml_loader.get_forecast_data()
        
        return Response(result, status=status.HTTP_200_OK)
            
    except FileNotFoundError as e:
        return Response(
            {'error': 'Forecast data not found', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to get forecast data', 'details': str(e), 'traceback': traceback.format_exc()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    tags=['Machine Learning - Forecasting'],
    operation_description="""
    Generate custom forecast for specified number of periods ahead.
    
    Parameters:
    - steps: Number of periods to forecast (1-20, default: 5)
    """,
    request_body=ForecastCustomSerializer,
    responses={
        200: "Custom forecast result",
        400: "Invalid input",
        500: "Internal server error"
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def forecast_custom(request):
    """
    Endpoint untuk generate forecast custom dengan jumlah steps tertentu
    """
    try:
        serializer = ForecastCustomSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid input', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        steps = serializer.validated_data.get('steps', 5)
        result = ml_loader.forecast_future(steps=steps)
        
        return Response(result, status=status.HTTP_200_OK)
            
    except FileNotFoundError as e:
        return Response(
            {'error': 'Model files not found', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'error': 'Forecast failed', 'details': str(e), 'traceback': traceback.format_exc()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='get',
    tags=['Machine Learning - Forecasting'],
    operation_description="Get forecasting model information",
    responses={
        200: "Model information",
        500: "Internal server error"
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def forecast_info(request):
    """
    Endpoint untuk mendapatkan informasi tentang forecast model
    """
    try:
        config = ml_loader.load_forecast_config()
        
        return Response({
            'model_name': config['model']['model_name'],
            'arima_order': config['model']['arima_order'],
            'aic': config['model']['aic'],
            'bic': config['model']['bic'],
            'training_period': config['model']['training_period'],
            'forecast_horizon': config['model']['forecast_horizon'],
            'exported_at': config['model']['exported_at']
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': 'Failed to load model info', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    tags=['Machine Learning - System'],
    operation_description="Check if all ML models are loaded and accessible",
    responses={
        200: "All models OK",
        500: "Some models failed to load"
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def ml_health_check(request):
    """
    Endpoint untuk cek health status semua ML models
    """
    health_status = {
        'classification': {'status': 'unknown', 'error': None},
        'clustering': {'status': 'unknown', 'error': None},
        'forecasting': {'status': 'unknown', 'error': None}
    }
    
    try:
        ml_loader.load_classification_model()
        ml_loader.load_classification_config()
        health_status['classification']['status'] = 'ok'
    except Exception as e:
        health_status['classification']['status'] = 'error'
        health_status['classification']['error'] = str(e)
    
    try:
        ml_loader.load_clustering_model()
        ml_loader.load_clustering_config()
        health_status['clustering']['status'] = 'ok'
    except Exception as e:
        health_status['clustering']['status'] = 'error'
        health_status['clustering']['error'] = str(e)
    
    try:
        ml_loader.load_forecast_model()
        ml_loader.load_forecast_config()
        health_status['forecasting']['status'] = 'ok'
    except Exception as e:
        health_status['forecasting']['status'] = 'error'
        health_status['forecasting']['error'] = str(e)
    
    all_ok = all(v['status'] == 'ok' for v in health_status.values())
    
    return Response(
        {
            'overall_status': 'healthy' if all_ok else 'degraded',
            'models': health_status
        },
        status=status.HTTP_200_OK if all_ok else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
