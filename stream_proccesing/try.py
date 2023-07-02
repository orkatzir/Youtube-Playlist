from prefect import flow
# import os

@flow(name="test")
def ma():
    print("hiiiiiii")
if __name__ == '__main__':    
 ma()