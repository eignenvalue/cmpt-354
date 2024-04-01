import sys
from consolemenu import *
from consolemenu.items import *
import subprocess



##functions do not work currently except for exit 
def find_open_competitions():
    pu = PromptUtils(Screen())
    # PromptUtils.input() returns an InputResult
    result = pu.input("Enter an input")
    
    print(result)


def find_largest_amount(area):
    print(area)


def find_awarded_before_date(date):
    print(date)


def calculate_discrepancy(area):
    print(area)


def list_reviewers_not_in_conflict(proposal_id):
    print(proposal_id)


def find_proposals_for_reviewer(reviewer_name):
    print(reviewer_name)


def install(package):    
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade","pip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        
def main():
    # Create the root menu
    menu = ConsoleMenu("Welcome to the grant database", "Please enter the option you would like to choose")

    find_open_competitionsitem =FunctionItem("Find open competitions with large proposals at a specific month",find_open_competitions)
    find_largest_amountitem= FunctionItem("Find proposal with the largest amount of money requested in a specific area",find_largest_amount)
    find_awarded_before_dateitem = FunctionItem("Find awarded proposal with the largest amount of money submitted before a specific date",find_awarded_before_date)
    calculate_discrepancyitem = FunctionItem("Calculate average requested/awarded discrepancy for a specific area",calculate_discrepancy)
    list_reviewers_not_in_conflictitem = FunctionItem("List reviewers not in conflict for a proposal",list_reviewers_not_in_conflict)
    find_proposals_for_revieweritem =FunctionItem("Find proposals to review for a specific reviewer",find_proposals_for_reviewer)
    
    #create menu items
    menu.append_item(find_open_competitionsitem)
    menu.append_item(find_largest_amountitem)
    menu.append_item(find_awarded_before_dateitem)
    menu.append_item(calculate_discrepancyitem)
    menu.append_item(list_reviewers_not_in_conflictitem)
    menu.append_item(find_proposals_for_revieweritem)
    
    # Show the menu
    menu.start()
    menu.join()

if __name__ == "__main__":
    install("console-menu")
    main()
    