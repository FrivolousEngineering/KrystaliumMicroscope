from .types import Color, ParameterModifier

effect_table = {
    "Increasing": {
        "Energy": [
            ParameterModifier("base_movement_speed", 2.0, "mul"),
        ],
        "Flesh": [
            ParameterModifier("rbc_spawn_chance", 2.0, "mul"),
            ParameterModifier("wbc_spawn_chance", 2.0, "mul")
        ],
        "Sound": [],
        "Gas": [
            ParameterModifier("rbc_tint", Color(r = 0.25, g = -0.5, b = -0.5), "add")
        ],
        "Krystal": [
            ParameterModifier("krystal_spawn_chance", 2.0, "mul")
        ],
        "Light": [],
        "Liquid": [
            ParameterModifier("base_movement_speed", 2.0, "mul"),
            ParameterModifier("base_spawn_rate", 0.5, "mul")
        ],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_spawn_rate", 2.0, "mul")
        ],
        "Solid": [
        ]
    },
    "Decreasing": {
        "Energy": [
            ParameterModifier("base_movement_speed", 0.5, "mul")
        ],
        "Flesh": [
            ParameterModifier("rbc_spawn_chance", 0.5, "mul"),
            ParameterModifier("wbc_spawn_chance", 0.5, "mul")
        ],
        "Sound": [],
        "Gas": [
            ParameterModifier("rbc_tint", Color(r = 0.05, g = 0.15, b = 0.15), "add")
        ],
        "Krystal": [
            ParameterModifier("krystal_spawn_chance", 0.5, "mul")
        ],
        "Light": [],
        "Liquid": [
            ParameterModifier("base_movement_speed", 0.5, "mul"),
            ParameterModifier("base_spawn_rate", 2.0, "mul")
        ],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_spawn_rate", 0.5, "mul")
        ],
        "Solid": []
    },
    "Creating": {
        "Energy": [
            ParameterModifier("coagulated_strand_spawn_chance", 1.0, "set"),
            ParameterModifier("coagulated_strand_tint", Color(r = 0.9, g = 1.5, b = 2.0), "set"),
            ParameterModifier("coagulated_strand_lifetime", 1.0, "set")
        ],
        "Flesh": [
            ParameterModifier("rbc_spawn_chance", 0.5, "add"),
            ParameterModifier("wbc_spawn_chance", 0.5, "add")
        ],
        "Sound": [
            ParameterModifier("base_movement_jiggle", 1.0, "add")
        ],
        "Gas": [],
        "Krystal": [
            ParameterModifier("krystal_spawn_chance", 1.0, "add")
        ],
        "Light": [
            ParameterModifier("base_color", Color(r = 7, g = 10, b = 7), "set")
        ],
        "Liquid": [
            ParameterModifier("base_movement_speed", 2.0, "mul"),
            ParameterModifier("base_spawn_rate", 0.5, "mul")
        ],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_spawn_rate", 1.0, "add")
        ],
        "Solid": []
    },
    "Destroying": {
        "Energy": [
            ParameterModifier("base_movement_speed", 0.1, "mul")
        ],
        "Flesh": [
            ParameterModifier("rbc_spawn_chance", -1.0, "add"),
            ParameterModifier("wbc_spawn_chance", -1.0, "add")
        ],
        "Sound": [],
        "Gas": [
            ParameterModifier("rbc_tint", Color(0.10, 0.25, 0.25), "add")
        ],
        "Krystal": [
            ParameterModifier("krystal_spawn_chance", 0, "set")
        ],
        "Light": [],
        "Liquid": [],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_spawn_rate", 0, "set")
        ],
        "Solid": []
    },
    "Expanding": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("base_movement_speed", 2.0, "mul"),
            ParameterModifier("base_spawn_rate", 0.5, "mul")
        ],
        "Sound": [],
        "Gas": [
            ParameterModifier("dead_spawn_chance", 1.0, "add")
        ],
        "Krystal": [
            ParameterModifier("krystal_scale", 0.5, "add")
        ],
        "Light": [],
        "Liquid": [],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_scale", 0.5, "add")
        ],
        "Solid": []
    },
    "Contracting": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("base_movement_speed", 0.5, "mul"),
            ParameterModifier("base_spawn_rate", 2.0, "mul")
        ],
        "Sound": [],
        "Gas": [],
        "Krystal": [
            ParameterModifier("krystal_Scale", -0.5, "add")
        ],
        "Light": [],
        "Liquid": [],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_scale", -0.5, "add")
        ],
        "Solid": []
    },
    "Fortifying": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("wbc_spawn_chance", 1.0, "add")
        ],
        "Sound": [],
        "Gas": [],
        "Krystal": [],
        "Light": [],
        "Liquid": [],
        "Mind": [],
        "Plant": [],
        "Solid": []
    },
    "Deteriorating": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("wbc_spawn_chance", -1.0, "add")
        ],
        "Sound": [],
        "Gas": [],
        "Krystal": [],
        "Light": [],
        "Liquid": [],
        "Mind": [],
        "Plant": [],
        "Solid": []
    },
    "Lightening": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("base_movement_speed", 2.0, "mul")
        ],
        "Sound": [],
        "Gas": [],
        "Krystal": [
            ParameterModifier("krystal_movement_multiplier", 0.5, "add")
        ],
        "Light": [],
        "Liquid": [],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_movement_multiplier", 0.5, "add")
        ],
        "Solid": []
    },
    "Encumbering": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("base_movement_speed", 0.5, "mul")
        ],
        "Sound": [],
        "Gas": [],
        "Krystal": [
            ParameterModifier("krystal_movement_multiplier", -0.5, "add")
        ],
        "Light": [],
        "Liquid": [],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_movement_multiplier", -0.5, "add")
        ],
        "Solid": []
    },
    "Cooling": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("base_movement_jitter", -0.5, "add")
        ],
        "Sound": [],
        "Gas": [],
        "Krystal": [
            ParameterModifier("krystal_movement_jitter", -0.5, "add")
        ],
        "Light": [],
        "Liquid": [],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_movement_jitter", -0.5, "add")
        ],
        "Solid": []
    },
    "Heating": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("base_movement_jitter", 0.5, "add")
        ],
        "Sound": [],
        "Gas": [],
        "Krystal": [
            ParameterModifier("krystal_movement_jitter", 0.5, "add")
        ],
        "Light": [],
        "Liquid": [],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_movement_jitter", 0.5, "add")
        ],
        "Solid": []
    },
    "Conducting": {
        "Energy": [
            ParameterModifier("rbc_burr_chance", 1.0, "add"),
            ParameterModifier("rbc_normal_chance", -1.0, "add")
        ],
        "Flesh": [],
        "Sound": [],
        "Gas": [],
        "Krystal": [],
        "Light": [
            ParameterModifier("rbc_tint", "R+0.25G+0.25B+0.25", "add")
        ],
        "Liquid": [
            ParameterModifier("rbc_burr_chance", 1.0, "add"),
            ParameterModifier("rbc_normal_chance", -1.0, "add")
        ],
        "Mind": [],
        "Plant": [],
        "Solid": []
    },
    "Insulating": {
        "Energy": [],
        "Flesh": [],
        "Sound": [],
        "Gas": [],
        "Krystal": [],
        "Light": [
            ParameterModifier("rbc_tint", Color(r = -0.25, g = -0.25, b = -0.25), "add")
        ],
        "Liquid": [],
        "Mind": [],
        "Plant": [],
        "Solid": []
    },
    "Absorbing": {
        "Energy": [
            ParameterModifier("rbc_burr_chance", 1.0, "add"),
            ParameterModifier("rbc_normal_chance", -1.0, "add")
        ],
        "Flesh": [],
        "Sound": [],
        "Gas": [
            ParameterModifier("rbc_scale", 0.25, "add")
        ],
        "Krystal": [
            ParameterModifier("rbc_tint", Color(r = 0.0, g = 0.0, b = 1.0), "add"),
            ParameterModifier("wbc_tint", Color(r = 0.0, g = 0.0, b = 1.0), "add")
        ],
        "Light": [],
        "Liquid": [],
        "Mind": [],
        "Plant": [],
        "Solid": []
    },
    "Releasing": {
        "Energy": [],
        "Flesh": [],
        "Sound": [],
        "Gas": [
            ParameterModifier("rbc_scale", -0.25, "add")
        ],
        "Krystal": [],
        "Light": [],
        "Liquid": [],
        "Mind": [],
        "Plant": [],
        "Solid": []
    },
    "Solidifying": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("coagulated_strand_spawn_chance", 0.01, "add")
        ],
        "Sound": [],
        "Gas": [
            ParameterModifier("coagulated_strand_spawn_chance", 0.01, "add")
        ],
        "Krystal": [],
        "Light": [],
        "Liquid": [
            ParameterModifier("coagulated_strand_spawn_chance", 0.01, "add")
        ],
        "Mind": [],
        "Plant": [],
        "Solid": []
    }
}
