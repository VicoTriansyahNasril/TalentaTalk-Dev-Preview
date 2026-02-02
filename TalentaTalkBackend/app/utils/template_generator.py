import pandas as pd
import io
from typing import List
from app.core.exceptions import AppError

class TemplateGenerator:
    
    @staticmethod
    def _create_excel_buffer(data: List[List[str]], columns: List[str], instructions: List[str]) -> io.BytesIO:
        try:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Sheet 1: Template Data
                df = pd.DataFrame(data, columns=columns)
                df.to_excel(writer, sheet_name='Data Template', index=False)
                
                # Sheet 2: Instructions
                df_inst = pd.DataFrame({'Instructions': instructions})
                df_inst.to_excel(writer, sheet_name='Instructions', index=False)
                
                # Auto-adjust column width
                worksheet = writer.sheets['Data Template']
                for i, col in enumerate(columns):
                    worksheet.set_column(i, i, 20)
                    
            buffer.seek(0)
            return buffer
        except Exception as e:
            raise AppError(status_code=500, detail=f"Failed to generate template: {str(e)}")

    @staticmethod
    def get_phoneme_word_template() -> io.BytesIO:
        columns = ["kategori", "kata", "fonem", "arti", "definisi"]
        data = [
            ['i', 'believe', 'bɪliv', 'percaya', 'Menerima kebenaran.'],
            ['p', 'push', 'pʊʃ', 'mendorong', 'Memberi tekanan.']
        ]
        instructions = [
            "1. Kategori: Fonem tunggal (contoh: i, p, b)",
            "2. Fonem: Transkripsi IPA",
            "3. Semua kolom wajib diisi"
        ]
        return TemplateGenerator._create_excel_buffer(data, columns, instructions)

    @staticmethod
    def get_phoneme_sentence_template() -> io.BytesIO:
        columns = ["kategori", "kalimat", "fonem"]
        data = [
            ['i-ɪ', 'He did see if this big team is really in it.', 'hi dɪd si ɪf ðɪs bɪg tim ɪz rɪəli ɪn ɪt']
        ]
        instructions = [
            "1. Kategori: Minimal pairs (contoh: i-ɪ, p-b)",
            "2. Kalimat minimal 10 kata"
        ]
        return TemplateGenerator._create_excel_buffer(data, columns, instructions)

    @staticmethod
    def get_phoneme_exam_template() -> io.BytesIO:
        # Generate dynamic columns for 10 sentences
        columns = ["kategori"]
        for i in range(1, 11):
            columns.extend([f"kalimat_{i}", f"fonem_{i}"])
            
        data_row = ["i-ɪ"]
        for _ in range(10):
            data_row.extend(["Example Sentence", "fonem"])
            
        data = [data_row]
        instructions = [
            "1. Kategori: Minimal pairs (contoh: i-ɪ)",
            "2. Wajib mengisi 10 kalimat dan 10 fonem lengkap",
            "3. Satu baris = Satu paket ujian"
        ]
        return TemplateGenerator._create_excel_buffer(data, columns, instructions)

    @staticmethod
    def get_talent_template() -> io.BytesIO:
        columns = ["nama", "email", "role", "password"]
        data = [
            ['John Doe', 'john@example.com', 'Software Engineer', 'Password123']
        ]
        instructions = [
            "1. Email harus unik",
            "2. Password minimal 6 karakter",
            "3. Role opsional (default: talent)"
        ]
        return TemplateGenerator._create_excel_buffer(data, columns, instructions)