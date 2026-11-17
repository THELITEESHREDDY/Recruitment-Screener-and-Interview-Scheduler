from backend.db.base import Base
from backend.db.connection import engine
# Import every model module here so SQLAlchemy registers its tables.
from backend.models.job import JobDescription
from backend.models.job_ranking_rubrik import JobRankingRubric
from backend.models.candidate import Candidate
from backend.models.candidate_ranking import CandidateRanking
from backend.models.ideal_candidate import IdealCandidateModel
# Import your IdealCandidateModel module here as well.


def initialize_database():
    Base.metadata.create_all(bind=engine)