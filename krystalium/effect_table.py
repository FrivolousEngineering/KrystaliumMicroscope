from .types import Color, ParameterModifier

effect_table = {
    "None": {
        "None": []
    },
    "Increasing": {
        "Energy": [
            ParameterModifier("base_movement_speed", 2.0, "mul")
        ],
        "Flesh": [
            ParameterModifier("rbc_spawn_chance", 2.0, "mul"),
            ParameterModifier("wbc_spawn_chance", 2.0, "mul")
        ],
        "Sound": [],
        "Gas": [
            ParameterModifier("rbc_tint", Color(0.25, -0.5, -0.5), "add")
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
            ParameterModifier("plant_spawn_chance", 2.0, "mul")
        ],
        "Solid": [
            ParameterModifier("platelet_spawn_chance", 2.0, "mul")
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
            ParameterModifier("rbc_tint", Color(0.05, 0.15, 0.15), "add")
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
            ParameterModifier("plant_spawn_chance", 0.5, "mul")
        ],
        "Solid": [
            ParameterModifier("platelet_spawn_chance", 0.5, "mul"),
            ParameterModifier("rbc_oval_chance", 1.0, "add")
        ]
    },
    "Creating": {
        "Energy": [
            ParameterModifier("strand_spawn_chance", 1.0, "set"),
            ParameterModifier("strand_tint", Color(.5, 1.0, 2.0), "set_unscaled"),
            ParameterModifier("strand_lifetime", 0.2, "set_unscaled"),
            ParameterModifier("strand_scale", 0.5, "set_unscaled"),
            ParameterModifier("strand_movement", 0.5, "set_unscaled")
        ],
        "Flesh": [
            ParameterModifier("rbc_spawn_chance", 0.5, "add"),
            ParameterModifier("wbc_spawn_chance", 0.5, "add")
        ],
        "Sound": [
            ParameterModifier("base_movement_jitter", 1.0, "add")
        ],
        "Gas": [],
        "Krystal": [
            ParameterModifier("krystal_spawn_chance", 0.1, "add")
        ],
        "Light": [
            ParameterModifier("base_color", Color(7.0, 10.0, 7.0), "set")
        ],
        "Liquid": [
            ParameterModifier("base_movement_speed", 2.0, "mul"),
            ParameterModifier("base_spawn_rate", 0.5, "mul")
        ],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_spawn_chance", 0.25, "add")
        ],
        "Solid": [
            ParameterModifier("strand_spawn_chance", 0.01, "add"),
            ParameterModifier("platelet_spawn_chance", 0.5, "add"),
        ]
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
        "Liquid": [
            ParameterModifier("base_spawn_rate", 0, "set")
        ],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_spawn_chance", 0, "set")
        ],
        "Solid": [
            ParameterModifier("base_spawn_rate", 0, "set")
        ]
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
        "Liquid": [
            ParameterModifier("base_spawn_rate", 2.0, "mul")
        ],
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
        "Gas": [
            ParameterModifier("base_movement_speed", 3.0, "add")
        ],
        "Krystal": [
            ParameterModifier("krystal_scale", -0.5, "add")
        ],
        "Light": [],
        "Liquid": [
            ParameterModifier("base_spawn_rate", 0.5, "mul")
        ],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_scale", -0.5, "add")
        ],
        "Solid": []
    },
    "Fortifying": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("wbc_spawn_chance", 0.5, "add")
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
            ParameterModifier("wbc_spawn_chance", -0.5, "add")
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
        "Gas": [
            ParameterModifier("rbc_movement_multiplier", -0.5, "add")
        ],
        "Krystal": [
            ParameterModifier("krystal_movement_multiplier", 0.5, "add")
        ],
        "Light": [],
        "Liquid": [],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_movement_multiplier", 0.5, "add")
        ],
        "Solid": [
            ParameterModifier("platelet_movement_multiplier", 0.5, "add")
        ]
    },
    "Encumbering": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("base_movement_speed", 0.5, "mul")
        ],
        "Sound": [],
        "Gas": [
            ParameterModifier("rbc_movement_multiplier", 0.5, "add")
        ],
        "Krystal": [
            ParameterModifier("krystal_movement_multiplier", -0.5, "add")
        ],
        "Light": [],
        "Liquid": [],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_movement_multiplier", -0.5, "add")
        ],
        "Solid": [
            ParameterModifier("platelet_movement_multiplier", -0.5, "add")
        ]
    },
    "Cooling": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("base_movement_jitter", -0.5, "add")
        ],
        "Sound": [],
        "Gas": [
            ParameterModifier("rbc_movement_jitter", -0.5, "add")
        ],
        "Krystal": [
            ParameterModifier("krystal_movement_jitter", -0.5, "add")
        ],
        "Light": [],
        "Liquid": [
            ParameterModifier("base_movement_jitter", -0.5, "add")
        ],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_movement_jitter", -0.5, "add")
        ],
        "Solid": [
            ParameterModifier("platelet_movement_jitter", -0.5, "add")
        ]
    },
    "Heating": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("base_movement_jitter", 0.5, "add")
        ],
        "Sound": [],
        "Gas": [
            ParameterModifier("rbc_movement_jitter", 0.5, "add")
        ],
        "Krystal": [
            ParameterModifier("krystal_movement_jitter", 0.5, "add")
        ],
        "Light": [],
        "Liquid": [
            ParameterModifier("base_movement_jitter", 0.5, "add")
        ],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_movement_jitter", 0.5, "add")
        ],
        "Solid": [
            ParameterModifier("platelet_movement_jitter", 0.5, "add")
        ]
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
            ParameterModifier("rbc_tint", Color(0.25, 0.25, 0.25), "add")
        ],
        "Liquid": [
            ParameterModifier("rbc_burr_chance", 1.0, "add"),
            ParameterModifier("rbc_normal_chance", -1.0, "add")
        ],
        "Mind": [],
        "Plant": [],
        "Solid": [
            ParameterModifier("platelet_movement_multiplier", 1.0, "add")
        ]
    },
    "Insulating": {
        "Energy": [],
        "Flesh": [],
        "Sound": [],
        "Gas": [],
        "Krystal": [],
        "Light": [
            ParameterModifier("rbc_tint", Color(-0.25, -0.25, -0.25), "add")
        ],
        "Liquid": [],
        "Mind": [],
        "Plant": [],
        "Solid": [
            ParameterModifier("platelet_movement_multiplier", -1.0, "add"),
            ParameterModifier("rbc_oval_chance", 1.0, "add")
        ]
    },
    "Absorbing": {
        "Energy": [
            ParameterModifier("rbc_burr_chance", 1.0, "add"),
            ParameterModifier("rbc_normal_chance", -1.0, "add")
        ],
        "Flesh": [],
        "Sound": [],
        "Gas": [
            ParameterModifier("rbc_scale", 0.5, "add")
        ],
        "Krystal": [
            ParameterModifier("rbc_tint", Color(0.0, 0.0, 1.0), "add"),
            ParameterModifier("wbc_tint", Color(0.0, 0.0, 1.0), "add")
        ],
        "Light": [],
        "Liquid": [
            ParameterModifier("rbc_scale", 1.0, "add"),
            ParameterModifier("dead_spawn_chance", 0.5, "add")
        ],
        "Mind": [],
        "Plant": [
            ParameterModifier("base_color", Color(0.0, 0.2, 0.0), "add")
        ],
        "Solid": [
            ParameterModifier("platelet_spawn_chance", 0.5, "add")
        ]
    },
    "Releasing": {
        "Energy": [
            ParameterModifier("strand_spawn_chance", 1.0, "set"),
            ParameterModifier("strand_tint", Color(.5, 1.0, 2.0), "set_unscaled"),
            ParameterModifier("strand_lifetime", 0.2, "set_unscaled"),
            ParameterModifier("strand_scale", 0.2, "set_unscaled"),
            ParameterModifier("strand_movement", 0.5, "set_unscaled")
        ],
        "Flesh": [],
        "Sound": [],
        "Gas": [
            ParameterModifier("rbc_scale", -0.5, "add")
        ],
        "Krystal": [],
        "Light": [],
        "Liquid": [
            ParameterModifier("rbc_burr_chance", 1.0, "add")
        ],
        "Mind": [],
        "Plant": [
            ParameterModifier("plant_tint", Color(0.2, 0.0, 0.2), "add")
        ],
        "Solid": [
            ParameterModifier("platelet_spawn_chance", -0.5, "add"),
            ParameterModifier("rbc_oval_chance", 1.0, "add")
        ]
    },
    "Solidifying": {
        "Energy": [],
        "Flesh": [
            ParameterModifier("strand_spawn_chance", 0.01, "add")
        ],
        "Sound": [],
        "Gas": [
            ParameterModifier("strand_spawn_chance", 0.01, "add")
        ],
        "Krystal": [],
        "Light": [],
        "Liquid": [
            ParameterModifier("strand_spawn_chance", 0.01, "add")
        ],
        "Mind": [],
        "Plant": [
            ParameterModifier("strand_spawn_chance", 0.01, "add"),
            ParameterModifier("strand_tint", Color(-0.2, 0.0, -0.2), "add")
        ],
        "Solid": []
    }
}
