"""
Moduł do predykcji cukrzycy dla aplikacji Django
Klinika Diabetologiczna
"""

import pickle
import numpy as np
from pathlib import Path


class DiabetesPredictor:
    """
    Klasa do przewidywania prawdopodobieństwa cukrzycy na podstawie danych pacjenta.
    """
    
    def __init__(self, model_path=None, scaler_path=None):
        """
        Inicjalizacja predyktora.
        
        Args:
            model_path: Ścieżka do pliku z modelem (.pkl)
            scaler_path: Ścieżka do pliku ze scalerem (.pkl)
        """
        # Jeśli nie podano ścieżek, użyj domyślnych (w tym samym katalogu)
        if model_path is None:
            model_path = Path(__file__).parent / 'diabetes_model.pkl'
        if scaler_path is None:
            scaler_path = Path(__file__).parent / 'diabetes_scaler.pkl'
            
        # Wczytanie modelu i scalera
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
    
    def predict_probability(self, patient_data):
        """
        Przewiduje prawdopodobieństwo cukrzycy dla pacjenta.
        
        Args:
            patient_data: Słownik z danymi pacjenta zawierający:
                - pregnancies: liczba ciąż (int)
                - glucose: poziom glukozy (float)
                - blood_pressure: ciśnienie krwi (float)
                - skin_thickness: grubość fałdu skórnego (float)
                - insulin: poziom insuliny (float)
                - bmi: wskaźnik masy ciała (float)
                - diabetes_pedigree: funkcja rodowodu cukrzycy (float)
                - age: wiek (int)
        
        Returns:
            float: Prawdopodobieństwo cukrzycy (0.0 - 1.0)
        
        Example:
            >>> predictor = DiabetesPredictor()
            >>> data = {
            ...     'pregnancies': 6,
            ...     'glucose': 148,
            ...     'blood_pressure': 72,
            ...     'skin_thickness': 35,
            ...     'insulin': 0,
            ...     'bmi': 33.6,
            ...     'diabetes_pedigree': 0.627,
            ...     'age': 50
            ... }
            >>> probability = predictor.predict_probability(data)
            >>> print(f"Prawdopodobieństwo: {probability*100:.1f}%")
        """
        # Przygotowanie danych w odpowiedniej kolejności
        features = np.array([[
            patient_data['pregnancies'],
            patient_data['glucose'],
            patient_data['blood_pressure'],
            patient_data['skin_thickness'],
            patient_data['insulin'],
            patient_data['bmi'],
            patient_data['diabetes_pedigree'],
            patient_data['age']
        ]])
        
        # Standaryzacja
        features_scaled = self.scaler.transform(features)
        
        # Predykcja
        probability = self.model.predict_proba(features_scaled)[0][1]
        
        return probability
    
    def predict_with_interpretation(self, patient_data):
        """
        Przewiduje prawdopodobieństwo cukrzycy i dodaje interpretację ryzyka.
        
        Args:
            patient_data: Słownik z danymi pacjenta (jak w predict_probability)
        
        Returns:
            dict: Słownik zawierający:
                - probability: prawdopodobieństwo (float 0.0-1.0)
                - percentage: prawdopodobieństwo w procentach (float)
                - risk_level: poziom ryzyka ('niskie', 'umiarkowane', 'wysokie', 'bardzo wysokie')
                - risk_color: kolor do wyświetlenia ('green', 'yellow', 'orange', 'red')
        
        Example:
            >>> result = predictor.predict_with_interpretation(data)
            >>> print(f"Ryzyko: {result['risk_level']} ({result['percentage']:.1f}%)")
        """
        probability = self.predict_probability(patient_data)
        percentage = probability * 100
        
        # Określenie poziomu ryzyka
        if percentage < 30:
            risk_level = 'niskie'
            risk_color = 'green'
        elif percentage < 50:
            risk_level = 'umiarkowane'
            risk_color = 'yellow'
        elif percentage < 70:
            risk_level = 'wysokie'
            risk_color = 'orange'
        else:
            risk_level = 'bardzo wysokie'
            risk_color = 'red'
        
        return {
            'probability': probability,
            'percentage': percentage,
            'risk_level': risk_level,
            'risk_color': risk_color
        }


# Przykład użycia (można usunąć w produkcji)
if __name__ == '__main__':
    predictor = DiabetesPredictor()
    
    # Test 1: Pacjent wysokiego ryzyka
    high_risk_patient = {
        'pregnancies': 8,
        'glucose': 183,
        'blood_pressure': 64,
        'skin_thickness': 0,
        'insulin': 0,
        'bmi': 23.3,
        'diabetes_pedigree': 0.672,
        'age': 32
    }
    
    result = predictor.predict_with_interpretation(high_risk_patient)
    print("Pacjent wysokiego ryzyka:")
    print(f"  Prawdopodobieństwo: {result['percentage']:.1f}%")
    print(f"  Poziom ryzyka: {result['risk_level']}")
    print()
    
    # Test 2: Pacjent niskiego ryzyka
    low_risk_patient = {
        'pregnancies': 1,
        'glucose': 85,
        'blood_pressure': 66,
        'skin_thickness': 29,
        'insulin': 0,
        'bmi': 26.6,
        'diabetes_pedigree': 0.351,
        'age': 31
    }
    
    result = predictor.predict_with_interpretation(low_risk_patient)
    print("Pacjent niskiego ryzyka:")
    print(f"  Prawdopodobieństwo: {result['percentage']:.1f}%")
    print(f"  Poziom ryzyka: {result['risk_level']}")
