#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Michael
#
# Created:     16/04/2014
# Copyright:   (c) Michael 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

class Event:
    nextState = None
    sucessCheckFunction = None
    def __init__(self, sucessCheckFunction = None, sucessCheckParam = [], nextState = None):
        #sucessCheckFunction is a function that will be run using sucessCheckParam
        #as the input. If the event returns "True", then the machine will shift
        #to the "nextState" state. It will do this untill all the events are
        #checked, or untill an event returns "True".

        self.sucessCheckFunction = sucessCheckFunction
        self.sucessCheckParam = sucessCheckParam
        self.nextState = nextState

    def checkForEvent(self):
        result = self.sucessCheckFunction(*self.sucessCheckParam)
        if (result != None):
            return self.sucessCheckFunction(*self.sucessCheckParam)
        else:
            return False

class State:
    #Stores the name of the state, the functions that will be run on an event check,
    #the action that will be performed by the owner, and the inputs for the action.
    events = []
    name = ""
    def __init__(self, name = "Null", events = [], action = None, actionInputs = [], stateMachineVariables = {}):
        self.name = name
        self.events = events
        self.action = action
        self.actionInputs = actionInputs
        self.stateMachineVariables = stateMachineVariables

    def performAction(self):
        if self.action!= None:
            self.action(*self.actionInputs)

    def checkForEvents(self):
        e = Event()
        for e in self.events:
            #print e
            if e.checkForEvent():
                return e.nextState
        return False

    def __repr__(self):
        return "<State: " + str(self.name) +" " +str(hash(self)) +">"


class StateMachine(object):
    currentState = State()
    innerVariables = {}

    def __init__(self, start = None, states = []):
        self.currentState = start
        self.states = states
        self.innerVariables = {}
        state = State()
        for state in states:
            for variable, value in state.stateMachineVariables.iteritems():
                self.innerVariables[variable] = value

    def currentStateAction(self):
        self.currentState.performAction()

    def checkCurrentState(self):
        if self.currentState != None:
            test = self.currentState.checkForEvents()
            if (test != False):
                print ("Found a state: " + str(test))
                self.currentState = test
                return


def alwaysTrue():
    return True

def main():
    #Testing Function
    event1 = Event(alwaysTrue, [], None)
    event2 = Event(alwaysTrue, [], None)

    State1 = State("Start",[event1])
    State2 = State("Mid",[event2])
    State3 = State("End",[event1])

    event1.nextState = State2
    event2.nextState = State3

    machine = StateMachine(State1, [State1,State2,State3])
    machine.checkCurrentState()
    machine.checkCurrentState()
    machine.checkCurrentState()

    pass

if __name__ == '__main__':
    main()
