from dotenv import load_dotenv

load_dotenv()

from parser.main import LeadsGenerator


l = LeadsGenerator()

print("START")

l.generate(session_id=1, lead_id=1)

print("END")
