import random
import sys
import copy
import time
import tensorflow as tf
import numpy as np

#Knowledge = []
#OpTafel = []
#TrashNumber = 0
#PlayedNumber = 0

#NietHetzelfde = 0

GREEN = 0
YELLOW = 1
WHITE = 2
BLUE = 3
RED = 4
ALL_COLORS = [GREEN, YELLOW, WHITE, BLUE, RED]
COLORNAMES = ["green", "yellow", "white", "blue", "red"]

COUNTS = [3,2,2,2,1]

HANABIMODEL = tf.keras.models.load_model('HanabiModelMaximaalBeste.h5')

# semi-intelligently format cards in any format
def f(something):
    if type(something) == list:
        return map(f, something)
    elif type(something) == dict:
        return {k: something(v) for (k,v) in something.iteritems()}
    elif type(something) == tuple and len(something) == 2:
        return (COLORNAMES[something[0]],something[1])
    return something

def make_deck():
    #print("ik maak een deck")
    deck = []
    for col in ALL_COLORS:
        for num, cnt in enumerate(COUNTS):
            for i in xrange(cnt):
                deck.append((col, num+1))
    random.shuffle(deck)
    #print(deck)
    return deck
    
def initial_knowledge():
    knowledge = []
    for col in ALL_COLORS:
        knowledge.append(COUNTS[:])
    return knowledge
    
def hint_color(knowledge, color, truth):
    result = []
    for col in ALL_COLORS:
        if truth == (col == color):
            result.append(knowledge[col][:])
        else:
            result.append([0 for i in knowledge[col]])
    return result
    
def hint_rank(knowledge, rank, truth):
    result = []
    for col in ALL_COLORS:
        colknow = []
        for i,k in enumerate(knowledge[col]):
            if truth == (i + 1 == rank):
                colknow.append(k)
            else:
                colknow.append(0)
        result.append(colknow)
    return result
    
def iscard((c,n)):
    knowledge = []
    for col in ALL_COLORS:
        knowledge.append(COUNTS[:])
        for i in xrange(len(knowledge[-1])):
            if col != c or i+1 != n:
                knowledge[-1][i] = 0
            else:
                knowledge[-1][i] = 1
            
    return knowledge
    
HINT_COLOR = 0
HINT_NUMBER = 1
PLAY = 2
DISCARD = 3
    
class Action(object):
    def __init__(self, type, pnr=None, col=None, num=None, cnr=None):
        self.type = type
        self.pnr = pnr
        self.col = col
        self.num = num
        self.cnr = cnr
    def __str__(self):
        if self.type == HINT_COLOR:
            return "hints " + str(self.pnr) + " about all their " + COLORNAMES[self.col] + " cards"
        if self.type == HINT_NUMBER:
            return "hints " + str(self.pnr) + " about all their " + str(self.num)
        if self.type == PLAY:
            return "plays their " + str(self.cnr)
        if self.type == DISCARD:
            return "discards their " + str(self.cnr)
    def __eq__(self, other):
        return (self.type, self.pnr, self.col, self.num, self.cnr) == (other.type, other.pnr, other.col, other.num, other.cnr)
        
class Player(object):
    def __init__(self, name, pnr):
        self.name = name
        self.explanation = []
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        return random.choice(valid_actions)
    def inform(self, action, player, game):
        pass
    def get_explanation(self):
        return self.explanation
        
def get_possible(knowledge):
    result = []
    for col in ALL_COLORS:
        for i,cnt in enumerate(knowledge[col]):
            if cnt > 0:
                result.append((col,i+1))
    return result
    
def playable(possible, board):
    for (col,nr) in possible:
        if board[col][1] + 1 != nr:
            return False
    return True
    
def potentially_playable(possible, board):
    for (col,nr) in possible:
        if board[col][1] + 1 == nr:
            return True
    return False
    
def discardable(possible, board):
    for (col,nr) in possible:
        if board[col][1] < nr:
            return False
    return True
    
def potentially_discardable(possible, board):
    for (col,nr) in possible:
        if board[col][1] >= nr:
            return True
    return False
    
def update_knowledge(knowledge, used):
    result = copy.deepcopy(knowledge)
    for r in result:
        for (c,nr) in used:
            r[c][nr-1] = max(r[c][nr-1] - used[c,nr], 0)
    return result

        
class InnerStatePlayer(Player):
    def __init__(self, name, pnr):
        self.name = name
        self.explanation = []
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        handsize = len(knowledge[0])
        possible = []
        for k in knowledge[nr]:
            possible.append(get_possible(k))
        
        discards = []
        duplicates = []
        for i,p in enumerate(possible):
            if playable(p,board):
                return Action(PLAY, cnr=i)
            if discardable(p,board):
                discards.append(i)

        if discards:
            return Action(DISCARD, cnr=random.choice(discards))
            
        playables = []
        for i,h in enumerate(hands):
            if i != nr:
                for j,(col,n) in enumerate(h):
                    if board[col][1] + 1 == n:
                        playables.append((i,j))
        
        if playables and hints > 0:
            i,j = playables[0]
            if random.random() < 0.5:
                return Action(HINT_COLOR, pnr=i, col=hands[i][j][0])
            return Action(HINT_NUMBER, pnr=i, num=hands[i][j][1])
        
        
        for i, k in enumerate(knowledge):
            if i == nr:
                continue
            cards = range(len(k))
            random.shuffle(cards)
            c = cards[0]
            (col,num) = hands[i][c]            
            hinttype = [HINT_COLOR, HINT_NUMBER]
            if hinttype and hints > 0:
                if random.choice(hinttype) == HINT_COLOR:
                    return Action(HINT_COLOR, pnr=i, col=col)
                else:
                    return Action(HINT_NUMBER, pnr=i, num=num)
        
        prefer = []
        for v in valid_actions:
            if v.type in [HINT_COLOR, HINT_NUMBER]:
                prefer.append(v)
        prefer = []
        if prefer and hints > 0:
            return random.choice(prefer)
        return random.choice([Action(DISCARD, cnr=i) for i in xrange(len(knowledge[0]))])
    def inform(self, action, player, game):
        pass
        
class OuterStatePlayer(Player):
    def __init__(self, name, pnr):
        self.name = name
        self.hints = {}
        self.pnr = pnr
        self.explanation = []
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        handsize = len(knowledge[0])
        possible = []
        for k in knowledge[nr]:
            possible.append(get_possible(k))
        
        discards = []
        duplicates = []
        for i,p in enumerate(possible):
            if playable(p,board):
                return Action(PLAY, cnr=i)
            if discardable(p,board):
                discards.append(i)

        if discards:
            return Action(DISCARD, cnr=random.choice(discards))
            
        playables = []
        for i,h in enumerate(hands):
            if i != nr:
                for j,(col,n) in enumerate(h):
                    if board[col][1] + 1 == n:
                        playables.append((i,j))
        playables.sort(key=lambda (i,j): -hands[i][j][1])
        while playables and hints > 0:
            i,j = playables[0]
            knows_rank = True
            real_color = hands[i][j][0]
            real_rank = hands[i][j][0]
            k = knowledge[i][j]
            
            hinttype = [HINT_COLOR, HINT_NUMBER]
            if (j,i) not in self.hints:
                self.hints[(j,i)] = []
            
            for h in self.hints[(j,i)]:
                hinttype.remove(h)
            
            t = None
            if hinttype:
                t = random.choice(hinttype)
            
            if t == HINT_NUMBER:
                self.hints[(j,i)].append(HINT_NUMBER)
                return Action(HINT_NUMBER, pnr=i, num=hands[i][j][1])
            if t == HINT_COLOR:
                self.hints[(j,i)].append(HINT_COLOR)
                return Action(HINT_COLOR, pnr=i, col=hands[i][j][0])
            
            playables = playables[1:]
        
        for i, k in enumerate(knowledge):
            if i == nr:
                continue
            cards = range(len(k))
            random.shuffle(cards)
            c = cards[0]
            (col,num) = hands[i][c]            
            hinttype = [HINT_COLOR, HINT_NUMBER]
            if (c,i) not in self.hints:
                self.hints[(c,i)] = []
            for h in self.hints[(c,i)]:
                hinttype.remove(h)
            if hinttype and hints > 0:
                if random.choice(hinttype) == HINT_COLOR:
                    self.hints[(c,i)].append(HINT_COLOR)
                    return Action(HINT_COLOR, pnr=i, col=col)
                else:
                    self.hints[(c,i)].append(HINT_NUMBER)
                    return Action(HINT_NUMBER, pnr=i, num=num)

        return random.choice([Action(DISCARD, cnr=i) for i in xrange(handsize)])
    def inform(self, action, player, game):
        if action.type in [PLAY, DISCARD]:
            x = str(action)
            if (action.cnr,player) in self.hints:
                self.hints[(action.cnr,player)] = []
            for i in xrange(10):
                if (action.cnr+i+1,player) in self.hints:
                    self.hints[(action.cnr+i,player)] = self.hints[(action.cnr+i+1,player)]
                    self.hints[(action.cnr+i+1,player)] = []

                    
def generate_hands(knowledge, used={}):
    if len(knowledge) == 0:
        yield []
        return
    
    
    
    for other in generate_hands(knowledge[1:], used):
        for col in ALL_COLORS:
            for i,cnt in enumerate(knowledge[0][col]):
                if cnt > 0:
                    
                    result = [(col,i+1)] + other
                    ok = True
                    thishand = {}
                    for (c,n) in result:
                        if (c,n) not in thishand:
                            thishand[(c,n)] = 0
                        thishand[(c,n)] += 1
                    for (c,n) in thishand:
                        if used[(c,n)] + thishand[(c,n)] > COUNTS[n-1]:
                           ok = False
                    if ok:
                        yield  result

def generate_hands_simple(knowledge, used={}):
    if len(knowledge) == 0:
        yield []
        return
    for other in generate_hands_simple(knowledge[1:]):
        for col in ALL_COLORS:
            for i,cnt in enumerate(knowledge[0][col]):
                if cnt > 0:
                    yield [(col,i+1)] + other



                    
a = 1   

class SelfRecognitionPlayer(Player):
    def __init__(self, name, pnr, other=OuterStatePlayer):
        self.name = name
        self.hints = {}
        self.pnr = pnr
        self.gothint = None
        self.last_knowledge = []
        self.last_played = []
        self.last_board = []
        self.other = other
        self.explanation = []
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        handsize = len(knowledge[0])
        possible = []
        
        if self.gothint:
            
            possiblehands = []
            wrong = 0
            used = {}
            for c in ALL_COLORS:
                for i,cnt in enumerate(COUNTS):
                    used[(c,i+1)] = 0
            for c in trash + played:
                used[c] += 1
            
            for h in generate_hands_simple(knowledge[nr], used):
                newhands = hands[:]
                newhands[nr] = h
                other = self.other("Pinocchio", self.gothint[1])
                act = other.get_action(self.gothint[1], newhands, self.last_knowledge, self.last_trash, self.last_played, self.last_board, valid_actions, hints + 1)
                lastact = self.gothint[0]
                if act == lastact:
                    possiblehands.append(h)
                    def do(c,i):
                        newhands = hands[:]
                        h1 = h[:]
                        h1[i] = c
                        newhands[nr] = h1
                        print other.get_action(self.gothint[1], newhands, self.last_knowledge, self.last_trash, self.last_played, self.last_board, valid_actions, hints + 1)
                    #import pdb
                    #pdb.set_trace()
                else:
                    wrong += 1
            #print len(possiblehands), "would have led to", self.gothint[0], "and not:", wrong
            #print f(possiblehands)
            if possiblehands:
                mostlikely = [(0,0) for i in xrange(len(possiblehands[0]))]
                for i in xrange(len(possiblehands[0])):
                    counts = {}
                    for h in possiblehands:
                        if h[i] not in counts:
                            counts[h[i]] = 0
                        counts[h[i]] += 1
                    for c in counts:
                        if counts[c] > mostlikely[i][1]:
                            mostlikely[i] = (c,counts[c])
                #print "most likely:", mostlikely
                m = max(mostlikely, key=lambda (card,cnt): cnt)
                second = mostlikely[:]
                second.remove(m)
                m2 = max(second, key=lambda (card,cnt): cnt)
                if m[1] >= m2[1]*a:
                    #print ">>>>>>> deduced!", f(m[0]), m[1],"vs", f(m2[0]), m2[1]
                    knowledge = copy.deepcopy(knowledge)
                    knowledge[nr][mostlikely.index(m)] = iscard(m[0])

        
        self.gothint = None
        for k in knowledge[nr]:
            possible.append(get_possible(k))
        
        discards = []
        duplicates = []
        for i,p in enumerate(possible):
            if playable(p,board):
                return Action(PLAY, cnr=i)
            if discardable(p,board):
                discards.append(i)

        if discards:
            return Action(DISCARD, cnr=random.choice(discards))
            
        playables = []
        for i,h in enumerate(hands):
            if i != nr:
                for j,(col,n) in enumerate(h):
                    if board[col][1] + 1 == n:
                        playables.append((i,j))
        playables.sort(key=lambda (i,j): -hands[i][j][1])
        while playables and hints > 0:
            i,j = playables[0]
            knows_rank = True
            real_color = hands[i][j][0]
            real_rank = hands[i][j][0]
            k = knowledge[i][j]
            
            hinttype = [HINT_COLOR, HINT_NUMBER]
            if (j,i) not in self.hints:
                self.hints[(j,i)] = []
            
            for h in self.hints[(j,i)]:
                hinttype.remove(h)
            
            if HINT_NUMBER in hinttype:
                self.hints[(j,i)].append(HINT_NUMBER)
                return Action(HINT_NUMBER, pnr=i, num=hands[i][j][1])
            if HINT_COLOR in hinttype:
                self.hints[(j,i)].append(HINT_COLOR)
                return Action(HINT_COLOR, pnr=i, col=hands[i][j][0])
            
            playables = playables[1:]
        
        for i, k in enumerate(knowledge):
            if i == nr:
                continue
            cards = range(len(k))
            random.shuffle(cards)
            c = cards[0]
            (col,num) = hands[i][c]            
            hinttype = [HINT_COLOR, HINT_NUMBER]
            if (c,i) not in self.hints:
                self.hints[(c,i)] = []
            for h in self.hints[(c,i)]:
                hinttype.remove(h)
            if hinttype and hints > 0:
                if random.choice(hinttype) == HINT_COLOR:
                    self.hints[(c,i)].append(HINT_COLOR)
                    return Action(HINT_COLOR, pnr=i, col=col)
                else:
                    self.hints[(c,i)].append(HINT_NUMBER)
                    return Action(HINT_NUMBER, pnr=i, num=num)

        return random.choice([Action(DISCARD, cnr=i) for i in xrange(handsize)])
    def inform(self, action, player, game):
        if action.type in [PLAY, DISCARD]:
            x = str(action)
            if (action.cnr,player) in self.hints:
                self.hints[(action.cnr,player)] = []
            for i in xrange(10):
                if (action.cnr+i+1,player) in self.hints:
                    self.hints[(action.cnr+i,player)] = self.hints[(action.cnr+i+1,player)]
                    self.hints[(action.cnr+i+1,player)] = []
        elif action.pnr == self.pnr:
            self.gothint = (action,player)
            self.last_knowledge = game.knowledge[:]
            self.last_board = game.board[:]
            self.last_trash = game.trash[:]
            self.played = game.played[:]
            
TIMESCALE = 40.0/1000.0 # ms
SLICETIME = TIMESCALE / 10.0
APPROXTIME = SLICETIME/8.0

def priorities(c, board):
    (col,val) = c
    if board[col][1] == val-1:
        return val - 1
    if board[col][1] >= val:
        return 5
    if val == 5:
        return 15
    return 6 + (4 - val)
    


SENT = 0
ERRORS = 0
COUNT = 0

CAREFUL = True
        
class TimedPlayer(object):
    def __init__(self, name, pnr):
        self.name = name
        self.explanation = []
        self.last_tick = time.time()
        self.pnr = pnr
        self.last_played = False
        self.tt = time.time()
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        global SENT, ERRORS, COUNT
        tick = time.time()
        duration = round((tick - self.last_tick)/SLICETIME)
        other = (self.pnr + 1)% len(hands)
        #print(self.pnr, "got", duration)
        if duration >= 10:
            duration = 9
        if duration != SENT:
            ERRORS += 1
            #print("mismatch", nr, f(hands), f(board), duration, SENT)
        COUNT += 1
        other_hand = hands[other][:]
        def prio(c):
            return priorities(c,board)
        other_hand.sort(key=prio)
        #print(f(other_hand), f(board), list(map(prio, other_hand)), f(hands))
        p = prio(other_hand[0])
        delta = 0.0
        if p >= 5:
            delta += 5
        #print("idx", hands[other].index(other_hand[0]))
        def fix(n):
            if n >= len(other_hand):
               return len(other_hand) - 1
            return int(round(n))
        delta += hands[other].index(other_hand[0])
        if duration >= 5:
            action = Action(DISCARD, cnr=fix(duration-5))
        else:
            action = Action(PLAY, cnr=fix(duration))
        if self.last_played and hints > 0 and CAREFUL:
            action = Action(HINT_COLOR, pnr=other, col=other_hand[0][0])
        t1 = time.time()
        SENT = delta
        #print(self.pnr, "convey", round(delta))
        delta -= 0.5
        while (t1 - tick) < delta*SLICETIME:
            time.sleep(APPROXTIME)
            t1 = time.time()
        self.last_tick = time.time()
        return action
    def inform(self, action, player, game):
        self.last_played = (action.type == PLAY)
        self.last_tick = self.tt
        self.tt = time.time()
        #print(action, player)
    def get_explanation(self):
        return self.explanation
            
            
CANDISCARD = 128

def format_intention(i):
    if isinstance(i, str):
        return i
    if i == PLAY:
        return "Play"
    elif i == DISCARD:
        return "Discard"
    elif i == CANDISCARD:
        return "Can Discard"
    return "Keep"

###decide what the player is gonna do, following Gryce's maxims
### if that card is potentially playable, the player will play that card if he gets a hint about it
### if that card is potentially discardable and not pot. playable, the playerwill discard the card
### if both not, return None
def whattodo(knowledge, pointed, board):
    possible = get_possible(knowledge)
    play = potentially_playable(possible, board)
    discard = potentially_discardable(possible, board)
    
    if play and pointed:
        return PLAY
    if discard and pointed:
        return DISCARD
    return None

def pretend(action, knowledge, intentions, hand, board):
    ###action = Hint_color, color or Hint_rank, rank
    (type,value) = action
    #print("intentional Hint = ", action)
    
    positive = []
    haspositive = False
    change = False
    
    ###for each type of hint, change knowledge accordinly for each color or rank
    ###positive is list with True or False wether the value is the same as the color that is being simulated
    ###newknowledge is list of knowledgestructures for all possible hints
    ###has postive is True if color = value
    ###Change is False if newknowledge is not different
    
    if type == HINT_COLOR:
        newknowledge = []
        for i,(col,num) in enumerate(hand):
            positive.append(value==col)
            newknowledge.append(hint_color(knowledge[i], value, value == col))
            if value == col:
                haspositive = True
                if newknowledge[-1] != knowledge[i]:
                    change = True
    else:
        newknowledge = []
        for i,(col,num) in enumerate(hand):
            positive.append(value==num)
            
            newknowledge.append(hint_rank(knowledge[i], value, value == num))
            if value == num:
                haspositive = True
                if newknowledge[-1] != knowledge[i]:
                    change = True
    ##hints are not valid if the value was different then the color or if the hint doesnt add knowledge
    if not haspositive:
        return False, 0, ["Invalid hint"]
    if not change:
        return False, 0, ["No new information"]
    
    ###If the Hint can doesnt match intentions return Invalid,
    ###If it does match, give the hint score
    score = 0
    predictions = []
    pos = False
    for i,c,k,p in zip(intentions, hand, newknowledge, positive):
        
        #print("intentional new knowledge", k)
        action = whattodo(k, p, board)
        
        if action == PLAY and i != PLAY:
            #print "would cause them to play", f(c)
            return False, 0, predictions + [PLAY]
        
        if action == DISCARD and i not in [DISCARD, CANDISCARD]:
            #print "would cause them to discard", f(c)
            return False, 0, predictions + [DISCARD]
            
        if action == PLAY and i == PLAY:
            pos = True
            predictions.append(PLAY)
            score += 3
        elif action == DISCARD and i in [DISCARD, CANDISCARD]:
            pos = True
            predictions.append(DISCARD)
            if i == DISCARD:
                score += 2
            else:
                score += 1
        else:
            predictions.append(None)
    if not pos:
        return False, score, predictions
    return True,score, predictions
    
HINT_VALUE = 0.5
    
def pretend_discard(act, knowledge, board, trash):
    which = copy.deepcopy(knowledge[act.cnr])
    for (col,num) in trash:
        if which[col][num-1]:
            which[col][num-1] -= 1
    for col in ALL_COLORS:
        for i in xrange(board[col][1]):
            if which[col][i]:
                which[col][i] -= 1
    possibilities = sum(map(sum, which))
    expected = 0
    terms = []
    for col in ALL_COLORS:
        for i,cnt in enumerate(which[col]):
            rank = i+1
            if cnt > 0:
                prob = cnt*1.0/possibilities
                if board[col][1] >= rank:
                    expected += prob*HINT_VALUE
                    terms.append((col,rank,cnt,prob,prob*HINT_VALUE))
                else:
                    dist = rank - board[col][1]
                    if cnt > 1:
                        value = prob*(6-rank)/(dist*dist)
                    else:
                        value = (6-rank)
                    if rank == 5:
                        value += HINT_VALUE
                    value *= prob
                    expected -= value
                    terms.append((col,rank,cnt,prob,-value))
    return (act, expected, terms)

def format_knowledge(k):
    result = ""
    for col in ALL_COLORS:
        for i,cnt in enumerate(k[col]):
            if cnt > 0:
                result += COLORNAMES[col] + " " + str(i+1) + ": " + str(cnt) + "\n"
    return result



class IntentionalPlayer(Player):
    def __init__(self, name, pnr):
        self.name = name
        self.hints = {}
        self.pnr = pnr
        self.gothint = None
        self.last_knowledge = []
        self.last_played = []
        self.last_board = []
        self.explanation = []
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        print("self: ", self)
        print("nr: ", nr)
        print("hands: ", hands)
        print("knowledge: ", knowledge)
        print("trash: ", trash)
        print("played: ", played)
        print("board: ", board)
        print("vaild_actions: ", valid_actions)
        print("hints: ", hints)
        handsize = len(knowledge[0])
        possible = []
        result = None
        self.explanation = []
        self.explanation.append(["Your Hand:"] + map(f, hands[1-nr]))
        
        self.gothint = None
        for k in knowledge[nr]:
            possible.append(get_possible(k))
        
        discards = []
        duplicates = []
        for i,p in enumerate(possible):
            if playable(p,board):
                result = Action(PLAY, cnr=i)
            if discardable(p,board):
                discards.append(i)

        if discards and hints < 8 and not result:
            result =  Action(DISCARD, cnr=random.choice(discards))
            
        playables = []
        useless = []
        discardables = []
        othercards = trash + board
        intentions = [None for i in xrange(handsize)]
        for i,h in enumerate(hands):
            if i != nr:
                for j,(col,n) in enumerate(h):
                    if board[col][1] + 1 == n:
                        playables.append((i,j))
                        intentions[j] = PLAY
                    if board[col][1] >= n:
                        useless.append((i,j))
                        if not intentions[j]:
                            intentions[j] = DISCARD
                    if n < 5 and (col,n) not in othercards:
                        discardables.append((i,j))
                        if not intentions[j]:
                            intentions[j] = CANDISCARD
        
        self.explanation.append(["Intentions"] + map(format_intention, intentions))
        
        
            
        if hints > 0:
            valid = []
            for c in ALL_COLORS:
                action = (HINT_COLOR, c)
                #print "HINT", COLORNAMES[c],
                (isvalid,score,expl) = pretend(action, knowledge[1-nr], intentions, hands[1-nr], board)
                self.explanation.append(["Prediction for: Hint Color " + COLORNAMES[c]] + map(format_intention, expl))
                #print isvalid, score
                if isvalid:
                    valid.append((action,score))
            
            for r in xrange(5):
                r += 1
                action = (HINT_NUMBER, r)
                #print "HINT", r,
                
                (isvalid,score, expl) = pretend(action, knowledge[1-nr], intentions, hands[1-nr], board)
                self.explanation.append(["Prediction for: Hint Rank " + str(r)] + map(format_intention, expl))
                #print isvalid, score
                if isvalid:
                    valid.append((action,score))
                 
            if valid and not result:
                valid.sort(key=lambda (a,s): -s)
                #print valid
                (a,s) = valid[0]
                if a[0] == HINT_COLOR:
                    result = Action(HINT_COLOR, pnr=1-nr, col=a[1])
                else:
                    result = Action(HINT_NUMBER, pnr=1-nr, num=a[1])

        self.explanation.append(["My Knowledge"] + map(format_knowledge, knowledge[nr]))
        possible = [ Action(DISCARD, cnr=i) for i in xrange(handsize) ]
        
        scores = map(lambda p: pretend_discard(p, knowledge[nr], board, trash), possible)
        def format_term((col,rank,n,prob,val)):
            return COLORNAMES[col] + " " + str(rank) + " (%.2f%%): %.2f"%(prob*100, val)
            
        self.explanation.append(["Discard Scores"] + map(lambda (a,s,t): "\n".join(map(format_term, t)) + "\n%.2f"%(s), scores))
        scores.sort(key=lambda (a,s,t): -s)
        if result:
            return result
        return scores[0][0]
        
        return random.choice([Action(DISCARD, cnr=i) for i in xrange(handsize)])
    def inform(self, action, player, game):
        if action.type in [PLAY, DISCARD]:
            x = str(action)
            if (action.cnr,player) in self.hints:
                self.hints[(action.cnr,player)] = []
            for i in xrange(10):
                if (action.cnr+i+1,player) in self.hints:
                    self.hints[(action.cnr+i,player)] = self.hints[(action.cnr+i+1,player)]
                    self.hints[(action.cnr+i+1,player)] = []
        elif action.pnr == self.pnr:
            self.gothint = (action,player)
            self.last_knowledge = game.knowledge[:]
            self.last_board = game.board[:]
            self.last_trash = game.trash[:]
            self.played = game.played[:]

            
# Mijn eigen voorspel functie
#Krijgt als input de situatie, en roept neural netwerk aan.
#Returned de voorspelling in de vorm van een tuple,
#Het eerste element van de tuple is de actie die wordt gedaan (PLAY, DISCARD or None)
#Het tweede element is de kaart waarmee de actie wordt gedaan. 

def NEURAAL(allknowledge, newknowledge, trash, played, hints):
    
    #HANABIMODEL = tf.keras.models.load_model('HanabiModelBeter.h5')
    
    #Er wordt een library gemaakt met als keys alle kaarten die al zijn gespeeld en
    #values hoevaak die kaart al is gespeeld.
    used = {}
    for c in trash + played:
            if c not in used:
                used[c] = 0
            used[c] += 1
    
    #De library wordt omgezet in een lijst met 25 elementen,
    #Elk element representeert een kaart en het element is een getal tussen 0 en 3, dat aangeeft
    #hoeveel van die kaart er nog niet is gespeeld (lees: gespeeld of discard)
    #Deze knowledge is dus niet de representatie van wat de spelers weten, zoals de originele makers van de code het gebruiken
    #Vandaar de hoofdletter
    Knowledge = updateKnowledge(used)
    
    #Van een lijst met alle gespeelde kaarten wordt een lijst gemaakt met 25 elementen
    #Elk element staat voor een kaart en het element is een 0 of een 1, een 1 als deze kaart op tafel ligt
    #en dus eerder succesvol is gespeeld
    OpTafel = updateOpTafel(played)

    #Hier wordt de Mindstate van beide spelers samen met de nieuwe mindstate die bij de hint past gebruikt
    #om een lijst te maken met 250 elementen.
    #De eerste 125 elementen staan voor de Mindstate van de AI, de tweede 125 elementen zijn de Mindstate van de speler
    #De elementen zijn 0 en 1, 1 als er wordt gedacht dat de kaartoptie nog mogelijk is.
    Mind = MaakMindvanknowledge(allknowledge, newknowledge)
    
    ###Print voor elke kaart de mindstate
    #T_een = 0
    #T_twee = 25
    #for t in range(10):
        #print("card: ",t," Mind: ", Mind[T_een:T_twee])
        #T_een += 25
        #T_twee += 25
    
    
    #In deze code heb ik nog niet gevonden hoe ik kan bijhouden hoeveel fouten er zijn gemaakt,
    #dus Fuses is altijd 3
    Fuses = 3
    
    #Aantalkaarten is het aantal kaarten dat nog op de stapel ligt,
    #Dit is 50 - 10 (allebei handen van spelers) - alle kaarten die zijn discard - alle kaarten die zijn gespeeld
    Aantalkaarten = 40 - len(trash) - len(played)
    
    #Alle bovenstaande lijsten plus hoeveel hint tokens er nog zijn wordt in 1 lijst met 303 elementen gestopt
    
    
    
    
    
    
    Input = MaakInput(Knowledge, Mind, OpTafel, hints, Fuses, Aantalkaarten)
    
    
    if len(Input) != 303:
        print("mind", len(Mind))
        print("Op Tafel", len(OpTafel))
        print("Knowledge", len(Knowledge))
        print("trash", trash)
        print("played", played)
        
        return [(None, 0, 0)]
    
    #Deze lijst moet een numpy array zijn, zodat deze als input voor het neurale netwerk gebruikt kan worden
    INPUT = np.array([Input])
    
    
    
    
    #Hier wordt het neurale netwerk aangeroepen.
    # De uitkomst is een lijst met een lijst met 11 elementen.
    # Elk element is een kans dat een bepaalde actie wordt gedaan
    predictions = HANABIMODEL.predict(INPUT)
    
    #Bijvoorbeeld [0,0,0,0.25,0,0,0.65,0,0,1]
    #dit betekent dat er   25% kans is dat de speler kaart 4 gaat spelen
                            #65% kans is dat de speler kaart 3 gaat discarden
                            #10% kans is dat de speler een hint gaat geven
    
    
    predictions_round = []
    Predictions = []
    PotentialAction = []
    
    #Hier worden van de lijst met de lijst een lijst gemaakt 
    #en er wordt een lijst gemaakt met de kansen, maar dan afgerond
    for x in predictions:
        for p in x:
            #Predictions.append(p)
            predictions_round.append(round(p,3))
    
    print("Predictions ML:", predictions_round)
    
    #Als de kans boven de 25% is, dan wordt de actie die daarbij hoort als tuple toegevoegd aan een lijst
    #De elementen uit deze lijst worden uiteindelijk gereturned
    # 25% heb ik zelf bedacht en ik niet op literatuur gebasseerd
    for nr, pred in enumerate(predictions_round):
        if pred != 0:
            PotentialAction.append((nr, pred))
        
    #hieronder worden de potentiele acties omgezet in tuples met als eerste element de actie
    #en als tweede element de kaart
    #De tuples worden in een lijst gezet en deze lijst wordt gereturned
    
    actions = []
    for nr, pred in PotentialAction:
        if nr < 5:
            actions.append((PLAY, nr, pred))
        elif nr < 10:
            actions.append((DISCARD, nr-5, pred))
        else:
            actions.append((None, nr, pred))

    return actions
    

        
        
            
            
            
#Een Aangepaste Pretend functie
#Deze functie gaat voor een bepaalde hint na, wat er verwacht wordt dat de speler ermee zal doen
#en returned of het een goede of slechte hint is

def pretend_ML(action, knowledge, intentions, hand, board, trash, played, allknowledge, hints):
    (type,value) = action
    positive = []
    haspositive = False
    change = False
    
    #print("Hand: ", hand)
    #print("Hint: " ,type, value)
    
    
    #for each type of hint, change knowledge accordinly for each color or rank
    #positive is list with True or False wether the value is the same as the color that is being simulated
    #newknowledge is list of knowledgestructures for all possible hints
    #has postive is True if color = value, (cant give hint about color that is not in hand)
    #Change is False if newknowledge is not different (hint has to give new information)
    
    
    
    if type == HINT_COLOR:
        newknowledge = []
        for i,(col,num) in enumerate(hand):
            positive.append(value==col)
            newknowledge.append(hint_color(knowledge[i], value, value==col))
            if value == col:
                haspositive = True
                if newknowledge[-1] != knowledge[i]:
                    change = True
    else:
        newknowledge = []
        for i,(col,num) in enumerate(hand):
            positive.append(value==num)
            
            newknowledge.append(hint_rank(knowledge[i], value, value==num))
            if value == num:
                haspositive = True
                if newknowledge[-1] != knowledge[i]:
                    change = True
    ##hints are not valid if the value was different then the color or if the hint doesnt add knowledge
    if not haspositive:
        #print("invalid")
        return False, 0, ["Invalid hint"]
    if not change:
        #print("no change")
        return False, 0, ["No new information"]
    
    #print("New Knowledge", newknowledge)
    
    #
    #Vanaf hier is het aangepast door mij
    #
    
    #In plaats van voor elke kaar in de hand een functie op te roepen die acties 'voorspelt'
    #doe ik dat 1 keer
    
    #In de functie NEURAAL wordt uitgelegd wat daar gebeurt. Deze functie returned een lijst met 
    #acties waarvan wordt verwacht dat de speler ze doet, als de hint wordt gegeven.
    #Deze lijst heeft meestal maar 1 element, omdat het neurale netwerk meestal 1 actie duidelijk de beste vindt.
    #Als het neurale netwerk meerdere acties plausibel vindt, en 1 van die acties is goed, dan wordt de hint goedgekeurd
    
    ACTIONS = NEURAAL(allknowledge, newknowledge, trash, played, hints)
    
    #De acties in de lijst zijn tuples, bijvoorbeeld (PLAY, 4, 0.89), dit betekent dat het Netwerk voorspelt
    #dat de 5e kaart in de hand wordt gespeeld (0-basis) met een kans van 89%
    
    #Hieronder wordt voor elke actie uit de lijst gechekt of deze matcht met de intentie die bij die kaart hoort
    #Bij een match, krijgt de Hint een positieve score, bij een mismatch een negative score. Omdat een mismatch beteken dat er
    # ene kans bestaat dat de tegenspeler een fout gaat maken, is de negatieve score erg hoog.
    #De score wordt vermenigvuuldigt met de kans dat iets gebeurt. Elke mogelijke actie krijgt een score. 
    #Die scores worden bij elkaar opgeteld en als de score positief is, dan wordt een hint goedgekeurd. 
    #Als de kans erg klein is dat de speler een verkeerde zet gaat doen,
    #dan kan de hint uiteindelijk toch nog positief worden. 
    
    for ACTION in ACTIONS:
        
        #Het tweede element van de tuple is het nummer van de kaart waarmee iets gedaan wordt
        (action, card , pred) = ACTION
        
        score = 0
        predictions = []
        
        #Wouldreturn is een lijst waarin voor elke actie wordt opgeslagen wat de uitkomst zou zijn;
        #met andere worden, er wordt bijgehouden of een actie goed zou zijn of niet
        WouldReturn = []
        


        #Als de voorspelling van een kaart PLAY is, maar de intentie van die kaart is niet PLAY
        #dan wordt de hint dus afgekeurd
        if action == PLAY and intentions[card] != PLAY:
            #print "would cause them to play", f(hand[card])
            
            WouldReturn.append((False, -20 * pred, predictions + [PLAY]))
            continue
            
        #Als de voorspelling van een kaart DISCARD is, maar de intentie van die kaart is niet DISCARD
        #dan wordt de hint dus afgekeurd
        
        
        if action == DISCARD and intentions[card] not in [DISCARD, CANDISCARD]:
            #print "would cause them to discard", f(hand[card])
            WouldReturn.append((False, -20 * pred, predictions + [DISCARD]))
            continue

        #Als er wordt voorspelt dat de speler een hint gaat geven, dan wordt de actie ook afgekeurd
        elif action == None:
            WouldReturn.append((False, 0, predictions))
        
        #Als er geen mismatch is, dan wordt de hint goedgekeurd
        #Een kaart spelen is beter dan een kaart discarden dus de score daarvan is hoger.
        #De score wordt vermingvuldigt met de kans dat die actie wordt gedaan.
        else:
            if action == PLAY:
                WouldReturn.append((True, 2*pred, predictions))
            if action == DISCARD:
                WouldReturn.append((True, 1*pred, predictions))

    
    #Nu is WouldReturn een lijst met meerdere acties en de scores zijn afhankelijk van hoe groot de kans is
    #Voor elke mogelijke actie van een hint wordt de score opgeteld.
    
    #Als de score uiteindelijk hoger is dan 0, dan is er dus gebleken dat de hint waarschijnlijk goed uit zal pakken
    #en dus wordt de hint goedgekeurd.
    
    #Het sorteren gebeurt alleen, om de prediction van de meest positieve of meest negatieve actie te returnen,
    #maar dit heeft geen effect op de uitkomst, want de prediction wordt alleen gebruikt voor de uitleg van een actie
    
    #positive = []
    Score = 0
    
    for Return in WouldReturn:
        Score += Return[1]

    if Score > 0:
        WouldReturn = sorted(WouldReturn, key=lambda x: x[1])
        predictions = WouldReturn[0][2]
        return (True, Score, predictions)
    
    if Score <= 0:
        WouldReturn = sorted(WouldReturn, key=lambda x: x[1], reverse = True)
        predictions = WouldReturn[0][2]
        return (False, Score, predictions)
    
    #Voordat ik de scores met kansen vermenigvuldigden was dit het laatste deel van deze functie
    #positive = []
    #for Return in WouldReturn:
        #if Return[0] == True:
        #positive.append(Return)
    
    #if len(positive) > 0:
        #positive = sorted(positive, key=lambda x: x[1])
        #return positive[0]
    #else:
        #return random.choice(WouldReturn)
        
    
                          
            
###########
###########Extra toegevoegde functies
###########



#maakt van alle informatie een lijst die als input aan netwerk kan worden gegeven
def MaakInput(Knowledge, Mind, tafelrep, tokens, fuses, aantalkaarten):
    Input = []
    
    for c in Knowledge:
        for y in c:
            Input.append(y)
    
    for x in Mind:
        Input.append(x)
    
    for c in tafelrep:
        for y in c:
            Input.append(y)
    
    Input.append(tokens)
    Input.append(fuses)
    Input.append(aantalkaarten)
    
    return Input






def updateKnowledge(used):
    knowledge=[[3,2,2,2,1],[3,2,2,2,1],[3,2,2,2,1],[3,2,2,2,1],[3,2,2,2,1]]
    result = copy.deepcopy(knowledge)
    teller = 0
    for (c,nr) in used:
        result[c][nr-1] = max(knowledge[c][nr-1] - used[c,nr], 0)
    return result

def updateOpTafel(played):
    result = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
    for (c,nr) in played:
        result[c][nr-1] = 1
    return result


def MaakMindvanknowledge(know, newknow):
    MIND = []
    
    KNOW = copy.deepcopy(know)
    
    teller = 0
    for new in newknow:
        KNOW[1][teller] = new
        teller+=1
    
    for x in KNOW:
        for y in x:
            for z in y:
                for p in z:
                    if p > 0:
                        MIND.append(1)
                    else:
                        MIND.append(0)
    return MIND


####### tot hier
#######
#######

            
            
class IntentionalPlayerML(Player):
    def __init__(self, name, pnr):
        self.name = name
        self.hints = {}
        self.pnr = pnr
        self.gothint = None
        self.last_knowledge = []
        self.last_played = []
        self.last_board = []
        self.explanation = []
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        #print("knowledge begin", knowledge) 
        handsize = len(knowledge[0])
        possible = []
        result = None
        self.explanation = []
        self.explanation.append(["Your Hand:"] + map(f, hands[1-nr]))
        
        #makes list: 'possible' for each card. containts lists which have every possible card a card could be
        self.gothint = None
        for k in knowledge[nr]:
            possible.append(get_possible(k))
        
        #if all the possibilities of a card are playable, Action = play that card
        #if a card is definitely discardable, add the number of the card to a list of discardables 
        discards = []
        duplicates = []
        for i,p in enumerate(possible):
            if playable(p,board):
                result = Action(PLAY, cnr=i)
            if discardable(p,board):
                discards.append(i)

        #if discards is not empty and there are less then 8 hint tokens and result is empty:
        #result = random card from discards
        #oftewel er kan geen hint worden gegeven en niet met zekerheid worden gespeeld, dus er wordt een kaart weggedaan
        if discards and hints < 8 and not result:
            result =  Action(DISCARD, cnr=random.choice(discards))
        
        
        #hier worden intenties voor elke kaart uit de hand van de ander gemaakt
        #elke kaart van de ander krijgt: 'PLAY', als kaart playable is
                                        ###'DISCARD, als kaart niet meer gebruikt kan worden
                                        ###'CANDISCARD', als er nog meer van die kaart in het spel zitten
        playables = []
        useless = []
        discardables = []
        othercards = trash + board
        intentions = [None for i in xrange(handsize)]
        for i,h in enumerate(hands):
            if i != nr:
                for j,(col,n) in enumerate(h):
                    if board[col][1] + 1 == n:
                        playables.append((i,j))
                        intentions[j] = PLAY
                    if board[col][1] >= n:
                        useless.append((i,j))
                        if not intentions[j]:
                            intentions[j] = DISCARD
                    if n < 5 and (col,n) not in othercards:
                        discardables.append((i,j))
                        if not intentions[j]:
                            intentions[j] = CANDISCARD
        
        self.explanation.append(["Intentions"] + map(format_intention, intentions))
        
        #Hierna wordt voor elke hint gekeken wat er in de knowledge structuur van de ander verandert (knowledge) 
        #en welke actie de andere dan zou doen
        Result = []
        
        if hints > 0:
            valid = []
            
            Valid = []
            
            for c in ALL_COLORS:
                action = (HINT_COLOR, c)
                #print "HINT", COLORNAMES[c]
                
                (isvalid,score,expl) = pretend_ML(action, knowledge[1-nr], intentions, hands[1-nr], board, trash, played, knowledge, hints)
                
                #(Isvalid,Score, Expl) = pretend(action, knowledge[1-nr], intentions, hands[1-nr], board)
                
                self.explanation.append(["Prediction for: Hint Color " + COLORNAMES[c]] + map(format_intention, expl))
                #print isvalid, score
                if isvalid:
                    valid.append((action,score))
                
                #if Isvalid:
                    #Valid.append((Action, Score))
            
            for r in xrange(5):
                r += 1
                action = (HINT_NUMBER, r)
                #print "HINT", r,
                
                (isvalid,score, expl) = pretend_ML(action, knowledge[1-nr], intentions, hands[1-nr], board, trash, played, knowledge, hints)
                
                #(Isvalid,Score, Expl) = pretend(action, knowledge[1-nr], intentions, hands[1-nr], board)
                self.explanation.append(["Prediction for: Hint Rank " + str(r)] + map(format_intention, expl))
                #print isvalid, score
                if isvalid:
                    valid.append((action,score))
                
                #if Isvalid:
                    #Valid.append((action, Score))
            
            #after all hints are simulated, sort the hints on score
            #the first element of the sorted list is the best scoring hint
            #result is that hint
            
            
            #if Valid and not result:
                #Valid.sort(key=lambda (a,s): -s)
                #(a,s) = Valid[0]
                #if a[0] == HINT_COLOR:
                    #Result = Action(HINT_COLOR, pnr=1-nr, col=a[1])
                #else:
                    #Result = Action(HINT_NUMBER, pnr=1-nr, num=a[1])
            
            if valid and not result:
                valid.sort(key=lambda (a,s): -s)
                #print valid
                (a,s) = valid[0]
                if a[0] == HINT_COLOR:
                    result = Action(HINT_COLOR, pnr=1-nr, col=a[1])
                else:
                    result = Action(HINT_NUMBER, pnr=1-nr, num=a[1])
        
        #if Result:
            #resultaat = str(result)
            #Resultaat = str(Result)

            #if result is a hint
            #if resultaat[0] == "h":
                #if Result != result:
                    #print("ANDERS")
                    #print("int zegt ", Resultaat, " ML zegt ", resultaat) 
                #else:
                    #print("ZELFDE")
                    #print("int zegt ", Resultaat, " ML zegt ", resultaat) 
            
            

        self.explanation.append(["My Knowledge"] + map(format_knowledge, knowledge[nr]))
        possible = [ Action(DISCARD, cnr=i) for i in xrange(handsize) ]
        
        scores = map(lambda p: pretend_discard(p, knowledge[nr], board, trash), possible)
        
        def format_term((col,rank,n,prob,val)):
            return COLORNAMES[col] + " " + str(rank) + " (%.2f%%): %.2f"%(prob*100, val)
            
        self.explanation.append(["Discard Scores"] + map(lambda (a,s,t): "\n".join(map(format_term, t)) + "\n%.2f"%(s), scores))
        scores.sort(key=lambda (a,s,t): -s)
        if result:
            return result
        return scores[0][0]
        
        return random.choice([Action(DISCARD, cnr=i) for i in xrange(handsize)])
    
    def inform(self, action, player, game):
        if action.type in [PLAY, DISCARD]:
            x = str(action)
            #print(x)
            if (action.cnr,player) in self.hints:
                self.hints[(action.cnr,player)] = []
            for i in xrange(10):
                if (action.cnr+i+1,player) in self.hints:
                    self.hints[(action.cnr+i,player)] = self.hints[(action.cnr+i+1,player)]
                    self.hints[(action.cnr+i+1,player)] = []
        elif action.pnr == self.pnr:
            self.gothint = (action,player)
            self.last_knowledge = game.knowledge[:]
            self.last_board = game.board[:]
            self.last_trash = game.trash[:]
            self.played = game.played[:]
            
            
            
class SelfIntentionalPlayer(Player):
    def __init__(self, name, pnr):
        self.name = name
        self.hints = {}
        self.pnr = pnr
        self.gothint = None
        self.last_knowledge = []
        self.last_played = []
        self.last_board = []
        self.explanation = []
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        handsize = len(knowledge[0])
        possible = []
        result = None
        self.explanation = []
        self.explanation.append(["Your Hand:"] + map(f, hands[1-nr]))
        action = []
        if self.gothint:
            (act,plr) = self.gothint
            if act.type == HINT_COLOR:
                for k in knowledge[nr]:
                    action.append(whattodo(k, sum(k[act.col]) > 0, board))
            elif act.type == HINT_NUMBER:
                for k in knowledge[nr]:
                    cnt = 0
                    for c in ALL_COLORS:
                        cnt += k[c][act.num-1]
                    action.append(whattodo(k, cnt > 0, board))
                    

        if action:
            self.explanation.append(["What you want me to do"] + map(format_intention, action))
            for i,a in enumerate(action):
                if a == PLAY and (not result or result.type == DISCARD):
                    result = Action(PLAY, cnr=i)
                elif a == DISCARD and not result:
                    result = Action(DISCARD, cnr=i)

        self.gothint = None
        for k in knowledge[nr]:
            possible.append(get_possible(k))
        
        discards = []
        duplicates = []
        for i,p in enumerate(possible):
            if playable(p,board) and not result:
                result = Action(PLAY, cnr=i)
            if discardable(p,board):
                discards.append(i)

        if discards and hints < 8 and not result:
            result =  Action(DISCARD, cnr=random.choice(discards))
            
        playables = []
        useless = []
        discardables = []
        othercards = trash + board
        intentions = [None for i in xrange(handsize)]
        for i,h in enumerate(hands):
            if i != nr:
                for j,(col,n) in enumerate(h):
                    if board[col][1] + 1 == n:
                        playables.append((i,j))
                        intentions[j] = PLAY
                    if board[col][1] >= n:
                        useless.append((i,j))
                        if not intentions[j]:
                            intentions[j] = DISCARD
                    if n < 5 and (col,n) not in othercards:
                        discardables.append((i,j))
                        if not intentions[j]:
                            intentions[j] = CANDISCARD
        
        self.explanation.append(["Intentions"] + map(format_intention, intentions))
        
        
            
        if hints > 0:
            valid = []
            for c in ALL_COLORS:
                action = (HINT_COLOR, c)
                #print "HINT", COLORNAMES[c],
                (isvalid,score,expl) = pretend(action, knowledge[1-nr], intentions, hands[1-nr], board)
                self.explanation.append(["Prediction for: Hint Color " + COLORNAMES[c]] + map(format_intention, expl))
                #print isvalid, score
                if isvalid:
                    valid.append((action,score))
            
            for r in xrange(5):
                r += 1
                action = (HINT_NUMBER, r)
                #print "HINT", r,
                
                (isvalid,score, expl) = pretend(action, knowledge[1-nr], intentions, hands[1-nr], board)
                self.explanation.append(["Prediction for: Hint Rank " + str(r)] + map(format_intention, expl))
                #print isvalid, score
                if isvalid:
                    valid.append((action,score))
                 
            if valid and not result:
                valid.sort(key=lambda (a,s): -s)
                #print valid
                (a,s) = valid[0]
                if a[0] == HINT_COLOR:
                    result = Action(HINT_COLOR, pnr=1-nr, col=a[1])
                else:
                    result = Action(HINT_NUMBER, pnr=1-nr, num=a[1])
                    

        self.explanation.append(["My Knowledge"] + map(format_knowledge, knowledge[nr]))
        possible = [ Action(DISCARD, cnr=i) for i in xrange(handsize) ]
        
        scores = map(lambda p: pretend_discard(p, knowledge[nr], board, trash), possible)
        def format_term((col,rank,n,prob,val)):
            return COLORNAMES[col] + " " + str(rank) + " (%.2f%%): %.2f"%(prob*100, val)
            
        self.explanation.append(["Discard Scores"] + map(lambda (a,s,t): "\n".join(map(format_term, t)) + "\n%.2f"%(s), scores))
        scores.sort(key=lambda (a,s,t): -s)
        if result:
            return result
        return scores[0][0]
        
        return random.choice([Action(DISCARD, cnr=i) for i in xrange(handsize)])
    def inform(self, action, player, game):
        if action.type in [PLAY, DISCARD]:
            x = str(action)
            if (action.cnr,player) in self.hints:
                self.hints[(action.cnr,player)] = []
            for i in xrange(10):
                if (action.cnr+i+1,player) in self.hints:
                    self.hints[(action.cnr+i,player)] = self.hints[(action.cnr+i+1,player)]
                    self.hints[(action.cnr+i+1,player)] = []
        elif action.pnr == self.pnr:
            self.gothint = (action,player)
            self.last_knowledge = game.knowledge[:]
            self.last_board = game.board[:]
            self.last_trash = game.trash[:]
            self.played = game.played[:]
            

    
def do_sample(knowledge):
    if not knowledge:
        return []
        
    possible = []
    
    for col in ALL_COLORS:
        for i,c in enumerate(knowledge[0][col]):
            for j in xrange(c):
                possible.append((col,i+1))
    if not possible:
        return None
    
    other = do_sample(knowledge[1:])
    if other is None:
        return None
    sample = random.choice(possible)
    return [sample] + other
    
def sample_hand(knowledge):
    result = None
    while result is None:
        result = do_sample(knowledge)
    return result
    
used = {}
for c in ALL_COLORS:
    for i,cnt in enumerate(COUNTS):
        used[(c,i+1)] = 0

    

class SamplingRecognitionPlayer(Player):
    def __init__(self, name, pnr, other=IntentionalPlayer, maxtime=5000):
        self.name = name
        self.hints = {}
        self.pnr = pnr
        self.gothint = None
        self.last_knowledge = []
        self.last_played = []
        self.last_board = []
        self.other = other
        self.maxtime = maxtime
        self.explanation = []
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        handsize = len(knowledge[0])
        possible = []
        
        if self.gothint:
            possiblehands = []
            wrong = 0
            used = {}
            
            for c in trash + played:
                if c not in used:
                    used[c] = 0
                used[c] += 1
            
            i = 0
            t0 = time.time()
            while i < self.maxtime:
                i += 1
                h = sample_hand(update_knowledge(knowledge[nr], used))
                newhands = hands[:]
                newhands[nr] = h
                other = self.other("Pinocchio", self.gothint[1])
                act = other.get_action(self.gothint[1], newhands, self.last_knowledge, self.last_trash, self.last_played, self.last_board, valid_actions, hints + 1)
                lastact = self.gothint[0]
                if act == lastact:
                    possiblehands.append(h)
                    def do(c,i):
                        newhands = hands[:]
                        h1 = h[:]
                        h1[i] = c
                        newhands[nr] = h1
                        print other.get_action(self.gothint[1], newhands, self.last_knowledge, self.last_trash, self.last_played, self.last_board, valid_actions, hints + 1)
                    #import pdb
                    #pdb.set_trace()
                else:
                    wrong += 1
            #print "sampled", i
            #print len(possiblehands), "would have led to", self.gothint[0], "and not:", wrong
            #print f(possiblehands)
            if possiblehands:
                mostlikely = [(0,0) for i in xrange(len(possiblehands[0]))]
                for i in xrange(len(possiblehands[0])):
                    counts = {}
                    for h in possiblehands:
                        if h[i] not in counts:
                            counts[h[i]] = 0
                        counts[h[i]] += 1
                    for c in counts:
                        if counts[c] > mostlikely[i][1]:
                            mostlikely[i] = (c,counts[c])
                #print "most likely:", mostlikely
                m = max(mostlikely, key=lambda (card,cnt): cnt)
                second = mostlikely[:]
                second.remove(m)
                m2 = max(second, key=lambda (card,cnt): cnt)
                if m[1] >= m2[1]*a:
                    #print ">>>>>>> deduced!", f(m[0]), m[1],"vs", f(m2[0]), m2[1]
                    knowledge = copy.deepcopy(knowledge)
                    knowledge[nr][mostlikely.index(m)] = iscard(m[0])

        
        self.gothint = None
        for k in knowledge[nr]:
            possible.append(get_possible(k))
        
        discards = []
        duplicates = []
        for i,p in enumerate(possible):
            if playable(p,board):
                return Action(PLAY, cnr=i)
            if discardable(p,board):
                discards.append(i)

        if discards:
            return Action(DISCARD, cnr=random.choice(discards))
            
        playables = []
        for i,h in enumerate(hands):
            if i != nr:
                for j,(col,n) in enumerate(h):
                    if board[col][1] + 1 == n:
                        playables.append((i,j))
        playables.sort(key=lambda (i,j): -hands[i][j][1])
        while playables and hints > 0:
            i,j = playables[0]
            knows_rank = True
            real_color = hands[i][j][0]
            real_rank = hands[i][j][0]
            k = knowledge[i][j]
            
            hinttype = [HINT_COLOR, HINT_NUMBER]
            if (j,i) not in self.hints:
                self.hints[(j,i)] = []
            
            for h in self.hints[(j,i)]:
                hinttype.remove(h)
            
            if HINT_NUMBER in hinttype:
                self.hints[(j,i)].append(HINT_NUMBER)
                return Action(HINT_NUMBER, pnr=i, num=hands[i][j][1])
            if HINT_COLOR in hinttype:
                self.hints[(j,i)].append(HINT_COLOR)
                return Action(HINT_COLOR, pnr=i, col=hands[i][j][0])
            
            playables = playables[1:]
        
        for i, k in enumerate(knowledge):
            if i == nr:
                continue
            cards = range(len(k))
            random.shuffle(cards)
            c = cards[0]
            (col,num) = hands[i][c]            
            hinttype = [HINT_COLOR, HINT_NUMBER]
            if (c,i) not in self.hints:
                self.hints[(c,i)] = []
            for h in self.hints[(c,i)]:
                hinttype.remove(h)
            if hinttype and hints > 0:
                if random.choice(hinttype) == HINT_COLOR:
                    self.hints[(c,i)].append(HINT_COLOR)
                    return Action(HINT_COLOR, pnr=i, col=col)
                else:
                    self.hints[(c,i)].append(HINT_NUMBER)
                    return Action(HINT_NUMBER, pnr=i, num=num)

        return random.choice([Action(DISCARD, cnr=i) for i in xrange(handsize)])
    def inform(self, action, player, game):
        if action.type in [PLAY, DISCARD]:
            x = str(action)
            if (action.cnr,player) in self.hints:
                self.hints[(action.cnr,player)] = []
            for i in xrange(10):
                if (action.cnr+i+1,player) in self.hints:
                    self.hints[(action.cnr+i,player)] = self.hints[(action.cnr+i+1,player)]
                    self.hints[(action.cnr+i+1,player)] = []
        elif action.pnr == self.pnr:
            self.gothint = (action,player)
            self.last_knowledge = game.knowledge[:]
            self.last_board = game.board[:]
            self.last_trash = game.trash[:]
            self.played = game.played[:]
            
class FullyIntentionalPlayer(Player):
    def __init__(self, name, pnr):
        self.name = name
        self.hints = {}
        self.pnr = pnr
        self.gothint = None
        self.last_knowledge = []
        self.last_played = []
        self.last_board = []
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        handsize = len(knowledge[0])
        possible = []
        
        
        self.gothint = None
        for k in knowledge[nr]:
            possible.append(get_possible(k))
        
        discards = []
        plays = []
        duplicates = []
        for i,p in enumerate(possible):
            if playable(p,board):
                plays.append(i)
            if discardable(p,board):
                discards.append(i)
            
        playables = []
        useless = []
        discardables = []
        othercards = trash + board
        intentions = [None for i in xrange(handsize)]
        for i,h in enumerate(hands):
            if i != nr:
                for j,(col,n) in enumerate(h):
                    if board[col][1] + 1 == n:
                        playables.append((i,j))
                        intentions[j] = PLAY
                    if board[col][1] <= n:
                        useless.append((i,j))
                        if not intentions[j]:
                            intentions[j] = DISCARD
                    if n < 5 and (col,n) not in othercards:
                        discardables.append((i,j))
                        if not intentions[j]:
                            intentions[j] = CANDISCARD
        
        

        if hints > 0:
            valid = []
            for c in ALL_COLORS:
                action = (HINT_COLOR, c)
                #print "HINT", COLORNAMES[c],
                (isvalid,score) = pretend(action, knowledge[1-nr], intentions, hands[1-nr], board)
                #print isvalid, score
                if isvalid:
                    valid.append((action,score))
            
            for r in xrange(5):
                r += 1
                action = (HINT_NUMBER, r)
                #print "HINT", r,
                (isvalid,score) = pretend(action, knowledge[1-nr], intentions, hands[1-nr], board)
                #print isvalid, score
                if isvalid:
                    valid.append((action,score))
            if valid:
                valid.sort(key=lambda (a,s): -s)
                #print valid
                (a,s) = valid[0]
                if a[0] == HINT_COLOR:
                    return Action(HINT_COLOR, pnr=1-nr, col=a[1])
                else:
                    return Action(HINT_NUMBER, pnr=1-nr, num=a[1])
            
        
        for i, k in enumerate(knowledge):
            if i == nr or True:
                continue
            cards = range(len(k))
            random.shuffle(cards)
            c = cards[0]
            (col,num) = hands[i][c]            
            hinttype = [HINT_COLOR, HINT_NUMBER]
            if (c,i) not in self.hints:
                self.hints[(c,i)] = []
            for h in self.hints[(c,i)]:
                hinttype.remove(h)
            if hinttype and hints > 0:
                if random.choice(hinttype) == HINT_COLOR:
                    self.hints[(c,i)].append(HINT_COLOR)
                    return Action(HINT_COLOR, pnr=i, col=col)
                else:
                    self.hints[(c,i)].append(HINT_NUMBER)
                    return Action(HINT_NUMBER, pnr=i, num=num)

        return random.choice([Action(DISCARD, cnr=i) for i in xrange(handsize)])
    def inform(self, action, player, game):
        if action.type in [PLAY, DISCARD]:
            x = str(action)
            if (action.cnr,player) in self.hints:
                self.hints[(action.cnr,player)] = []
            for i in xrange(10):
                if (action.cnr+i+1,player) in self.hints:
                    self.hints[(action.cnr+i,player)] = self.hints[(action.cnr+i+1,player)]
                    self.hints[(action.cnr+i+1,player)] = []
        elif action.pnr == self.pnr:
            self.gothint = (action,player)
            self.last_knowledge = game.knowledge[:]
            self.last_board = game.board[:]
            self.last_trash = game.trash[:]
            self.played = game.played[:]
        
def format_card((col,num)):
    return COLORNAMES[col] + " " + str(num)
        
def format_hand(hand):
    return ", ".join(map(format_card, hand))
        

class Game(object):
    def __init__(self, players, log=sys.stdout, format=0):
        self.players = players
        self.hits = 3
        self.hints = 8
        self.current_player = 0
        self.board = map(lambda c: (c,0), ALL_COLORS)
        self.played = []
        self.deck = make_deck()
        self.extra_turns = 0
        self.hands = []
        self.knowledge = []
        self.make_hands()
        self.trash = []
        self.log = log
        self.turn = 1
        self.format = format
        self.dopostsurvey = False
        self.study = False
        if self.format:
            print >> self.log, self.deck
    def make_hands(self):
        handsize = 4
        if len(self.players) < 4:
            handsize = 5
        for i, p in enumerate(self.players):
            self.hands.append([])
            self.knowledge.append([])
            for j in xrange(handsize):
                self.draw_card(i)
    def draw_card(self, pnr=None):
        if pnr is None:
            pnr = self.current_player
        if not self.deck:
            return
        self.hands[pnr].append(self.deck[0])
        #print(self.deck[0])
        self.knowledge[pnr].append(initial_knowledge())
        del self.deck[0]
    def perform(self, action):
        for p in self.players:
            p.inform(action, self.current_player, self)
        if format:
            print >> self.log, "MOVE:", self.current_player, action.type, action.cnr, action.pnr, action.col, action.num
        if action.type == HINT_COLOR:
            self.hints -= 1
            print >>self.log, self.players[self.current_player].name, "hints", self.players[action.pnr].name, "about all their", COLORNAMES[action.col], "cards", "hints remaining:", self.hints
            print >>self.log, self.players[action.pnr].name, "has", format_hand(self.hands[action.pnr])
            for (col,num),knowledge in zip(self.hands[action.pnr],self.knowledge[action.pnr]):
                if col == action.col:
                    for i, k in enumerate(knowledge):
                        if i != col:
                            for i in xrange(len(k)):
                                k[i] = 0
                else:
                    for i in xrange(len(knowledge[action.col])):
                        knowledge[action.col][i] = 0
        elif action.type == HINT_NUMBER:
            self.hints -= 1
            print >>self.log, self.players[self.current_player].name, "hints", self.players[action.pnr].name, "about all their", action.num, "hints remaining:", self.hints
            print >>self.log, self.players[action.pnr].name, "has", format_hand(self.hands[action.pnr])
            for (col,num),knowledge in zip(self.hands[action.pnr],self.knowledge[action.pnr]):
                if num == action.num:
                    for k in knowledge:
                        for i in xrange(len(COUNTS)):
                            if i+1 != num:
                                k[i] = 0
                else:
                    for k in knowledge:
                        k[action.num-1] = 0
        elif action.type == PLAY:
            (col,num) = self.hands[self.current_player][action.cnr]
            print >>self.log, self.players[self.current_player].name, "plays", format_card((col,num)),
            if self.board[col][1] == num-1:
                self.board[col] = (col,num)
                self.played.append((col,num))
                if num == 5:
                    self.hints += 1
                    self.hints = min(self.hints, 8)
                print >>self.log, "successfully! Board is now", format_hand(self.board)
            else:
                self.trash.append((col,num))
                self.hits -= 1
                print >>self.log, "and fails. Board was", format_hand(self.board)
            del self.hands[self.current_player][action.cnr]
            del self.knowledge[self.current_player][action.cnr]
            self.draw_card()
            print >>self.log, self.players[self.current_player].name, "now has", format_hand(self.hands[self.current_player])
        else:
            self.hints += 1 
            self.hints = min(self.hints, 8)
            self.trash.append(self.hands[self.current_player][action.cnr])
            print >>self.log, self.players[self.current_player].name, "discards", format_card(self.hands[self.current_player][action.cnr])
            print >>self.log, "trash is now", format_hand(self.trash)
            del self.hands[self.current_player][action.cnr]
            del self.knowledge[self.current_player][action.cnr]
            self.draw_card()
            print >>self.log, self.players[self.current_player].name, "now has", format_hand(self.hands[self.current_player])
    def valid_actions(self):
        valid = []
        for i in xrange(len(self.hands[self.current_player])):
            valid.append(Action(PLAY, cnr=i))
            valid.append(Action(DISCARD, cnr=i))
        if self.hints > 0:
            for i, p in enumerate(self.players):
                if i != self.current_player:
                    for col in set(map(lambda (col,num): col, self.hands[i])):
                        valid.append(Action(HINT_COLOR, pnr=i, col=col))
                    for num in set(map(lambda (col,num): num, self.hands[i])):
                        valid.append(Action(HINT_NUMBER, pnr=i, num=num))
        return valid
    def run(self, turns=-1):
        self.turn = 1
        while not self.done() and (turns < 0 or self.turn < turns):
            self.turn += 1
            if not self.deck:
                self.extra_turns += 1
            hands = []
            for i, h in enumerate(self.hands):
                if i == self.current_player:
                    hands.append([])
                else:
                    hands.append(h)
            action = self.players[self.current_player].get_action(self.current_player, hands, self.knowledge, self.trash, self.played, self.board, self.valid_actions(), self.hints)
            self.perform(action)
            self.current_player += 1
            self.current_player %= len(self.players)
        print >>self.log, "Game done, hits left:", self.hits
        points = self.score()
        print >>self.log, "Points:", points
        return points
    def score(self):
        return sum(map(lambda (col,num): num, self.board))
    def single_turn(self):
        if not self.done():
            if not self.deck:
                self.extra_turns += 1
            hands = []
            for i, h in enumerate(self.hands):
                if i == self.current_player:
                    hands.append([])
                else:
                    hands.append(h)
            action = self.players[self.current_player].get_action(self.current_player, hands, self.knowledge, self.trash, self.played, self.board, self.valid_actions(), self.hints)
            self.perform(action)
            self.current_player += 1
            self.current_player %= len(self.players)
    def external_turn(self, action): 
        if not self.done():
            if not self.deck:
                self.extra_turns += 1
            self.perform(action)
            self.current_player += 1
            self.current_player %= len(self.players)
    def done(self):
        if self.extra_turns == len(self.players) or self.hits == 0:
            return True
        for (col,num) in self.board:
            if num != 5:
                return False
        return True
    def finish(self):
        if self.format:
            print >> self.log, "Score", self.score()
            self.log.close()
        
    
class NullStream(object):
    def write(self, *args):
        pass
        
random.seed(123)

playertypes = {"random": Player, "inner": InnerStatePlayer, "outer": OuterStatePlayer, "self": SelfRecognitionPlayer, "intentional": IntentionalPlayer, "sample": SamplingRecognitionPlayer, "full": SelfIntentionalPlayer, "timed": TimedPlayer}
names = ["Shangdi", "Yu Di", "Tian", "Nu Wa", "Pangu"]
        
        
def make_player(player, i):
    if player in playertypes:
        return playertypes[player](names[i], i)
    elif player.startswith("self("):
        other = player[5:-1]
        return SelfRecognitionPlayer(names[i], i, playertypes[other])
    elif player.startswith("sample("):
        other = player[7:-1]
        if "," in other:
            othername, maxtime = other.split(",")
            othername = othername.strip()
            maxtime = int(maxtime.strip())
            return SamplingRecognitionPlayer(names[i], i, playertypes[othername], maxtime=maxtime)
        return SamplingRecognitionPlayer(names[i], i, playertypes[other])
    return None 


def main(args):
    if not args:
        args = ["random"]*3
    if args[0] == "trial":
        treatments = [["intentional", "intentional"], ["intentional", "outer"], ["outer", "outer"]]
        #[["sample(intentional, 50)", "sample(intentional, 50)"], ["sample(intentional, 100)", "sample(intentional, 100)"]] #, ["self(intentional)", "self(intentional)"], ["self", "self"]]
        results = []
        print treatments
        for i in xrange(int(args[1])):
            result = []
            times = []
            avgtimes = []
            print "trial", i+1
            for t in treatments:
                random.seed(i)
                players = []
                for i,player in enumerate(t):
                    players.append(make_player(player,i))
                g = Game(players, NullStream())
                t0 = time.time()
                result.append(g.run())
                times.append(time.time() - t0)
                avgtimes.append(times[-1]*1.0/g.turn)
                print ".",
            print
            print "scores:",result
            print "times:", times
            print "avg times:", avgtimes
        
        return
        
        
    players = []
    
    for i,a in enumerate(args):
        players.append(make_player(a, i))
        
    n = 10000
    out = NullStream()
    if n < 3:
        out = sys.stdout
    pts = []
    for i in xrange(n):
        if (i+1)%100 == 0:
            print "Starting game", i+1
        random.seed(i+1)
        g = Game(players, out)
        try:
            pts.append(g.run())
            if (i+1)%100 == 0:
                print "score", pts[-1]
        except Exception:
            import traceback
            traceback.print_exc()
    if n < 10:
        print pts
    import numpy
    print "average:", numpy.mean(pts)
    print "stddev:", numpy.std(pts, ddof=1)
    print "range", min(pts), max(pts)
    
    
if __name__ == "__main__":
    main(sys.argv[1:])
    
    
    
    
    ####TROEP
    
#print("card:", c, "newknowledge", k)
        ##p = true als hint over de kaart ging
        #if p == True:
            #action = NEURAAL(allknowledge, k, trash, played, hints)
            
            
            #if not isinstance(action, int) and n == None:
                
                #for nr, act in action:
                    
                    #if action == PLAY and i != PLAY:
                        #continue
                    #if action == DISCARD and i not in [DISCARD, CANDISCARD]:
                        #continue
                    #if action == PLAY and i == PLAY:
                        #bedenk oplossing            
             
        #else:
            #action = None
            
            
    
    #score = 0
    #predictions = []
    #pos = False
    #for i,c,k,p,x in zip(intentions, hand, newknowledge, positive, range(len(hand))):
        
        ###wat gaat de speler doen met de nieuwe informatie
        
        ###wat zou de speler volgens de intentional AI doen
        #Action = whattodo(k, p, board)
        
        #if Action != action:
            #print("ML ANDERS DAN INTENTIONAL")
        
        #if action == PLAY and i != PLAY:
            #print "would cause them to play", f(c)
            #return False, 0, predictions + [PLAY]
        
        #if action == DISCARD and i not in [DISCARD, CANDISCARD]:
            #print "would cause them to discard", f(c)
            #return False, 0, predictions + [DISCARD]
            
        #if action == PLAY and i == PLAY:
            #pos = True
            #predictions.append(PLAY)
            #score += 3
        #elif action == DISCARD and i in [DISCARD, CANDISCARD]:
            #pos = True
            #predictions.append(DISCARD)
            #if i == DISCARD:
                #score += 2
            #else:
                #score += 1
        #else:
            #predictions.append(None)
    #if not pos:
        #return False, score, predictions
    #return True,score, predictions
    
    
    
    
    
    
#Allekaarten = [(0,1),(0,2),(0,3),(0,4),(0,5),(1,1),(1,2),(1,3),(1,4),(1,5),(2,1),(2,2),(2,3),(2,4),(2,5),(3,1),(3,2),(3,3),(3,4),(3,5),(4,1),(4,2),(4,3),(4,4),(4,5)]

#wordt niet meer gebruikt
#def MaakAlleKaarten():
    #Allekaarten = []
    #for x in range(5):
        #for y in range(1,6):
            #Allekaarten.append((x,y))
    #return Allekaarten

#Allekaarten = MaakAlleKaarten()

#wordt niet meer gebruikt
#def BuildKnowledge(allekaarten):
    #mind = []
    #for kaart in allekaarten:
        #if((kaart[1]) == 1):
         #       mind.append((kaart, 3))
        #if kaart[1] == 2 or kaart[1] == 3 or kaart[1] == 4:
         #       mind.append((kaart, 2))
        #if((kaart[1]) == 5):
       #         mind.append((kaart, 1))
    #return mind

#wordt niet meer gebruikt
#def BuildMind(allekaarten, een):
    #mind = []
    #for kaart in allekaarten:
        #if een:
            #mind.append((kaart, 1))
        #else:
            #mind.append((kaart, 0))
    #return mind

#Knowledge = BuildKnowledge(Allekaarten)

#MindAI = []
#MindSpeler = []
#for x in range(5):
    #mindkaart = BuildMind(Allekaarten, True)
    #MindAI.append(mindkaart)
    #MindSpeler.append(mindkaart)

#KaartenOpTafel = BuildMind(Allekaarten, False)

#print(len(Knowledge), "Knowledge", Knowledge)
#print(len(MindAI), "MindAI", MindAI)
#print(len(MindSpeler), "MindSpeler", MindSpeler)
#print(len(KaartenOpTafel), "KaartenOpTafel", KaartenOpTafel)



#wordt niet meer gebruikt
#def MaakInputRaw(Knowledge, MindAI, MindSpeler, tafelrep, tokens, fuses, aantalkaarten):
    #Input = []
    
    #for y in Knowledge:
        #Input.append(y)
    
    #for mind in MindAI:
        #for y in mind:
            #Input.append(y)
            
    #for mind in MindSpeler:
        #for y in mind:
            #Input.append(y)
    
    #for y in tafelrep:
        #Input.append(y)
    
    #Input.append(tokens)
    #Input.append(fuses)
    #Input.append(aantalkaarten)
    
    #return Input

#wordt niet meer gebruikt
#def MaakInputClean(Knowledge, MindAI, MindSpeler, tafelrep, tokens, fuses, aantalkaarten):
    #Input = []
    
    #for x,y in Knowledge:
        #Input.append(y)
    
    #for mind in MindAI:
        #for x,y in mind:
            #Input.append(y)
            
    #for mind in MindSpeler:
        #for x,y in mind:
            #Input.append(y)
    
    #for x,y in tafelrep:
        #Input.append(y)
    
    #Input.append(tokens[1])
    #Input.append(fuses[1])
    #Input.append(aantalkaarten[1])
    
    #return Input

#InputRaw = MaakInputRaw(Knowledge, MindAI, MindSpeler, KaartenOpTafel,Hints, Fuses, AantalKaarten)
#Input = MaakInputClean(Knowledge, MindAI, MindSpeler, KaartenOpTafel,Hints, Fuses, AantalKaarten)

#print(len(Input), "Input", Input)
#print(len(InputRaw), "InputRaw", InputRaw)
    
    #wordt niet meer gebruikt
### returned kaarten die aan trash zijn toegevoed, als dat zo is
#def checkTrash(Trash):
    #Kaarten = []
    #aantal = len(Trash) - TrashNumber
    #for x in range(aantal):
       # Kaarten.append(Trash.pop)
    #TrashNumber += aantal
    #return Kaarten

#wordt niet meer gebruikt
#def checkPlayed(Played):
    #Kaarten = []
    #aantal = len(Played) - PlayedNumber
    #for x in range(aantal):
        #Kaarten.append(Played.pop)
    #PlayedNumber += aantal
    #return Kaarten      

#wordt niet meer gebruikt
#def UpdateKnowledge(Knowledge, kaarten):
    #for dekaart in kaarten:
        #teller = 0
        #for kaart, hoeveelheid in Knowledge:
            #if kaart == dekaart:
                #hoeveelheid -= 1
                #break
            #else:
                #teller += 1
        #Knowledge[teller] = (kaart, hoeveelheid)
    #return Knowledge


###wordt niet meer gebruikt
#def UpdateOpTafel(Optafel, kaarten):
    #for dekaart in kaarten:
        #teller = 0
        #for kaart, hoeveelheid in Optafel:
            #if kaart == dekaart:
                #hoeveelheid += 1
                #break
            #else:
                #teller += 1
        #Optafel[teller] = (kaart, hoeveelheid)
    #return Optafel
    
    
    
    
    ###Dit was eerst het einde van NEURAAL
    ###        ####Eerst
        #hoogste = 0
        #for nr, pred in PotentialAction:
            #if pred > hoogste:
                #beste = pred
                #hoogste = pred
                
                
        #if beste == cardnumber:
            #print("PLAY")
            #return PLAY
        #if beste == (cardnumber + 5):
            #print("DISCARD")
            #return DISCARD
        #return None  