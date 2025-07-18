'''
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
sys.modules["sqlite3.dbapi2"] = sys.modules["pysqlite3.dbapi2"]
'''
from src.open_source.crew import OpenSourceCrew

def main():
    business_requirement = input("Please provide your business requirement: ")
    crew = OpenSourceCrew(business_requirement)
    result = crew.run()
    print(result)

if __name__ == "__main__":
    main()
