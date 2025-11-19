from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON
Base = declarative_base()

class Ujianfonem(Base):
    __tablename__ = 'ujianfonem'

    idujian = Column(Integer, primary_key=True, autoincrement=True)
    idmateriujian = Column(Integer, ForeignKey('materiujian.idmateriujian'))
    idtalent = Column(Integer, ForeignKey('talent.idtalent'))
    kategori = Column(String(255))
    nilai = Column(Float)
    waktuujian = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Detailujianfonem(Base):
    __tablename__ = 'detailujianfonem'

    iddetail = Column(Integer, primary_key=True, autoincrement=True)
    idujian = Column(Integer, ForeignKey('ujianfonem.idujian'))
    idsoal = Column(Integer, ForeignKey('materiujiankalimat.idmateriujiankalimat'))
    nilai = Column(Float)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Materiujian(Base):
    __tablename__ = 'materiujian'

    idmateriujian = Column(Integer, primary_key=True, autoincrement=True)
    kategori = Column(String(255))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Materiujiankalimat(Base):
    __tablename__ = 'materiujiankalimat'

    idmateriujiankalimat = Column(Integer, primary_key=True, autoincrement=True)
    idmateriujian = Column(Integer, ForeignKey('materiujian.idmateriujian'))
    kalimat = Column(String(255))
    fonem = Column(String(255))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Hasillatihanfonem(Base):
    __tablename__ = 'hasillatihanfonem'

    idhasilfonem = Column(Integer, primary_key=True, autoincrement=True)
    typelatihan = Column(String(255))
    idtalent = Column(Integer, ForeignKey('talent.idtalent'))
    idsoal = Column(Integer)
    nilai = Column(Float)
    waktulatihan = Column(DateTime)
    phoneme_comparison = Column(JSON) 

class Hasillatihanpercakapan(Base):
    __tablename__ = 'hasillatihanpercakapan'

    idhasilpercakapan = Column(Integer, primary_key=True, autoincrement=True)
    idtalent = Column(Integer, ForeignKey('talent.idtalent'))
    idmateripercakapan = Column(Integer, ForeignKey('materipercakapan.idmateripercakapan'))
    wpm = Column(Float)
    grammar = Column(String(255))
    waktulatihan = Column(DateTime)

class Hasillatihaninterview(Base):
    __tablename__ = 'hasillatihaninterview'

    idhasilinterview = Column(Integer, primary_key=True, autoincrement=True)
    idtalent = Column(Integer, ForeignKey('talent.idtalent'))
    waktulatihan = Column(DateTime)
    feedback = Column(Text)
    wpm = Column(Float)
    grammar = Column(String(255))

class Manajemen(Base):
    __tablename__ = 'manajemen'

    idmanajemen = Column(Integer, primary_key=True)
    namamanajemen = Column(String(255))
    email = Column(String(255))
    password = Column(String(255))

class Materifonemkalimat(Base):
    __tablename__ = 'materifonemkalimat'

    idmaterifonemkalimat = Column(Integer, primary_key=True, autoincrement=True)
    kategori = Column(String(255))
    kalimat = Column(String(255))
    fonem = Column(String(255))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Materifonemkata(Base):
    __tablename__ = 'materifonemkata'

    idmaterifonemkata = Column(Integer, primary_key=True, autoincrement=True)
    kategori = Column(String(255))
    kata = Column(String(255))
    fonem = Column(String(255))
    meaning = Column(String(255))
    definition = Column(String(255))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Materipercakapan(Base):
    __tablename__ = 'materipercakapan'

    idmateripercakapan = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String(255))

class Materiinterview(Base):
    __tablename__ = 'materiinterview'

    idmateriinterview = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String(255))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, nullable=False, server_default='true')

class Talent(Base):
    __tablename__ = 'talent'

    idtalent = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(String(255))
    email = Column(String(255), unique=True)
    password = Column(String(255))
    pretest_score = Column(Float)
    role = Column(String(50), default='talent')