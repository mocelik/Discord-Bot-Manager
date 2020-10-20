import time

print("I am going to sleep for a long time...")
time.sleep(10)
for i in range(100):
    print("I just woke up... Going back to sleep")
    time.sleep(10)

print("That's enough sleep, I'm going to get up now.")