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

class Entity:
    #Class containing anything that can move around and fight people.

    """
    Axioms of Entities
        > The player and NPCs follow the same rules of movement, statistics and combat.

        > An Entity consists of a series of "Parts". Typically, the parts are as follows:
            Torso
            ->Head
            -->Left Eye
            -->Right Eye
            -->Mouth
            -->Nose
            ->Left Arm
            ->Right Arm
            ->Left Leg
            ->Right Leg

        > Parts provide "Feats" and "Traits".

            Traits: Abilities that are part of the player's body.
            This is decided at character creation, based on the race (erm,
            species) the player chooses. Humans are assumed to be the baseline.
            It is rare (but not unheard of) for an Entity to change traits.

            Feats: Abilities that have been learned through training and study,
            such as the ability to use magic or wield a sword.
            The player can gain new Feats by leveling up.
            Feats are not "stored" in any part of the entity.
            For lore purposes, they are part of an entity's "Soul".

            Stats: Both feats and traits can provide "Stats", a numerical
            measurement of physical capability. The stats are as follows:

                Hit Points:

                Mana Points:

                Willpower: Used for certain special moves. All classes must have
                at least one willpower-based ability.
                Starts at %0, and goes up to %100.

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


                Strength:
                Dexterity:
                Intelligence:
                Willpower:
                Charisma:

                Speed:

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

       "Boss" creatures
    """
    #Stats
    strength = 0
    dexterity = 0