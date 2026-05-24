import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, BigInteger, Float, DateTime, ForeignKey, Enum, JSON, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class AssetStatus(enum.Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    ANALYZED = "Analyzed"
    ERROR = "Error"

class ProposalStatus(enum.Enum):
    PROPOSED = "Proposed"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    EXECUTED = "Executed"
    CONFLICTED = "Conflicted"

class ActionOutcome(enum.Enum):
    SUCCESS = "Success"
    FAILURE = "Failure"

class Drive(Base):
    __tablename__ = "drives"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    filesystem_type = Column(String)
    total_space = Column(BigInteger)
    used_space = Column(BigInteger)
    last_scanned = Column(DateTime)
    assets = relationship("Asset", back_populates="drive", cascade="all, delete-orphan")

class Asset(Base):
    __tablename__ = "assets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drive_id = Column(UUID(as_uuid=True), ForeignKey("drives.id"), nullable=False)
    filename = Column(String, nullable=False)
    extension = Column(String)
    full_path = Column(String, nullable=False, index=True)
    size_bytes = Column(BigInteger)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    hash_sha256 = Column(String)
    status = Column(Enum(AssetStatus), default=AssetStatus.PENDING)
    drive = relationship("Drive", back_populates="assets")
    ai_metadata = relationship("AIMetadata", back_populates="asset", uselist=False, cascade="all, delete-orphan")
    proposals = relationship("MoveProposal", back_populates="asset", cascade="all, delete-orphan")

class AIMetadata(Base):
    __tablename__ = "ai_metadata"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    summary = Column(Text)
    detected_topics = Column(JSONB)
    detected_entities = Column(JSONB)
    image_description = Column(Text)
    suggested_tags = Column(JSONB)
    confidence_score = Column(Float)
    model_used = Column(String)
    asset = relationship("Asset", back_populates="ai_metadata")

class MoveProposal(Base):
    __tablename__ = "move_proposals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    source_path = Column(String, nullable=False)
    suggested_path = Column(String, nullable=False)
    reason = Column(Text)
    status = Column(Enum(ProposalStatus), default=ProposalStatus.PROPOSED)
    asset = relationship("Asset", back_populates="proposals")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action_type = Column(String, nullable=False)
    details = Column(JSONB)
    outcome = Column(Enum(ActionOutcome))
