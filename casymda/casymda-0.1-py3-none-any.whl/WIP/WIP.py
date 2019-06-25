import json

# this class provides the possibility to extract and preserve information from a given model
# the model is expected to consist of CoreComponents
# preserved information: name and entry time of entities for every component ("Work-in-Progress" - WIP)
# information is saved to dict/json
# init_model initializes a model with a given
# TODO: verify wip behavior


def snap_model(model, json_path):
    snap = {}

    snap["time"] = model.env.now

    snap["components"] = {}
    for component in model.modelComponents.values():
        # save contents of every component to json incl. timestamp
        snap["components"][component.name] = {}
        snap["components"][component.name]["entities"] = []
        for entity in component.entities:
            entitySnap = {}
            entitySnap["name"] = entity.name
            entitySnap["timeOfArrival"] = entity.timeOfArrival
            if hasattr(entity, "SPR_processingStartedAt"):
                entitySnap["SPR_processingStartedAt"] = entity.SPR_processingStartedAt
            snap["components"][component.name]["entities"].append(
                entitySnap)

    # save to json
    with open(json_path, "w+") as json_file:
        json.dump(snap, json_file, indent=4)

    print("WIP SNAP AT:   " + str(model.env.now))


def init_model(model_class, json_path, entity_type):
    # returns initialized model incl. environment etc, ready for further processing/execution

    with open(json_path, "r") as json_file:
        snap = json.load(json_file)

    snap_time = snap["time"]
    model = model_class(initial_time=snap_time)

    for component in snap["components"]:
        for entityInfo in snap["components"][component]["entities"]:
            entity = entity_type(model.env, entityInfo["name"])
            entity.timeOfArrival = entityInfo["timeOfArrival"]
            if "SPR_processingStartedAt" in entityInfo:
                entity.SPR_processingStartedAt = entityInfo["SPR_processingStartedAt"]

            model.env.process(
                model.modelComponents[component].wipProcessEntity(entity))

    return model
