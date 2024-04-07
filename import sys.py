import sys
import subprocess

import sqlite3


def find_open_competitions(cur):

    userspecmonth = input("Enter the user-specified month (MM): ").strip()

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
        print(
            "No competitions found for the specified month with at least one large proposal.\n"
        )


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
            print(
                f"Proposal ID: {proposal[0]}, Requested Amount: ${proposal[1]:,.2f}, Area: {proposal[2]}"
            )
    else:
        print(
            f"No proposals found for the area '{userspecarea}' with the largest request amount.\n"
        )


def find_awarded_before_date(cur):
    user_specified_date = input(
        "Please enter the date (YYYY-MM-DD) to search for proposals submitted before: "
    ).strip()

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
        print(
            f"Proposal(s) submitted before {user_specified_date} with the largest rewarded amount:"
        )
        for proposal in proposals:
            print(f"Proposal ID: {proposal[0]}, Rewarded Amount: ${proposal[1]:,.2f}")
    else:
        print(
            f"No proposals found submitted before {user_specified_date} with the largest rewarded amount.\n"
        )


def calculate_discrepancy(cur):

    area = input("Enter the area you would like the discrepancy for: ")

    query = """
    SELECT AVG(ABS(requestedAmount - rewardedAmount)) AS avg_discrepancy
    FROM GrantProposal
    JOIN GrantCompetition ON GrantCompetition.competitionID = GrantProposal.competitionID
    WHERE GrantCompetition.area = ?
    """
    cur.execute(query, (area,))
    result = cur.fetchone()

    if result[0] is not None:
        print(
            "The average requested /awaraded discrepnacy for the area " + area + " is :"
        )
        print(result[0])
    else:
        print("No data available for area " + area)


def list_reviewers_not_in_conflict(cur):
    id = int(input("Enter proposal ID: "))

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

    cur.execute(query, (id,))
    eligible_reviewers = cur.fetchall()

    if eligible_reviewers:
        print("Eligible Reviewers:")
        for reviewer in eligible_reviewers:
            print(f"{reviewer[0]} - {reviewer[1]} {reviewer[2]}")

        reviewer_ids = input(
            "Enter reviewer IDs (comma-separated) to assign to the proposal: "
        ).split(",")
        reviewer_ids = [int(reviewer_id.strip()) for reviewer_id in reviewer_ids]

        for reviewer_id in reviewer_ids:
            query = (
                "INSERT INTO ReviewerAssignment (proposalID, reviewerID) VALUES (?, ?)"
            )
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
        print("Proposals that " + first + " " + last + " needs to review are: ")
        for proposal in proposals:
            print(proposal[0])
    else:
        print("There are no proposals under " + first + " " + last)


def main():
    conn = sqlite3.connect("grantdatabase.db")
    cur = conn.cursor()

    while True:
        print("Grant Database Management System")
        print("1. Find open competitions with large proposals at a specific month")
        print(
            "2. find the proposal(s) that request(s) the largest amount of money for a specified area"
        )
        print("3. find the proposals submitted before that date that are awarded the largest amount of money
        print("4. Enter area to find discrepnacy.")
        print("5. Reviewer assignment")
        print("6. Find proposoal under entered name")
        print("7. exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            find_open_competitions(cur)
        elif choice == "2":
            find_largest_amount(cur)
        elif choice == "3":
            find_awarded_before_date(cur)
        elif choice == "4":
            calculate_discrepancy(cur)
        elif choice == "5":
            list_reviewers_not_in_conflict(cur)
        elif choice == "6":
            find_proposals_for_reviewer(cur)
        elif choice == "7":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice, please try again.")

    if conn:
        conn.close()


main()
