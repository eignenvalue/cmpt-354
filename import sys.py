import sys
import subprocess

import sqlite3
##functions do not work currently except for exit 
def find_open_competitions():
    pu = PromptUtils(Screen())
    # PromptUtils.input() returns an InputResult
    result = pu.input("enter the month you would like to find competitions for")
    
    pu.println("\nYou entered:", result.input_string, "\n")
    pu.enter_to_continue()


def find_largest_amount(area):
    print(area)


def find_awarded_before_date(date):
    print(date)


def calculate_discrepancy(cur):

    area = input("Enter the area you would like the discrepancy for: ")

    query = """
    SELECT AVG(ABS(requestedAmount - rewardedAmount)) AS avg_discrepancy
    FROM GrantProposal
    JOIN GrantCompetition ON GrantCompetition.competitionID = GrantProposal.competitionID
    WHERE GrantCompetition.area = ?
    """
    cur.execute(query,(area,))
    result = cur.fetchone()
    

    if result[0] is not None:
        print("The average requested /awaraded discrepnacy for the area " + area + " is :")
        print(result[0])
    else:
        print("No data available for area " + area)

def list_reviewers_not_in_conflict(cur):
    id = int(input("Enter proposal ID: "))
     # Query to select reviewers who are not in conflict with the proposal and have not reached the maximum of three proposals to review
    query = """
    SELECT R.reviewerID, R.firstName, R.lastName
    FROM Reviewer R
    LEFT JOIN ConflictsOfInterest C ON R.reviewerID = C.reviewerID
    LEFT JOIN (
        SELECT reviewerID, COUNT(*) AS assigned_proposals
        FROM ReviewerAssignment
        GROUP BY reviewerID
    ) AS A ON R.reviewerID = A.reviewerID
    WHERE (NOT EXISTS (
                SELECT 1
                FROM ConflictsOfInterest
                WHERE conflictedResearcherID = ? AND reviewerID = R.reviewerID
            )
        OR (A.assigned_proposals IS NULL OR A.assigned_proposals < 3))
    """
    
    cur.execute(query, (id, ))
    eligible_reviewers = cur.fetchall()

    if eligible_reviewers:
        print("Eligible Reviewers:")
        for reviewer in eligible_reviewers:
            print(f"{reviewer[0]} - {reviewer[1]} {reviewer[2]}")
        
        reviewer_ids = input("Enter reviewer IDs (comma-separated) to assign to the proposal: ").split(',')
        reviewer_ids = [int(reviewer_id.strip()) for reviewer_id in reviewer_ids]

        # Assign reviewers to review the proposal
        for reviewer_id in reviewer_ids:
            query = "INSERT INTO ReviewerAssignment (proposalID, reviewerID) VALUES (?, ?)"
            cur.execute(query, (id, reviewer_id))
        print("Reviewers assigned successfully.")
    else:
        print("No eligible reviewers found for the specified proposal.")

        

def find_proposals_for_reviewer(cur):


    first = input("Enter reviewer first name:").strip()
    last = input("Enter reviewer last name:").strip()
    query = """
    SELECT GrantProposal.proposalID
    FROM GrantProposal
    JOIN ReviewerAssignment ON GrantProposal.proposalID = ReviewerAssignment.proposalID
    JOIN Reviewer ON ReviewerAssignment.reviewerID = Reviewer.reviewerID
    WHERE Reviewer.firstName = ? AND Reviewer.lastName = ?
    """
    cur.execute(query, (first, last))
    proposals = cur.fetchall()
    if proposals:
        print("Proposals that "+ first + " " + last + " needs to review are: ")
        for proposal in proposals:
            print(proposal[0])
    else:
        print("There are no proposals under " + first + " " + last)
        

        
        
    

def install(package):    
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade","pip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
def main():
    conn = sqlite3.connect('grantdatabase.db')
    cur = conn.cursor()
    6
    while True:
        print("Grant Database Management System")
        print("1. Find open competitions with large proposals at a specific month")
        print("2. find the proposal(s) that request(s) the largest amount of money for a specified area")
        print("3. find the proposal(s) that")
        print("4. Enter area to find discrepnacy.")
        print("5. Test")
        print("6. Find proposoal under entered name")
        print("7. exit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            find_open_competitions(cur)
        elif choice == '2':
            find_largest_amount(cur)
        elif choice == '3':
            find_awarded_before_date(cur)
        elif choice == '4':
            calculate_discrepancy(cur)
        elif choice == '5':
            list_reviewers_not_in_conflict(cur)
        elif choice == '6':
            find_proposals_for_reviewer(cur)
        elif choice == '7':
            print("Exiting the program.")
            break    
        else:
            print("Invalid choice, please try again.")


    if conn:
        conn.close()

main()
   