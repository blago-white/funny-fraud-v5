from dotenv import load_dotenv

load_dotenv()

from parser.main import LeadsGenerator
from parser.transfer import LeadsGenerationSession


l = LeadsGenerator()

print("START")

l.generate(session_id=1, lead_id=1, session=LeadsGenerationSession(
    count=1,
    ref_link="https://finuslugi.ru/podbor_zajma?utm_source=leadssu&utm_medium=affiliate&utm_campaign=pr:kredity&utm_term=53f3ff45afb1a75efefb7017ab3d2638&offer_id=11437&utm_content=125100"
))

print("END")
