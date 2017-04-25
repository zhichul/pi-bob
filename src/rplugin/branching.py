# Right -> Left (9) -> Straight -> Straight (10) -> Right (11) -> Straight -> Straight (12) -> Left (13) -> Straight -> Straight (14) 
L = 0
S = 1
R = 2
DETECT_THRESHOLD = 1
COOLING = 2
detect_count = 0
cooling = 0
curr_decision = None
branch_decisions = [S,S,L,S,S,R,S,S,L,R]
if detect_branch:
    if detect_count < DETECT_THRESHOLD:
        detect_count += 1
    else:
        curr_decision = branch_decisions.pop()
        cooling += 1
        do_action(curr_decision) # to be changed
        if cooling == COOLING:
            detect_count = 0
            cooling = 0
            curr_decision = None
else:
    detect_count = 0
    cooling = 0
    curr_decision = None