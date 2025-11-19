# config/phoneme_constants.py

class PhonemeConstants:
    
    SIMILAR_PHONEMES = {
        "i": ["ɪ", "j"],
        "ɪ": ["ɛ"],
        "ɛ": ["æ"],
        "u": ["ʊ", "w"],
        "p": ["b"],
        "t": ["d"],
        "k": ["g"],
        "f": ["v"],
        "θ": ["ð"],
        "s": ["z"],
        "ʃ": ["ʒ"],
        "tʃ": ["dʒ"],
        "n": ["m", "ŋ"],
        "l": ["r"],
        "ə": ["ʌ", "ɚ"],
        "ɑ": ["ɔ", "ʌ"],
        "ɔ": ["oʊ"],
        "oʊ": ["ʊ"],
        "eɪ": ["ɛ", "ɪ"],
        "aɪ": ["ɪ", "ɑ"],
        "ɔɪ": ["ɔ", "ɪ"],
        "aʊ": ["ʊ", "ɑ"],
    }
    
    VOWEL_PHONEMES = [
        "i", "ɪ", "ɛ", "æ", "ə", "ɚ", "ʌ", "ɑ", "ɔ", "ʊ", "u"
    ]
    
    DIPHTHONG_PHONEMES = [
        "eɪ", "aɪ", "ɔɪ", "aʊ", "oʊ"
    ]
    
    CONSONANT_PHONEMES = [
        "p", "b", "t", "d", "k", "g", "f", "v", "θ", "ð",
        "s", "z", "ʃ", "ʒ", "tʃ", "dʒ", "h", "m", "n", "ŋ", "l", "r", "j", "w"
    ]
    
    ALL_PHONEMES = VOWEL_PHONEMES + DIPHTHONG_PHONEMES + CONSONANT_PHONEMES
    
    @classmethod
    def get_all_phonemes(cls) -> list:
        return cls.ALL_PHONEMES
    
    @classmethod
    def get_similar_phonemes(cls, phoneme: str) -> list:
        if phoneme not in cls.ALL_PHONEMES:
            return []

        direct_similars = set(cls.SIMILAR_PHONEMES.get(phoneme, []))
        
        inverse_similars = set()
        for key, values in cls.SIMILAR_PHONEMES.items():
            if phoneme in values:
                inverse_similars.add(key)
                inverse_similars.update(cls.SIMILAR_PHONEMES.get(key, []))

        all_similars = direct_similars.union(inverse_similars)
        all_similars.discard(phoneme)
        
        return sorted(list(all_similars))
    
    @classmethod
    def is_valid_phoneme(cls, phoneme: str) -> bool:
        """Check if phoneme is valid"""
        return phoneme in cls.ALL_PHONEMES
    
    @classmethod
    def create_minimal_pair_category(cls, phoneme1: str, phoneme2: str) -> str:
        return "-".join(sorted([phoneme1, phoneme2]))
    
    @classmethod
    def parse_minimal_pair_category(cls, category: str) -> list[str]:
        if "-" in category:
            return category.split("-")
        return [category]
    
    @classmethod
    def get_possible_minimal_pairs(cls, phoneme: str) -> list:
        """Get all possible minimal pair categories for a phoneme."""
        similar = cls.get_similar_phonemes(phoneme)
        return sorted([cls.create_minimal_pair_category(phoneme, s) for s in similar])
    
    @classmethod
    def validate_minimal_pair_category(cls, category: str) -> bool:
        """Validate a phoneme category, including groups of 3."""
        phonemes_to_check = cls.parse_minimal_pair_category(category)
        if len(phonemes_to_check) < 2:
            return False
        if not all(cls.is_valid_phoneme(p) for p in phonemes_to_check):
            return False

        first_phoneme = phonemes_to_check[0]
        similar_to_first = cls.get_similar_phonemes(first_phoneme)
        
        return all(p in similar_to_first for p in phonemes_to_check[1:])
    
    @classmethod
    def parse_similar_phonemes_category(cls, category: str) -> list[str]:
        """Parse similar phonemes category to list of phonemes"""
        if "-" in category:
            return [p.strip() for p in category.split("-") if p.strip()]
        return [category]

    @classmethod
    def validate_similar_phonemes_category(cls, category: str) -> bool:
        """Validate similar phonemes category (supports multiple phonemes)"""
        phonemes = cls.parse_similar_phonemes_category(category)
        if len(phonemes) < 2:
            return False
        return all(cls.is_valid_phoneme(p) for p in phonemes)

    @classmethod
    def create_similar_phonemes_category(cls, *phonemes: str) -> str:
        """Create similar phonemes category from multiple phonemes"""
        return "-".join(sorted(list(set(phonemes))))

    @classmethod
    def get_all_similar_combinations(cls, phoneme: str) -> list[str]:
        """Get all possible similar phoneme combinations for a given phoneme"""
        similar = cls.get_similar_phonemes(phoneme)
        combinations = set()
        
        for s in similar:
            combinations.add(cls.create_minimal_pair_category(phoneme, s))
        
        if len(similar) >= 2:
            for i in range(len(similar)):
                for j in range(i + 1, len(similar)):
                    combinations.add(cls.create_similar_phonemes_category(phoneme, similar[i], similar[j]))
        
        return sorted(list(combinations))

    @classmethod
    def is_valid_similar_combination(cls, category: str) -> bool:
        """Check if a category represents a valid similar phonemes combination"""
        return cls.validate_minimal_pair_category(category)

class MaterialType:
    WORD = "word"
    SENTENCE = "sentence"
    EXAM = "exam"
    TALENT = "talent"
    INTERVIEW = "interview"

class ImportTemplateFields:
    PHONEME_WORDS = {
        "required_columns": ["kategori", "kata", "fonem", "arti", "definisi"],
        "column_descriptions": {
            "kategori": "Fonem tunggal (contoh: i, ɪ, p, b) - tanpa tanda /",
            "kata": "Kata dalam bahasa Inggris",
            "fonem": "Target fonem dalam kata (sama dengan kategori)",
            "arti": "Arti kata dalam bahasa Indonesia", 
            "definisi": "Definisi lengkap kata"
        },
        "example_data": [
            ['i', 'believe', 'bɪliv', 'percaya', 'Menerima sesuatu sebagai kebenaran.'],
            ['ɪ', 'with', 'wɪð', 'dengan', 'Ditemani oleh; bersama.'],
            ['p', 'push', 'pʊʃ', 'mendorong', 'Memberi tekanan agar bergerak maju.']
        ]
    }
    
    EXERCISE_PHONEME = {
        "required_columns": ["kategori", "kalimat", "fonem"],
        "column_descriptions": {
            "kategori": "Similar phonemes (contoh: i-ɪ, p-b, ə-ʌ-ɚ, ɪ-i-ɛ) - tanpa tanda /",
            "kalimat": "Kalimat latihan (minimal 10 kata)",
            "fonem": "Transkripsi fonetik lengkap yang harus mengandung SEMUA phoneme dari kategori"
        },
        "example_data": [
            ['i-ɪ', 'He did see if this big team is really in it.', 'hi dɪd si ɪf ðɪs bɪg tim ɪz rɪəli ɪn ɪt'],
            ['p-b', 'The big problem is people buy poor quality baby products.', 'ðə bɪg prɔbləm ɪz pipəl baɪ pʊər kwɔləti beɪbi prɔdʌkts']
        ]
    }
    
    EXAM_PHONEME = {
        "required_columns": ["kategori", "kalimat_1", "kalimat_2", "kalimat_3", "kalimat_4", "kalimat_5",
                        "kalimat_6", "kalimat_7", "kalimat_8", "kalimat_9", "kalimat_10",
                        "fonem_1", "fonem_2", "fonem_3", "fonem_4", "fonem_5",
                        "fonem_6", "fonem_7", "fonem_8", "fonem_9", "fonem_10"],
        "column_descriptions": {
            "kategori": "Similar phonemes (contoh: i-ɪ, p-b, ə-ʌ-ɚ, ɪ-i-ɛ) - tanpa tanda /",
            "kalimat_1 sampai kalimat_10": "10 kalimat ujian (minimal 10 kata per kalimat)",
            "fonem_1 sampai fonem_10": "Transkripsi fonetik untuk masing-masing kalimat yang harus mengandung SEMUA phoneme dari kategori"
        },
        "example_data": [
            ["i-ɪ",
            "The green team will win this big game with ease.",
            "It is a big risk to leave the key in it.",
            "Did he believe this is the peak of his career?",
            "Please bring the little bit of cheese we need now.",
            "This deep shipping container is filled with interesting green things.",
            "He did sit in the seat he was given, feeling ill.",
            "We feel that it is easy to win this game.",
            "The machine is still missing its most important inner piece.",
            "Give me the keys to this big green fishing boat.",
            "Each ship is filled with deep green tea from India.",
            "ðə grin tim wɪl wɪn ðɪs bɪg geɪm wɪθ iz",
            "ɪt ɪz ə bɪg rɪsk tə liv ðə ki ɪn ɪt",
            "dɪd hi bɪliv ðɪs ɪz ðə pik əv hɪz kərɪər",
            "pliz brɪŋ ðə lɪtəl bɪt əv tʃiz wi nid naʊ",
            "ðɪs dip ʃɪpɪŋ kənteɪnər ɪz fɪld wɪθ ɪntrəstɪŋ grin θɪŋz",
            "hi dɪd sɪt ɪn ðə sit hi wɒz gɪvən filɪŋ ɪl",
            "wi fil ðæt ɪt ɪz izi tə wɪn ðɪs geɪm",
            "ðə məʃin ɪz stɪl mɪsɪŋ ɪts məʊst ɪmpɔrtənt ɪnər pis",
            "gɪv mi ðə kiz tə ðɪs bɪg grin fɪʃɪŋ bəʊt",
            "itʃ ʃɪp ɪz fɪld wɪθ dip grin ti frəm ɪndiə"]
        ]
    }
    
    TALENT = {
        "required_columns": ["nama", "email", "role", "password"],
        "column_descriptions": {
            "nama": "Nama lengkap talenta",
            "email": "Alamat email unik talenta",
            "role": "Peran atau posisi talenta (misal: Software Engineer)",
            "password": "Password untuk login (minimal 6 karakter)"
        },
        "example_data": [
            ['Brahmantya', 'brahmantyaganteng@gmail.com', 'Mobile Developer', 'Brahmantya987'],
            ['Hafidzon', 'hafidzonganteng@gmail.com', 'Backend Developer', 'Hafidzon987'],
            ['Vico', 'vicoganteng@gmail.com', 'Full Stack Developer', 'Vico987']
        ]
    }
    
    INTERVIEW_QUESTIONS = {
        "required_columns": ["pertanyaan"],
        "column_descriptions": {
            "pertanyaan": "Pertanyaan interview (minimal 5 kata)"
        },
        "example_data": [
            ["Tell me about yourself and your background in detail."],
            ["What are your greatest strengths and how do they help you?"],
            ["Describe a challenging situation you faced and how you overcame it."],
            ["Where do you see yourself in five years from now?"]
        ]
    }