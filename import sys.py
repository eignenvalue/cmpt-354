import sys
import subprocess

import sqlite3


##functions do not work currently except for exit 
def find_open_competitions(cur):
    
    # PromptUtils.input() returns an InputResult
    userspecmonth = input("Enter the user-specified month (MM): ").strip()

        
    # Define the SQL query
    myQuery = """
   SELECT DISTINCT gc.competitionID, gc.title
FROM GrantCompetition gc
JOIN GrantProposal gp ON gc.competitionID = gp.competitionID
LEFT JOIN (
    SELECT proposalID, COUNT(researcherID) AS participantCount 
    FROM Collaborators 
    GROUP BY proposalID
) c ON gp.proposalID = c.proposalID
WHERE gc.status = 'open'
AND strftime('%m', gc.applicationDeadline) = :userSpecifiedMonth
AND (gp.requestedAmount > 20000 OR IFNULL(c.participantCount, 0) + 1 > 10);

    """
    
    cur.execute(myQuery, {"userSpecifiedMonth": userspecmonth})
    
    competitions = cur.fetchall()
    
    if competitions:
        for competition in competitions:   
            print(f"Competition ID: {competition[0]}, Title: {competition[1]}")
    else:
         print("No competitions found for the specified month with at least one large proposal.\n")
         
    
              
   
    
    
def find_largest_amount(cur):
    userspecarea = input("please enter area of interest: ").strip()
    
    sql_query = """
    SELECT gp.proposalID, gp.requestedAmount, gc.area
    FROM GrantProposal gp
    JOIN GrantCompetition gc ON gp.competitionID = gc.competitionID
    WHERE gc.area = :user_specified_area
    AND gp.requestedAmount = (
        SELECT MAX(requestedAmount)
        FROM GrantProposal innerGP
        JOIN GrantCompetition innerGC ON innerGP.competitionID = innerGC.competitionID
        WHERE innerGC.area = :user_specified_area
    );
    """
    cur.execute(sql_query, {"user_specified_area": userspecarea})
    
    proposals = cur.fetchall()

   
    if proposals:
        for proposal in proposals:
            print(f"Proposal ID: {proposal[0]}, Requested Amount: ${proposal[1]:,.2f}, Area: {proposal[2]}")
    else:
        print(f"No proposals found for the area '{userspecarea}' with the largest request amount.\n")
    


def find_awarded_before_date(cur):
    user_specified_date = input("Please enter the date (YYYY-MM-DD) to search for proposals submitted before: ").strip()
    
    sql_query = """
    SELECT gp.proposalID, gp.rewardedAmount
    FROM GrantProposal gp
    JOIN GrantCompetition gc ON gp.competitionID = gc.competitionID
    WHERE gc.creationdate < :user_specified_date
    AND gp.rewardedAmount > 0
    AND gp.rewardedAmount = (
        SELECT MAX(gpInner.rewardedAmount)
        FROM GrantProposal gpInner
        JOIN GrantCompetition gcInner ON gpInner.competitionID = gcInner.competitionID
        WHERE gcInner.creationdate < :user_specified_date
        AND gpInner.rewardedAmount > 0
    );
    """
    cur.execute(sql_query, {"user_specified_date": user_specified_date})
    
    proposals = cur.fetchall()
    
    if proposals:
        print(f"Proposal(s) submitted before {user_specified_date} with the largest rewarded amount:")
        for proposal in proposals:
            print(f"Proposal ID: {proposal[0]}, Rewarded Amount: ${proposal[1]:,.2f}")
    else:
        print(f"No proposals found submitted before {user_specified_date} with the largest rewarded amount.\n")


def calculate_discrepancy(area):
    print(area)


def list_reviewers_not_in_conflict(proposal_id):
    print(proposal_id)


def find_proposals_for_reviewer(reviewer_name):
    print(reviewer_name)

        
def main():
    conn = sqlite3.connect('grantdatabase.db')
    cur = conn.cursor()
    
    while True:
        print("Grant Database Management System")
        print("1. Find open competitions with large proposals at a specific month")
        print("2. find the proposal(s) that request(s) the largest amount of money for a specified area")
        print("3. For a user-specified date,  find the proposals submitted before that date that are awarded the largest amount of money")
        print("7. exit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            find_open_competitions(cur)
        elif choice == '2':
            find_largest_amount(cur)
        elif choice == "3":
            find_awarded_before_date(cur)
        elif choice == '7':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice, please try again.")


    if conn:
        conn.close()

main()
    