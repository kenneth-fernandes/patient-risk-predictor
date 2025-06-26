"""Tests for API schemas module."""

import pytest
from pydantic import ValidationError

from src.api.schemas import PatientData


class TestPatientData:
    """Test PatientData schema validation."""
    
    def test_patient_data_valid_input(self, sample_patient_data):
        """Test valid patient data creation."""
        patient = PatientData(**sample_patient_data)
        
        # Check all fields are properly set
        assert patient.age == 63.0
        assert patient.sex == 1.0
        assert patient.cp == 3.0
        assert patient.trestbps == 145.0
        assert patient.chol == 233.0
        assert patient.fbs == 1.0
        assert patient.restecg == 0.0
        assert patient.thalach == 150.0
        assert patient.exang == 0.0
        assert patient.oldpeak == 2.3
        assert patient.slope == 0.0
        assert patient.ca == 0.0
        assert patient.thal == 1.0
    
    def test_patient_data_model_dump(self, sample_patient_data):
        """Test model_dump method returns correct dictionary."""
        patient = PatientData(**sample_patient_data)
        dumped = patient.model_dump()
        
        # Check that dumped data matches input
        assert dumped == sample_patient_data
        assert isinstance(dumped, dict)
    
    def test_patient_data_missing_field(self):
        """Test validation error when required field is missing."""
        incomplete_data = {
            "age": 63.0,
            "sex": 1.0,
            # Missing other required fields
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PatientData(**incomplete_data)
        
        # Check that validation error mentions missing fields
        errors = exc_info.value.errors()
        missing_fields = [error['loc'][0] for error in errors if error['type'] == 'missing']
        assert len(missing_fields) > 0
    
    def test_patient_data_type_coercion(self):
        """Test that numeric types are properly coerced."""
        # Test with integer inputs (should be converted to float)
        data_with_ints = {
            "age": 63,  # int
            "sex": 1,   # int
            "cp": 3,    # int
            "trestbps": 145,
            "chol": 233,
            "fbs": 1,
            "restecg": 0,
            "thalach": 150,
            "exang": 0,
            "oldpeak": 2.3,  # already float
            "slope": 0,
            "ca": 0,
            "thal": 1
        }
        
        patient = PatientData(**data_with_ints)
        
        # All fields should be float
        assert isinstance(patient.age, float)
        assert isinstance(patient.sex, float)
        assert isinstance(patient.cp, float)
        assert patient.age == 63.0
        assert patient.sex == 1.0
    
    def test_patient_data_string_numbers(self):
        """Test that string numbers are properly converted."""
        data_with_strings = {
            "age": "63.5",
            "sex": "1",
            "cp": "3.0",
            "trestbps": "145",
            "chol": "233.5",
            "fbs": "1",
            "restecg": "0",
            "thalach": "150",
            "exang": "0",
            "oldpeak": "2.3",
            "slope": "0",
            "ca": "0",
            "thal": "1"
        }
        
        patient = PatientData(**data_with_strings)
        
        # Check conversion worked correctly
        assert patient.age == 63.5
        assert patient.sex == 1.0
        assert patient.cp == 3.0
        assert patient.chol == 233.5
    
    def test_patient_data_invalid_string(self):
        """Test validation error with invalid string values."""
        invalid_data = {
            "age": "invalid_age",
            "sex": 1.0,
            "cp": 3.0,
            "trestbps": 145.0,
            "chol": 233.0,
            "fbs": 1.0,
            "restecg": 0.0,
            "thalach": 150.0,
            "exang": 0.0,
            "oldpeak": 2.3,
            "slope": 0.0,
            "ca": 0.0,
            "thal": 1.0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PatientData(**invalid_data)
        
        # Check that validation error is about type conversion
        errors = exc_info.value.errors()
        assert any("age" in str(error['loc']) for error in errors)
    
    def test_patient_data_negative_values(self):
        """Test that negative values are accepted (might be valid in medical context)."""
        data_with_negatives = {
            "age": 65.0,
            "sex": 1.0,
            "cp": 3.0,
            "trestbps": 145.0,
            "chol": 233.0,
            "fbs": 1.0,
            "restecg": 0.0,
            "thalach": 150.0,
            "exang": 0.0,
            "oldpeak": -1.5,  # Negative value
            "slope": 0.0,
            "ca": 0.0,
            "thal": 1.0
        }
        
        patient = PatientData(**data_with_negatives)
        assert patient.oldpeak == -1.5
    
    def test_patient_data_very_large_values(self):
        """Test handling of very large numeric values."""
        data_with_large_values = {
            "age": 999.9,
            "sex": 1.0,
            "cp": 3.0,
            "trestbps": 999.0,
            "chol": 999.0,
            "fbs": 1.0,
            "restecg": 0.0,
            "thalach": 999.0,
            "exang": 0.0,
            "oldpeak": 999.9,
            "slope": 999.0,
            "ca": 999.0,
            "thal": 999.0
        }
        
        patient = PatientData(**data_with_large_values)
        assert patient.age == 999.9
        assert patient.chol == 999.0
    
    def test_patient_data_zero_values(self):
        """Test that zero values are handled correctly."""
        data_with_zeros = {
            "age": 0.0,
            "sex": 0.0,
            "cp": 0.0,
            "trestbps": 0.0,
            "chol": 0.0,
            "fbs": 0.0,
            "restecg": 0.0,
            "thalach": 0.0,
            "exang": 0.0,
            "oldpeak": 0.0,
            "slope": 0.0,
            "ca": 0.0,
            "thal": 0.0
        }
        
        patient = PatientData(**data_with_zeros)
        assert all(getattr(patient, field) == 0.0 for field in data_with_zeros.keys())
    
    def test_patient_data_field_names(self):
        """Test that all expected fields are present in the schema."""
        expected_fields = [
            'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs',
            'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
        ]
        
        # Get field names from the model
        field_names = list(PatientData.model_fields.keys())
        
        # Check all expected fields are present
        for field in expected_fields:
            assert field in field_names
        
        # Check no unexpected fields
        assert len(field_names) == len(expected_fields)
    
    def test_patient_data_field_types(self):
        """Test that all fields are defined as float type."""
        for field_name, field_info in PatientData.model_fields.items():
            # All fields should accept float type
            assert field_info.annotation == float
    
    def test_patient_data_json_serialization(self, sample_patient_data):
        """Test JSON serialization and deserialization."""
        patient = PatientData(**sample_patient_data)
        
        # Test model_dump_json
        json_str = patient.model_dump_json()
        assert isinstance(json_str, str)
        
        # Test that we can parse it back
        import json
        parsed_data = json.loads(json_str)
        
        # Create new patient from parsed data
        patient2 = PatientData(**parsed_data)
        
        # Should be equivalent
        assert patient.model_dump() == patient2.model_dump()
    
    def test_patient_data_realistic_values(self):
        """Test with realistic medical values."""
        realistic_data = {
            "age": 45.0,     # 45 years old
            "sex": 0.0,      # Female
            "cp": 2.0,       # Atypical angina
            "trestbps": 130.0,  # Resting blood pressure
            "chol": 200.0,   # Cholesterol level
            "fbs": 0.0,      # Fasting blood sugar < 120
            "restecg": 1.0,  # ST-T wave abnormality
            "thalach": 175.0,   # Max heart rate
            "exang": 0.0,    # No exercise induced angina
            "oldpeak": 1.0,  # ST depression
            "slope": 1.0,    # Upsloping
            "ca": 0.0,       # Number of major vessels
            "thal": 2.0      # Normal thalassemia
        }
        
        patient = PatientData(**realistic_data)
        
        # Verify all values are stored correctly
        assert patient.age == 45.0
        assert patient.sex == 0.0
        assert patient.cp == 2.0
        assert patient.trestbps == 130.0
        assert patient.chol == 200.0
        assert patient.thalach == 175.0