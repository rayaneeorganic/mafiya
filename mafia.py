import random
import os
def ab():
    os.system("cls")
    while True:
    
        mafianbr=int(input("enter the number of mafia :"))
        playernbr=int(input(f"enter the number of player without the host (number>={mafianbr+3}):"))

        if playernbr < mafianbr+3:
            print(f"the number of player < {mafianbr + 3}")
            continue

        playerlist=["mafia"]*mafianbr + ["doctor-tabib"] + ["maior-9awad"] + ["Good citizen"]*(playernbr-2-mafianbr)
        print("the players : ",playerlist)
        input("pass entre to continue...")
        i=0
        n=0
        j=playernbr
        while j>0:
            os.system("cls")
            j-=1
            n+=1
            i=random.randint(0,j)

            print(f"player {n}:")
            input("pass entre to know what's your role...")
            print(f"your role is {playerlist[i]}")
            input("pass entre to continue...")
            playerlist.pop(i)
    

        print("fin ,have fan")
        q=input("pass q to quit ")

        if q=="q" or q=="Q":
            print("bey...")
            break
        os.system("cls")

ab()