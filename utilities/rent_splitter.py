rent =int (input("enter your hostel rent="))
food=int(input("enter the amount of food ordered="))
electricity=int(input("enter the electricity bill="))
persons =int (input("enter the number of persons sharing the rent="))
total_bill=rent+food+electricity
bill_per_person=total_bill/persons
print("the total bill is=",total_bill)
print("the bill per person is=",bill_per_person)