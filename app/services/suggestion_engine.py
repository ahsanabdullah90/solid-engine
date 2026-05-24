from app.database.models import Asset, AIMetadata, MoveProposal, ProposalStatus
import os

class SuggestionEngine:
    def __init__(self, db_session):
        self.db = db_session
    def generate_proposals(self):
        assets = self.db.query(Asset).join(AIMetadata).outerjoin(MoveProposal).filter(MoveProposal.id == None).all()
        for asset in assets:
            proposal = self._analyze_asset(asset)
            if proposal: self.db.add(proposal)
        self.db.commit()

    def _analyze_asset(self, asset):
        metadata = asset.ai_metadata
        target_dir = None
        topics = [t.lower() for t in (metadata.detected_topics or [])]
        if any(k in topics for k in ['invoice', 'finance']): target_dir = "Finance"
        elif any(k in topics for k in ['technical', 'code']): target_dir = "Technical"
        if target_dir:
            suggested_path = os.path.join(os.path.dirname(asset.full_path), target_dir, asset.filename)
            return MoveProposal(asset_id=asset.id, source_path=asset.full_path, suggested_path=suggested_path, reason="AI Content Analysis", status=ProposalStatus.PROPOSED)
        return None
