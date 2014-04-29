#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Michael
#
# Created:     23/04/2014
# Copyright:   (c) Michael 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import StateMachine
import Entity
import Object

class GenericType(StateMachine.StateMachine):
    def __init__(self, owner):
        self.owner = Object.Object()
        self.owner = owner
        idleState = StateMachine.State ("Idle")
        followState = StateMachine.State("Following Player",[],self.owner.Action_MoveTwoardsPlayer,[True])

        spotPlayer = StateMachine.Event(self.owner.Event_IsPlayerInPOV,[],followState)

        idleState.events = [spotPlayer]

        super(GenericType,self).__init__(idleState,[idleState,followState])
