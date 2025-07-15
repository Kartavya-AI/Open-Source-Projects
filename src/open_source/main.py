from src.open_source.crew import OpenSourceCrew

def main():
    business_requirement = input("Please provide your business requirement: ")
    crew = OpenSourceCrew(business_requirement)
    result = crew.run()
    print(result)

if __name__ == "__main__":
    main()
