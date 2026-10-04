import random
"""
input computer choice randomly user choice 
logic cases rock-rock tie rock paper paper win ,rock scissor rock win,paper paper tie,
paper rock paper win, paper scissor scissor win,scissor scissor tie,scissor rock rock win,scissor paper scissor win
"""
##list datatype syntax
choices=["rock","paper","scissor"]
user_choice=input("enter your choice rock paper scissor=")
computer_choice=random.choice(choices)
print(f"user choice={user_choice},computer choice={computer_choice }")
if user_choice==computer_choice:
    print("tie")
elif user_choice=="rock" and computer_choice=="paper":
    print("computer win")
elif user_choice=="rock" and computer_choice=="scissor":
    print("user win")
elif user_choice=="paper" and computer_choice=="rock":
    print("user win")
elif user_choice=="paper" and computer_choice=="scissor":
    print("computer win")
elif user_choice=="scissor" and computer_choice=="rock":
    print("computer win")
elif user_choice=="scissor" and computer_choice=="paper":
    print("user win")   
    

