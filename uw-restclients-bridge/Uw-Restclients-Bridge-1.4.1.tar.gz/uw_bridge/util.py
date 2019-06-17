from commonconf import override_settings


fdao_bridge_override = override_settings(RESTCLIENTS_BRIDGE_DAO_CLASS='Mock')
ldao_bridge_override = override_settings(RESTCLIENTS_BRIDGE_DAO_CLASS='Live')
