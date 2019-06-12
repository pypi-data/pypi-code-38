from panda3d.core import Material


def makeMaterial(
        ambient=(1, 1, 1, 1), diffuse=(1, 1, 1, 1), emission=(0, 0, 0, 1),
        shininess=0.0, specular=(0, 0, 0, 1)):
    m = Material()
    m.setAmbient(ambient)
    m.setDiffuse(diffuse)
    m.setEmission(emission)
    m.setShininess(shininess)
    m.setSpecular(specular)
    return m


BLUE_PLAYER_MATERIAL = makeMaterial(
    diffuse=(0, 0, 0.95, 1),
    specular=(0.1, 0.1, 0.15, 1),
    shininess=12.5,
    ambient=(0, 0, 0.95, 1),
    emission=(0, 0, 0.2, 1),
)

RED_PLAYER_MATERIAL = makeMaterial(
    diffuse=(0.95, 0, 0, 1),
    specular=(0.15, 0.1, 0.1, 1),
    shininess=12.5,
    ambient=(0.95, 0, 0, 1),
    emission=(0.2, 0, 0, 1),
)

ROGUE_PLAYER_MATERIAL = makeMaterial(
    diffuse=(0.7, 0.7, 0.7, 1),
    specular=(0.15, 0.15, 0.15, 1),
    shininess=12.5,
    ambient=(0.7, 0.7, 0.7, 1),
    emission=(0.2, 0.2, 0.2, 1),
)

BLUE_SHOT_MATERIAL = makeMaterial(
    diffuse=(0, 0, 0.95, 1),
    specular=(0.1, 0.1, 0.15, 1),
    shininess=12.5,
    ambient=(0.1, 0.1, 0.1, 1),
    emission=(0.2, 0.2, 0.9, 1),
)

RED_SHOT_MATERIAL = makeMaterial(
    diffuse=(0.95, 0, 0, 1),
    specular=(0.15, 0.1, 0.1, 1),
    shininess=12.5,
    ambient=(0.1, 0.1, 0.1, 1),
    emission=(0.9, 0.2, 0.2, 1),
)

ROGUE_SHOT_MATERIAL = makeMaterial(
    diffuse=(0.7, 0.1, 0.7, 1),
    specular=(0.15, 0.15, 0.15, 1),
    shininess=12.5,
    ambient=(0.1, 0.1, 0.1, 1),
    emission=(0.9, 0.9, 0.2, 1),
)

MINIMAP_SHOT_MATERIAL = makeMaterial(
    diffuse=(0.7, 0.7, 0.1, 1),
    specular=(0.15, 0.15, 0.15, 1),
    shininess=1,
    ambient=(0.1, 0.1, 0.1, 1),
    emission=(0.6, 0.9, 0.1, 1),
)

BLUE_CORE_MATERIAL = makeMaterial(
    diffuse=(0.2, 0.2, 0.64, 1),
    specular=(0.5, 0.5, 0.5, 1),
    shininess=12.5,
    ambient=(0.3, 0.3, 1, 1),
    emission=(0.3, 0.3, 0.75, 1),
)

RED_CORE_MATERIAL = makeMaterial(
    diffuse=(0.64, 0.64, 0.64, 1),
    specular=(0.5, 0.5, 0.5, 1),
    shininess=12.5,
    ambient=(1, 0.3, 0.3, 1),
    emission=(0.75, 0.3, 0.3, 1),
)

NEUTRAL_CORE_MATERIAL = makeMaterial(
    diffuse=(0.2, 0.2, 0.2, 1),
    specular=(0.5, 0.5, 0.5, 1),
    shininess=2,
    ambient=(0.2, 0.2, 0.2, 1),
    emission=(0, 0, 0, 1),
)


def getPlayerMaterial(team):
    if not team:
        return ROGUE_PLAYER_MATERIAL
    if team.id == b'A':
        return BLUE_PLAYER_MATERIAL
    if team.id == b'B':
        return RED_PLAYER_MATERIAL
    return ROGUE_PLAYER_MATERIAL


def getShotMaterial(team):
    if not team:
        return ROGUE_SHOT_MATERIAL
    if team.id == b'A':
        return BLUE_SHOT_MATERIAL
    if team.id == b'B':
        return RED_SHOT_MATERIAL
    return ROGUE_SHOT_MATERIAL


def getMiniMapShotMaterial(team):
    return MINIMAP_SHOT_MATERIAL


def getCoreMaterial(team):
    if not team:
        return NEUTRAL_CORE_MATERIAL
    if team.id == b'A':
        return BLUE_CORE_MATERIAL
    if team.id == b'B':
        return RED_CORE_MATERIAL
    return NEUTRAL_CORE_MATERIAL
