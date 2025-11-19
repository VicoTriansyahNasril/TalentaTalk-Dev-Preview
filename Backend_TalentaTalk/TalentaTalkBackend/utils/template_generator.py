# utils/template_generator.py
import pandas as pd
import io
from typing import Dict, List, Any
from config.phoneme_constants import ImportTemplateFields, MaterialType, PhonemeConstants

class TemplateGenerator:
    
    @staticmethod
    def generate_phoneme_words_template() -> Dict[str, Any]:
        template_info = ImportTemplateFields.PHONEME_WORDS
        
        df = pd.DataFrame(
            data=template_info["example_data"],
            columns=template_info["required_columns"]
        )
        
        return {
            "template_name": "Phoneme Words Template",
            "dataframe": df,
            "required_columns": template_info["required_columns"],
            "column_descriptions": template_info["column_descriptions"],
            "instructions": [
                "1. Kategori harus berupa fonem tunggal (contoh: i, ɪ, p, b)",
                "2. Tidak menggunakan tanda / di awal dan akhir",
                "3. Fonem harus sama dengan kategori untuk materi kata",
                "4. Semua kolom wajib diisi",
                "5. Satu baris = satu kata"
            ]
        }
    
    @staticmethod
    def generate_exercise_phoneme_template() -> Dict[str, Any]:
        template_info = ImportTemplateFields.EXERCISE_PHONEME
        
        df = pd.DataFrame(
            data=template_info["example_data"],
            columns=template_info["required_columns"]
        )
        
        return {
            "template_name": "Exercise Phoneme Template",
            "dataframe": df,
            "required_columns": template_info["required_columns"],
            "column_descriptions": template_info["column_descriptions"],
            "instructions": [
                "1. Kategori HARUS berupa minimal pairs (contoh: i-ɪ, p-b, s-z)",
                "2. Tidak menggunakan tanda / di awal dan akhir",
                "3. Kalimat minimal 10 kata",
                "4. Fonem adalah target yang difokuskan dalam kalimat",
                "5. Fonem harus salah satu dari minimal pair kategori",
                "6. Satu baris = satu kalimat latihan"
            ]
        }
    
    @staticmethod
    def generate_exam_phoneme_template() -> Dict[str, Any]:
        template_info = ImportTemplateFields.EXAM_PHONEME
        
        df = pd.DataFrame(
            data=template_info["example_data"],
            columns=template_info["required_columns"]
        )
        
        return {
            "template_name": "Exam Phoneme Template",
            "dataframe": df,
            "required_columns": template_info["required_columns"],
            "column_descriptions": template_info["column_descriptions"],
            "instructions": [
                "1. Kategori HARUS berupa minimal pairs (contoh: i-ɪ, p-b, s-z)",
                "2. Tidak menggunakan tanda / di awal dan akhir", 
                "3. Setiap exam harus memiliki tepat 10 kalimat",
                "4. Setiap kalimat minimal 10 kata",
                "5. Fonem_1 sampai fonem_10 sesuai dengan target di masing-masing kalimat",
                "6. Semua fonem harus dari kategori minimal pair yang ditentukan",
                "7. Satu baris = satu set ujian lengkap (10 kalimat)"
            ]
        }
    
    @staticmethod
    def generate_interview_questions_template() -> Dict[str, Any]:
        template_info = ImportTemplateFields.INTERVIEW_QUESTIONS
        
        df = pd.DataFrame(
            data=template_info["example_data"],
            columns=template_info["required_columns"]
        )
        
        return {
            "template_name": "Interview Questions Template",
            "dataframe": df,
            "required_columns": template_info["required_columns"],
            "column_descriptions": template_info["column_descriptions"],
            "instructions": [
                "1. Pertanyaan minimal 5 kata",
                "2. Gunakan bahasa Inggris yang jelas",
                "3. Hindari pertanyaan yang terlalu personal",
                "4. Satu baris = satu pertanyaan interview"
            ]
        }

    @staticmethod
    def generate_talent_template() -> Dict[str, Any]:
        template_info = ImportTemplateFields.TALENT
        
        df = pd.DataFrame(
            data=template_info["example_data"],
            columns=template_info["required_columns"]
        )
        
        return {
            "template_name": "Talent Import Template",
            "dataframe": df,
            "required_columns": template_info["required_columns"],
            "column_descriptions": template_info["column_descriptions"],
            "instructions": [
                "1. Semua kolom (nama, email, role, password) wajib diisi.",
                "2. Email harus unik dan belum terdaftar di sistem.",
                "3. Password harus memiliki minimal 6 karakter.",
                "4. Role adalah peran dari talenta (misal: Software Engineer, QA Tester).",
                "5. Satu baris = satu data talenta baru."
            ]
        }
    
    @staticmethod
    def create_excel_buffer(template_data: Dict[str, Any]) -> io.BytesIO:
        buffer = io.BytesIO()
        
        try:
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                template_data["dataframe"].to_excel(
                    writer, 
                    sheet_name='Data Template', 
                    index=False
                )
                
                instructions_df = pd.DataFrame({
                    'Instructions': template_data["instructions"]
                })
                instructions_df.to_excel(
                    writer, 
                    sheet_name='Instructions', 
                    index=False
                )

                descriptions_df = pd.DataFrame([
                    {"Column": col, "Description": desc} 
                    for col, desc in template_data["column_descriptions"].items()
                ])
                descriptions_df.to_excel(
                    writer, 
                    sheet_name='Column Descriptions', 
                    index=False
                )
                
        except Exception as e:
            print(f"Error creating Excel buffer: {str(e)}")
            raise e
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def get_template_by_type(material_type: str) -> Dict[str, Any]:
        template_map = {
            MaterialType.WORD: TemplateGenerator.generate_phoneme_words_template,
            MaterialType.SENTENCE: TemplateGenerator.generate_exercise_phoneme_template,
            MaterialType.EXAM: TemplateGenerator.generate_exam_phoneme_template,
            MaterialType.TALENT: TemplateGenerator.generate_talent_template,
            MaterialType.INTERVIEW: TemplateGenerator.generate_interview_questions_template
        }
        
        if material_type not in template_map:
            raise ValueError(f"Unknown material type: {material_type}")
        
        return template_map[material_type]()
    
    @staticmethod
    def validate_import_file(df: pd.DataFrame, material_type: str) -> Dict[str, Any]:
        template_data = TemplateGenerator.get_template_by_type(material_type)
        required_columns = template_data["required_columns"]
        
        errors = []
        warnings = []
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        if df.empty:
            errors.append("File is empty")
        
        empty_rows = df.isnull().all(axis=1).sum()
        if empty_rows > 0:
            warnings.append(f"Found {empty_rows} completely empty rows")
        
        if material_type == MaterialType.EXAM:
            sentence_columns = [col for col in df.columns if col.startswith('kalimat_')]
            if len(sentence_columns) != 10:
                errors.append("Exam template must have exactly 10 sentence columns (kalimat_1 to kalimat_10)")
            
            fonem_columns = [col for col in df.columns if col.startswith('fonem_')]
            if len(fonem_columns) != 10:
                errors.append("Exam template must have exactly 10 phoneme columns (fonem_1 to fonem_10)")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_rows": len(df),
            "empty_rows": empty_rows
        }

class ImportProcessor:
    
    @staticmethod
    def process_phoneme_words(df: pd.DataFrame) -> Dict[str, Any]:
        success_count = 0
        error_count = 0
        errors = []
        processed_data = []
        
        for idx, row in df.iterrows():
            try:
                kategori = str(row.get('kategori', '')).strip()
                kata = str(row.get('kata', '')).strip()
                fonem = str(row.get('fonem', '')).strip()
                arti = str(row.get('arti', '')).strip()
                definisi = str(row.get('definisi', '')).strip()
                
                if not all([kategori, kata, fonem, arti]):
                    errors.append({
                        "row": idx + 2,
                        "reason": "Missing required fields"
                    })
                    error_count += 1
                    continue
                
                if not PhonemeConstants.is_valid_phoneme(kategori):
                    errors.append({
                        "row": idx + 2,
                        "reason": f"Invalid phoneme category: {kategori}"
                    })
                    error_count += 1
                    continue
                
                if kategori not in fonem:
                    errors.append({
                        "row": idx + 2,
                        "reason": f"Phoneme '{fonem}' must match category '{kategori}' for word materials"
                    })
                    error_count += 1
                    continue
                
                processed_data.append({
                    "kategori": kategori,
                    "kata": kata,
                    "fonem": fonem,
                    "meaning": arti,
                    "definition": definisi
                })
                success_count += 1
                
            except Exception as e:
                errors.append({
                    "row": idx + 2,
                    "reason": f"Processing error: {str(e)}"
                })
                error_count += 1
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors,
            "processed_data": processed_data
        }
    
    @staticmethod
    def process_exercise_phoneme(df: pd.DataFrame) -> Dict[str, Any]:
        success_count = 0
        error_count = 0
        errors = []
        processed_data = []
        
        for idx, row in df.iterrows():
            try:
                kategori = str(row.get('kategori', '')).strip()
                kalimat = str(row.get('kalimat', '')).strip()
                fonem = str(row.get('fonem', '')).strip()
                
                if not all([kategori, kalimat, fonem]):
                    errors.append({
                        "row": idx + 2,
                        "reason": "Missing required fields"
                    })
                    error_count += 1
                    continue
                
                if "-" not in kategori:
                    errors.append({
                        "row": idx + 2,
                        "reason": f"Category must be minimal pairs (e.g., 'i-ɪ', 'p-b'), got: {kategori}"
                    })
                    error_count += 1
                    continue
                
                if not PhonemeConstants.validate_minimal_pair_category(kategori):
                    errors.append({
                        "row": idx + 2,
                        "reason": f"Invalid minimal pair category: {kategori}"
                    })
                    error_count += 1
                    continue
                
                if not PhonemeConstants.is_valid_phoneme(fonem):
                    errors.append({
                        "row": idx + 2,
                        "reason": f"Invalid phoneme: {fonem}"
                    })
                    error_count += 1
                    continue
                
                phoneme1, phoneme2 = PhonemeConstants.parse_minimal_pair_category(kategori)
                if fonem not in [phoneme1, phoneme2]:
                    errors.append({
                        "row": idx + 2,
                        "reason": f"Phoneme '{fonem}' must be one of [{phoneme1}, {phoneme2}] for category '{kategori}'"
                    })
                    error_count += 1
                    continue
                
                if len(kalimat.split()) < 10:
                    errors.append({
                        "row": idx + 2,
                        "reason": "Sentence must contain at least 10 words"
                    })
                    error_count += 1
                    continue
                
                processed_data.append({
                    "kategori": kategori,
                    "kalimat": kalimat,
                    "fonem": fonem
                })
                success_count += 1
                
            except Exception as e:
                errors.append({
                    "row": idx + 2,
                    "reason": f"Processing error: {str(e)}"
                })
                error_count += 1
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors,
            "processed_data": processed_data
        }
    
    @staticmethod
    def process_exam_phoneme(df: pd.DataFrame) -> Dict[str, Any]:
        success_count = 0
        error_count = 0
        errors = []
        processed_data = []
        
        for idx, row in df.iterrows():
            try:
                kategori = str(row.get('kategori', '')).strip()
                
                if not kategori or "-" not in kategori:
                    errors.append({
                        "row": idx + 2,
                        "reason": "Category must be a minimal pair (e.g., 'i-ɪ', 'p-b')"
                    })
                    error_count += 1
                    continue
                
                if not PhonemeConstants.validate_minimal_pair_category(kategori):
                    errors.append({
                        "row": idx + 2,
                        "reason": f"Invalid minimal pair category: {kategori}"
                    })
                    error_count += 1
                    continue
                
                phoneme1, phoneme2 = PhonemeConstants.parse_minimal_pair_category(kategori)
                sentences_and_phonemes = []
                
                for i in range(1, 11):
                    kalimat_col = f'kalimat_{i}'
                    fonem_col = f'fonem_{i}'
                    
                    kalimat = str(row.get(kalimat_col, '')).strip()
                    fonem = str(row.get(fonem_col, '')).strip()
                    
                    if not kalimat or not fonem:
                        errors.append({
                            "row": idx + 2,
                            "reason": f"Missing data for sentence {i}"
                        })
                        error_count += 1
                        break
                    
                    if len(kalimat.split()) < 10:
                        errors.append({
                            "row": idx + 2,
                            "reason": f"Sentence {i} must contain at least 10 words"
                        })
                        error_count += 1
                        break
                    
                    if not PhonemeConstants.is_valid_phoneme(fonem):
                        errors.append({
                            "row": idx + 2,
                            "reason": f"Invalid phoneme in sentence {i}: {fonem}"
                        })
                        error_count += 1
                        break
                    
                    if fonem not in [phoneme1, phoneme2]:
                        errors.append({
                            "row": idx + 2,
                            "reason": f"Phoneme '{fonem}' in sentence {i} must be one of [{phoneme1}, {phoneme2}] for category '{kategori}'"
                        })
                        error_count += 1
                        break
                    
                    sentences_and_phonemes.append({
                        "sentence": kalimat,
                        "phoneme": fonem
                    })
                
                if len(sentences_and_phonemes) == 10:
                    processed_data.append({
                        "kategori": kategori,
                        "sentences_and_phonemes": sentences_and_phonemes
                    })
                    success_count += 1
                
            except Exception as e:
                errors.append({
                    "row": idx + 2,
                    "reason": f"Processing error: {str(e)}"
                })
                error_count += 1
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors,
            "processed_data": processed_data
        }