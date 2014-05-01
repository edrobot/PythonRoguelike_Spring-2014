#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Michael
#
# Created:     14/03/2014
# Copyright:   (c) Michael 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from Items import Item
import GUI
import GameState
import Equipment
import BodyParts
import random
import Resistance
import Object
import AI
import sys


class Entity:
    #Class containing anything that can move around and fight people.

    """
    Axioms of Entities
        > The player and NPCs follow the same rules of movement, statistics and combat.

        > An Entity a series of "Parts", "Traits", "Feats" and "Stats".

        >Parts decide how may items an entity can equipt, as well as certain
        other traits.

        #DONE: Add parts to game.

        Typically, the parts are as follows:
            Torso
            ->Head
            ->Torso
            ->Left Arm
            ->Right Arm
            ->Left Leg
            ->Right Leg

        > Traits are Abilities that are part of the player's body.
        This is decided at character creation, based on the race (erm,
        species) the player chooses. Humans are assumed to be the baseline.
        It is rare (but not unheard of) for an Entity to change traits.

        #TODO: Add traits to game.

        > Feats: Abilities that have been learned through training and study,
        such as the ability to use magic or wield a sword.
        The player can gain new Feats by leveling up.

        #TODO: Add feats to game.

        > Stats: Both feats and traits can provide "Stats", a numerical
        measurement of physical capability. The stats are as follows:

            Hit Points: A measure of how healthy the Entity is.
            If an entity reach 0 hitpoints, they die and leave behind a corpse.
            An enity's max Hitpoints are decided by it's Constitution score.

            Mana Points: A measure of how magic the Entity is.
            An entity's max Mana is decided by wisdom.

            Willpower: Used for certain special moves.
            All classes must have at least one willpower-based ability.
            Starts at %0, and goes up to %100. No stats influence Willpower.

            By default, it goes up %1 every 5 turns, but certain feats
            can changes this behaivor. Examples:

                Rage: Starts at 0, goes up 5% every time the user hits or is
                hit by an enemy. Goes down 1% every 20 turns.

                Inner Focus: Goes up 5% for every turn spent meditating
                (read: doing nothing).

                Gormet: Goes up when eating food. The higher-quality the food,
                the better (10% for Poor, 25% for Average, 50% for Good,
                100% for Amazing).

            Example powers include:

                Bravely Second: 25% willpower to take an extra turn. Can go
                into negatives, but if it's negative you need to wait for
                it to recharge.

                Second Wind: When killed, fully heals player in exchange
                for 100% willpower.


            Strength: A measure of physical strength.
            Boosts carrying capacity.

            Dexterity:

            Intelligence:

            Wisdom:

            Charisma:

            Constitution: Determines your ability to resist negative effects.

            #DONE: Add HP, MP, Willpower, Strength, Dexterity, Wisdom, Constitution, Charisma

            Resistances: Your ability to resist damage of various types.
            Also prevents negative status effects. Resistances stack up to a
            certain point. To reach "S" rank, you need a special item or feat.
            Types of resistance include:

                Nonmagic
                Magic
                Iron
                Silver
                Fire
                Ice
                Thunder
                Holy
                Dark

            #TODO: Implement resistances.

            Deflection: Your ability to deflect projectiles. Provdes a bonus to
            dodging attacks. Most types of armor provide at least some Deflection.
            Like resistances, this is tracked seperately for each kind of
            deflection. Deflection types include:

                Mundane
                Iron
                Magic
                Rays

            #TODO: Implement deflection.

            Speed: Calulated based on your carrying capacity, current items,
            and dexterity. Current effect TBA.

            #TODO: Figure out how Speed will work.
            #TODO: Implement speed.

            Status Ailments: Various bad things that the player can be afflicted
            with. Usually temporary. Effects include:

                Blindness: Cannot see.

                Colorblindless: Cannot distinguish between colors.

                Poison: Lose 1 HP per turn.
                    Additional resistance check every 10 turns.

                Mute: Cannot cast spells, other abilities may or may not work.

                AntiMagic: Cannot cast spells, magic items don't work.

                Madness: Stacking effects;
                    Shaking: Player cannot distinguish between different
                    enemies and objects on map.
                    Hillucination: Player cannot distinguish between different
                    enemies and objects on map and in bag.
                    True Madness: As above, but very powerful enemies spawn
                    that can only be seen while mad (such as the Slender Man)"

                Cursed: Max HP cut in half. Can stack up to 4 times.

            #TODO: Implement status ailments.

        > Damage Formula

            Normal Hit:
            (STR_RANK * Strength + DEX_RANK * Dexterity) + BaseHit
            + 1d100 > (EnemyDexterity + 50) * (1 * DEFLECTION_RANK) + 100

            Magic Hit:
            (WIS_RANK * Wisdom + INT_RANK * Intelligence) + BaseHit
            + 1d100 > (EnemyWisdom + 50) * (1 * DEFLECTION_RANK) + 100

            Normal Damage:
            ((STR_RANK*Strength + DEX_RANK*Dexterity) + BaseDamage
            - MinimumZero(EnemyDefense - Penetration)) * (1 * RESISTANCE_RANK)

            Magic Damage:
            ((INT_RANK*Intelligence + WIS_RANK*Wisdom) + BaseDamage)
            * (1 * RESISTANCE_RANK)

            Resist Status Ailment:
            (Constitution * RESISTANCE_RANK) + 1d100 >
            (Base_Chance + EnemyIntelligence)

                (To compensate for Strength and Intelligence only applying to
                damage, weapon and spell scaling should be skewed twoards these
                stats)


            Statistic Scaling Ranks:
            X: 0%/ F: 50% / E: 75% / D: 85% / C: 100% / B: 125% / A: 150% / S: 200%

            Resistance Scaling Ranks:
            F: 400% / E: 200% / D: 150% / C: 100% / B: 50% / A: 0% / S: -100%*
                *Absorbs damage, if applicable.

            #TODO: Implement damage formulae.

        > The player has the following advantages.
            Greater


    Axioms of Monster Design

    (Where "Monster" is defined as "a Creature that can potententially kill the player"

        > All non-unique creatures must come in families with 3 variants; Normal, Elite, and Last One

            Normal: The player's first introduction to a monster family.
            Statistics are based on the part of the dungeon they spawn in, and
            should stop spawning when the player gets to the point that they
            pose no threat.

            Elite: A more powerful version of the base monster, encountered in
            the endgame. Elite monsters should all have approximately equivlent
            stats (with some spread to keep the player on their toes),
            and rely on their gimmick to pose a threat. This gimmick may be
            an upgraded version of the original monster's gimmick.

            Last One: If you get rid of all members of a single family of
            monster, the player can encounter a "Last One", a special version
            that is as powerful as an unique boss. These monsters have improved
            gimmicks, and are all bright magenta. Last Ones WILL pursue the player
            even if they change floors.

       > All creature families must do something unique. This can include:

            Spawning en-masse.
            Self-destructing.
            Calling for backup.
            Shooting from behind cover.
            Being invisible.
            Using ranged attacks.
            Using ranged splash attacks (note: pair with self-destructing enemeies)
            Cursing player items.
            Causing random things to happen to the player.
            Teleporting the player.
            Teleproting when hit.
            Stealing the player's money and items.
            Hit-And-Run tactics.

        #GOAL: Design and impliment at least one "Family" of monsters.
        #GOAL: Impliment all four types of AI
        #TODO: Design and impliment at least three "Families" of monsters.

    """
    #Stats
    level = 1
    hitPoints = 0
    maxHitPoints = 0

    manaPoints = 0
    maxManaPoints = 0
    carryingCapacity = 24

    willpower = 0 #Max 100

    strength = 0
    dexterity = 0
    intelligence = 0
    wisdom = 0
    constitution = 0
    charisma = 0
    luck = 0

    parts = []
    traits = []
    feats = []
    resistances = []
    unarmedAttackType = []

    owner = None
    AI_StateMachine = None

    def __init__(self,
                level,
                stats = {'strength': 10, 'dexterity': 10, 'intelligence':10, 'wisdom': 10, 'charisma':10, 'luck':10, 'constitution':10},
                parts = [BodyParts.Head(), BodyParts.Hand(), BodyParts.Hand(),
                         BodyParts.Feet(), BodyParts.Legs(), BodyParts.Torso()],
                traits = [],
                feats = [],
                inventory = [],
                resistances = [],
                unarmedAttackType = [Resistance.Blunt, Resistance.Mundane],
                named_character = False,
                ai_Type = "Generic"):
        self.level = level

        self.strength = stats['strength']
        self.dexterity = stats['dexterity']
        self.intelligence = stats['intelligence']
        self.wisdom = stats['wisdom']
        self.charisma = stats['charisma']
        self.luck = stats['luck']
        self.constitution = stats['constitution']

        self.Recalculate_HP_And_MP()
        self.hitPoints = self.maxHitPoints
        self.manaPoints = self.maxManaPoints

        self.feats = feats
        self.parts = parts
        self.traits = traits
        self.resistances = resistances

        self.unarmedAttackType = unarmedAttackType

        self.named_character = named_character

        #self.AI_StateMachine = AI.Generic(self)

    def Recalculate_HP_And_MP(self):
        self.maxHitPoints = self.constitution * self.level
        self.maxManaPoints = self.intelligence * self.level

    def Pick_Up(self,obj):
        if(len(self.owner.inventory) < 26):
            if(obj.item != None):
                obj.owner = self
                self.owner.inventory.append(obj)
                if(obj in GameState.objects):
                   GameState.objects.remove(obj)
            else:
                raise NotAnItemException(obj.name +" is not an Item!")
        else:
            GUI.message("Your inventory is full!")

    def ranged_attack_entity(self, weapons, target):
        pass

    def melee_attack_entity(self, target):
        AttackingWeapons = []
        DefendingArmor = []

        AttackingTypes = []
        DefendingResistances = []

        x = BodyParts.Part()

        for x in self.parts:
            if (isinstance(x,BodyParts.Part)):
                if isinstance(x.currentItem, Equipment.Weapon):
                    AttackingWeapons.append(x.currentItem)

        for x in target.parts:
            if (isinstance(x,BodyParts.Part)):
                if isinstance(BodyParts.Part.currentItem, Equipment.Armor):
                    DefendingArmor.append(x.currentItem)

        """
        if(len(AttackingWeapons) > 0):
            AttackingTypes = [atk for elem in [r for r in [x.attackType for x in AttackingWeapons]] for atk in elem]
        else:
            AttackingTypes = self.unarmedAttackType
        """

        DefendingResistances = [res for elem in [r for r in [x.resistances for x in DefendingArmor]] for res in elem] + target.resistances

        damage = 0
        totalDamage = 0

        totalDefense = 0
        totalDeflectRank = 0
        totalResistanceRank = 0

        arm = Equipment.Armor()

        for arm in DefendingArmor:
            totalDefense += arm.baseDefense

        wep = Equipment.Weapon()
        #Attack with all weapons
        if(len(AttackingWeapons) > 0):
            for wep in AttackingWeapons:
                if(isinstance(wep,Equipment.Weapon)):
                    """
                    Normal Hit:
                    (Dexterity) + BaseHit + 1d100 > (EnemyDexterity + 50) * (1 * DEFLECTION_RANK) + 100
                    > (EnemyDexterity + 50) * (1 * DEFLECTION_RANK)
                    """
                    attackerHit = self.dexterity + wep.baseAttack + random.randrange(1,100)
                    enemyDefence = (target.dexterity + 50.0) * (1.0)

                    #Todo: Implement Weapon Proficency Feats
                    #Todo: Implement Weapon Deflection

                    """
                    Normal Damage:
                    ((STR_RANK*Strength + DEX_RANK*Dexterity) + BaseDamage
                    - MinimumZero(EnemyDefense - Penetration)) * (1 * RESISTANCE_RANK)
                    """

                    if(attackerHit > enemyDefence):
                        tempDamage = (wep.baseDamage + (self.strength * Equipment.StatisticScaleingRank.Get_Rank() + \
                                                                self.dexterity * Equipment.StatisticScaleingRank.Get_Rank()) - \
                                                                (totalDefense))
                        if tempDamage <= 0:
                            tempDamage = 1

                        damage += tempDamage

                        GUI.message(self.owner.name + " attacked " + target.owner.name + " for " + str(int(tempDamage)) + " damage!")
                    else:
                        GUI.message(self.owner.name + " missed the " + target.owner.name + "!")

        #Unarmed Attack
        else:
            attackerHit = self.dexterity + random.randrange(1,100)
            enemyDefence = (target.dexterity + 50.0) * (1.0)

            if(attackerHit > enemyDefence):
                tempDamage = self.strength

                if tempDamage <= 0:
                        tempDamage = 1

                damage += tempDamage
                GUI.message(self.owner.name + " attacked " + target.owner.name + " for " + str(int(tempDamage)) + " damage!")

            else:
                GUI.message(self.owner.name + " missed the " + target.owner.name + "!")

        target.hitPoints -= int(damage)

        if(damage > 0):
            GUI.message(str(int(damage)) + " total!")

        if(target.hitPoints < 0):
            target.die()
        return

    def die(self):
        GUI.message(self.owner.name + " died!")
        self.owner.clearPath()
        GameState.objects.remove(self.owner)
        GameState.objects.insert(0,self.owner)
        self.owner.char = "%"
        self.owner.blocks = False
        self.owner.ai = None
        self.owner.entity = None
        if self == GameState.player.entity:
            GUI.message(self.owner.name + " died!")
            print "Game Over"
            sys.exit()
