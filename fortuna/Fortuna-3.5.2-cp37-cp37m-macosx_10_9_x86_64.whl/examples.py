from random import choice

from Fortuna import FlexCat, CumulativeWeightedChoice, distribution_timer


description = """
Example: FlexCat inside a CumulativeWeightedChoice behind a lambda, flick and twist.
Typical treasure table from a massively popular roll playing game.

  d(100)  Treasure Table F
--------------------------------
   1-30   Spell scroll (8th level)
  31-55   Potion of storm giant strength
  56-70   Potion of supreme healing
  71-85   Spell scroll (9th level)
  86-93   Universal solvent
  94-98   Arrow of slaying
  99-100  Sovereign glue
  
"""


get_random_spell = FlexCat({
    "cantrip": (
        "Acid Splash", "Blade Ward", "Chill Touch", "Dancing Lights", "Fire Bolt", "Friends", "Guidance", "Light",
        "Mage Hand", "Mending", "Message", "Minor Illusion", "Poison Spray", "Prestidigitation", "Ray of Frost",
        "Resistance", "Sacred Flame", "Shocking Grasp", "Spare the Dying", "Thaumaturgy", "True Strike",
        "Vicious Mockery",
    ),
    "level_1": (
        "Alarm", "Animal Friendship", "Bane", "Bless", "Burning Hands", "Charm Person", "Chromatic Orb",
        "Color Spray", "Command", "Comprehend Languages", "Create or Destroy Water", "Cure Wounds",
        "Detect Evil and Good", "Detect Magic", "Detect Poison and Disease", "Disguise Self", "Dissonant Whispers",
        "Expeditious Retreat", "Faerie Fire", "False Life", "Feather Fall", "Find Familiar", "Fog Cloud", "Grease",
        "Guiding Bolt", "Healing Word", "Heroism", "Identify", "Illusory Script", "Inflict Wounds", "Jump",
        "Longstrider", "Mage Armor", "Magic Missile", "Protection from Evil and Good", "Purify Food and Drink",
        "Ray of Sickness", "Sanctuary", "Shield", "Shield of Faith", "Silent Image", "Sleep", "Speak with Animals",
        "Tasha's Hideous Laughter", "Tenser's Floating Disk", "Thunderwave", "Unseen Servant", "Witch Bolt",
    ),
    "level_2": (
        "Aid", "Alter Self", "Animal Messenger", "Arcane Lock", "Augury", "Blindness/Deafness", "Blur",
        "Calm Emotions", "Cloud of Daggers", "Continual Flame", "Crown of Madness", "Darkness", "Darkvision",
        "Detect Thoughts", "Enhance Ability", "Enlarge/Reduce", "Enthrall", "Find Traps", "Flaming Sphere",
        "Gentle Repose", "Gust of Wind", "Heat Metal", "Hold Person", "Invisibility", "Knock",
        "Lesser Restoration", "Levitate", "Locate Animals or Plants", "Locate Object", "Magic Mouth",
        "Magic Weapon", "Melf's Acid Arrow", "Mirror Image", "Misty Step", "Nystul's Magic Aura",
        "Phantasmal Force", "Prayer of Healing", "Protection from Poison", "Ray of Enfeeblement",
        "Rope Trick", "Scorching Ray", "See Invisibility", "Shatter", "Silence", "Spider Climb",
        "Spiritual Weapon", "Suggestion", "Warding Bond", "Web", "Zone of Truth",
    ),
    "level_3": (
        "Animate Dead", "Beacon of Hope", "Bestow Curse", "Blink", "Clairvoyance", "Counterspell",
        "Create Food and Water", "Daylight", "Dispel Magic", "Fear", "Feign Death", "Fireball", "Fly",
        "Gaseous Form", "Glyph of Warding", "Haste", "Hypnotic Pattern", "Leomund's Tiny Hut", "Lightning Bolt",
        "Magic Circle", "Major Image", "Mass Healing Word", "Meld into Stone", "Nondetection", "Phantom Steed",
        "Plant Growth", "Protection from Energy", "Remove Curse", "Revivify", "Sending", "Sleet Storm", "Slow",
        "Speak with Dead", "Speak with Plants", "Spirit Guardians", "Stinking Cloud", "Tongues", "Vampiric Touch",
        "Water Breathing", "Water Walk",
    ),
    "level_4": (
        "Arcane Eye", "Banishment", "Blight", "Compulsion", "Confusion", "Conjure Minor Elementals",
        "Control Water", "Death Ward", "Dimension Door", "Divination", "Evard's Black Tentacles", "Fabricate",
        "Faithful Hound", "Fire Shield", "Freedom of Movement", "Greater Invisibility", "Guardian of Faith",
        "Hallucinatory Terrain", "Ice Storm", "Leomund's Secret Chest", "Locate Creature",
        "Mordenkainen's Private Sanctum", "Otiluke's Resilient Sphere", "Phantasmal Killer", "Polymorph",
        "Stone Shape", "Stoneskin", "Wall of Fire",
    ),
    "level_5": (
        "Animate Objects", "Awaken", "Bigby's Hand", "Cloudkill", "Commune Contagion", "Cone of Cold",
        "Conjure Elemental", "Contact Other Plane", "Creation", "Dispel Evil and Good", "Dominate Person", "Dream",
        "Flame Strike", "Geas", "Greater Restoration", "Hallow", "Hold Monster", "Insect Plague", "Legend Lore",
        "Mass Cure Wounds", "Mislead", "Modify Memory", "Passwall", "Planar Binding", "Raise Dead",
        "Rary's Telepathic Bond", "Scrying", "Seeming", "Telekinesis", "Teleportation Circle", "Wall of Force",
        "Wall of Stone",
    ),
    "level_6": (
        "Arcane Gate", "Blade Barrier", "Chain Lightning", "Circle of Death", "Contingency", "Create Undead",
        "Disintegrate", "Drawmij's Instant Summons", "Eyebite", "Find the Path", "Flesh to Stone",
        "Forbiddance", "Harm", "Globe of Invulnerability", "Guards and Wards", "Heal", "Heroes' Feast", "Magic Jar",
        "Mass Suggestion", "Move Earth", "Otiluke's Freezing Sphere", "Otto's Irresistible Dance", "Planar Ally",
        "Programmed Illusion", "Sunbeam", "True Seeing", "Wall of Ice", "Word of Recall",
    ),
    "level_7": (
        "Conjure Celestial", "Delayed Blast", "Divine Word", "Etherealness", "Finger of Death", "Fire Storm",
        "Forcecage", "Mirage Arcane", "Mordenkainen's Magnificent Mansion", "Mordenkainen's Sword", "Plane Shift",
        "Prismatic Spray", "Project Image", "Regenerate", "Resurrection", "Reverse Gravity", "Sequester",
        "Simulacrum", "Symbol", "Teleport",
    ),
    "level_8": (
        "Antimagic Field", "Antipathy/Sympathy", "Clone", "Control Weather", "Demiplane", "Dominate Monster",
        "Earthquake", "Feeblemind", "Glibness", "Holy Aura", "Incendiary Cloud", "Maze", "Mind Blank",
        "Power Word Stun", "Sunburst", "Telepathy", "Trap the Soul",
    ),
    "level_9": (
        "Astral Projection", "Foresight", "Gate", "Imprisonment", "Mass Heal", "Meteor Swarm", "Power Word Heal",
        "Power Word Kill", "Prismatic Wall", "Shapechange", "Time Stop", "True Polymorph", "True Resurrection",
        "Weird", "Wish",
    )
}, key_bias="front_linear", val_bias="flat_uniform")


treasure_table_f = CumulativeWeightedChoice((
    (30, lambda: f"Spell scroll (8th level) {get_random_spell('level_8')}"),
    (55, "Potion of storm giant strength"),
    (70, "Potion of supreme healing"),
    (85, lambda: f"Spell scroll (9th level) {get_random_spell('level_9')}"),
    (93, "Universal solvent"),
    (98, "Arrow of slaying"),
    (100, "Sovereign glue"),
))


if __name__ == "__main__":
    print(description)

    N = 20
    print(f"{N} random selections from treasure_table_f():")

    for _ in range(N):
        print(treasure_table_f())

    print()
    distribution_timer(treasure_table_f)
    level_9_spells = (
        "Astral Projection", "Foresight", "Gate", "Imprisonment", "Mass Heal", "Meteor Swarm", "Power Word Heal",
        "Power Word Kill", "Prismatic Wall", "Shapechange", "Time Stop", "True Polymorph", "True Resurrection",
        "Weird", "Wish",
    )
    distribution_timer(choice, level_9_spells)
    distribution_timer(get_random_spell, 'level_9')
