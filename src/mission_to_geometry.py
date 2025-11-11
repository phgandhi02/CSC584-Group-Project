"""
Translates mission requirements into PCG parameter adjustments.

This ensures the generated geometry actually supports the mission design.
"""

from typing import Any


def adjust_layout_for_mission(
    layout: dict[str, Any], mission: dict[str, Any], algorithm: str
) -> dict[str, Any]:
    """
    Modify layout parameters based on mission requirements.

    This ensures the level geometry actually supports the mission design:
    - Linear missions → longer, more connected paths
    - Exploration missions → more branches and dead-ends
    - Boss fights → ensure large end room
    - Key hunts → ensure separated areas
    """
    mission_type = mission.get("mission_type", "exploration")
    objectives = mission.get("objectives", [])

    # Count objective types
    needs_boss_room = any(obj["objective_type"] == "boss" for obj in objectives)
    needs_dead_ends = any(obj["placement_rule"] == "dead_end" for obj in objectives)
    dead_end_count = sum(
        obj["count"] for obj in objectives if obj["placement_rule"] == "dead_end"
    )
    needs_large_rooms = any(
        obj["placement_rule"] in ["central_room", "checkpoint"] for obj in objectives
    )

    # Create adjusted layout
    adjusted: dict[str, Any] = layout.copy()

    # ===== LINEAR PROGRESSION =====
    if mission_type == "linear_progression":
        if algorithm in ["random_room_placement", "bsp", "hybrid_rooms_caves"]:
            # Fewer, larger rooms with clear connections
            adjusted["max_rooms"] = max(6, layout.get("max_rooms", 10) - 4)
            adjusted["room_size_min"] = max(6, layout.get("room_size_min", 4) + 2)
            adjusted["room_size_max"] = min(18, layout.get("room_size_max", 12) + 4)

            if needs_boss_room:
                # Ensure at least one LARGE room for boss
                adjusted["room_size_max"] = min(20, adjusted["room_size_max"] + 3)

        elif algorithm == "drunkards_walk":
            # More winding for dramatic progression
            adjusted["straight_bias"] = max(0.5, layout.get("straight_bias", 0.7) - 0.2)

            # BOSS FIGHT SPECIAL CASE - need open area at end!
            if needs_boss_room:
                # Much more open for boss arena
                adjusted["target_floor_percent"] = min(
                    0.45, layout.get("target_floor_percent", 0.27) + 0.18
                )
                # Multiple drunkards converging creates larger areas
                adjusted["num_drunkards"] = max(3, layout.get("num_drunkards", 1) + 2)
                # Ensure we get drunkard_params dict
                if "drunkard_params" not in adjusted:
                    adjusted["drunkard_params"] = (
                        layout.get("drunkard_params", {}).copy()
                        if "drunkard_params" in layout
                        else {}
                    )
                # Force smoothing to widen corridors into chambers
                adjusted["drunkard_params"]["smooth"] = True
                adjusted["drunkard_params"]["add_pillars"] = True
                # Start from center so they spread outward
                adjusted["drunkard_params"]["start_pos"] = "center"
            else:
                # Normal progression - keep it interesting
                adjusted["target_floor_percent"] = min(
                    0.30, layout.get("target_floor_percent", 0.27) + 0.03
                )

        elif algorithm == "cellular_automata":
            # Boss needs larger connected spaces, but not one blob
            if "cellular_params" not in adjusted:
                adjusted["cellular_params"] = layout.get("cellular_params", {}).copy()
            params = adjusted["cellular_params"]
            params["initial_wall_probability"] = max(
                0.48, params.get("initial_wall_probability", 0.50) - 0.02
            )
            params["iterations"] = params.get("iterations", 4)  # Keep standard

    # ===== EXPLORATION =====
    elif mission_type == "exploration":
        if algorithm in ["random_room_placement", "bsp", "hybrid_rooms_caves"]:
            # MORE rooms, MORE branches
            adjusted["max_rooms"] = min(25, layout.get("max_rooms", 15) + 5)
            adjusted["room_size_min"] = layout.get("room_size_min", 4)  # Keep varied
            adjusted["room_size_max"] = layout.get("room_size_max", 12)  # Medium rooms

            # If we need dead-ends, ensure more rooms
            if needs_dead_ends:
                adjusted["max_rooms"] = min(30, adjusted["max_rooms"] + dead_end_count)

        elif algorithm == "drunkards_walk":
            # Branching caves with corridors (not too open!)
            adjusted["target_floor_percent"] = min(
                0.30, layout.get("target_floor_percent", 0.27) + 0.03
            )
            adjusted["straight_bias"] = max(
                0.60, layout.get("straight_bias", 0.7) - 0.10
            )

            # Multiple drunkards create branches for treasures
            if "num_drunkards" not in adjusted or adjusted.get("num_drunkards", 1) < 3:
                adjusted["num_drunkards"] = min(4, 2 + (dead_end_count // 2))

        elif algorithm == "cellular_automata":
            # Create NETWORK topology with varied corridors
            if "cellular_params" not in adjusted:
                adjusted["cellular_params"] = layout.get("cellular_params", {}).copy()
            params = adjusted["cellular_params"]
            # Higher walls (0.58) + more iterations = interesting corridors
            params["initial_wall_probability"] = min(
                0.58, params.get("initial_wall_probability", 0.50) + 0.08
            )
            params["iterations"] = min(6, params.get("iterations", 4) + 2)
            # Adjust birth/death for more varied topology
            params["birth_limit"] = 5  # Harder to create walls
            params["death_limit"] = 2  # Easier to remove walls

    # ===== SURVIVAL =====
    elif mission_type == "survival":
        if algorithm in ["random_room_placement", "bsp", "hybrid_rooms_caves"]:
            # Medium number of safe rooms (checkpoints)
            checkpoint_count = sum(
                obj["count"]
                for obj in objectives
                if obj["placement_rule"] == "checkpoint"
            )
            adjusted["max_rooms"] = max(
                8, min(20, layout.get("max_rooms", 12) + checkpoint_count)
            )
            adjusted["room_size_min"] = max(5, layout.get("room_size_min", 4) + 1)

        elif algorithm == "drunkards_walk":
            # Tighter passages for tension
            adjusted["target_floor_percent"] = max(
                0.22, layout.get("target_floor_percent", 0.27) - 0.05
            )
            adjusted["straight_bias"] = min(
                0.85, layout.get("straight_bias", 0.7) + 0.15
            )

        elif algorithm == "cellular_automata":
            # Structured caves with clear chambers for checkpoints
            if "cellular_params" not in adjusted:
                adjusted["cellular_params"] = layout.get("cellular_params", {}).copy()
            params = adjusted["cellular_params"]
            params["initial_wall_probability"] = min(
                0.55, params.get("initial_wall_probability", 0.50) + 0.05
            )
            params["iterations"] = params.get("iterations", 4)

    # ===== KEY HUNT =====
    elif mission_type == "key_hunt":
        key_count = sum(
            obj["count"] for obj in objectives if obj["objective_type"] == "key"
        )

        if algorithm in ["random_room_placement", "bsp", "hybrid_rooms_caves"]:
            # Ensure enough separated areas for keys
            adjusted["max_rooms"] = min(25, layout.get("max_rooms", 15) + key_count * 2)
            adjusted["room_size_min"] = layout.get("room_size_min", 4)
            adjusted["room_size_max"] = max(14, layout.get("room_size_max", 12) + 2)

        elif algorithm == "drunkards_walk":
            # More branching for key locations
            adjusted["num_drunkards"] = min(5, 2 + key_count)
            adjusted["target_floor_percent"] = min(
                0.30, layout.get("target_floor_percent", 0.27) + 0.03
            )

        elif algorithm == "cellular_automata":
            # Separated chambers for keys
            if "cellular_params" not in adjusted:
                adjusted["cellular_params"] = layout.get("cellular_params", {}).copy()
            params = adjusted["cellular_params"]
            params["initial_wall_probability"] = min(
                0.54, params.get("initial_wall_probability", 0.50) + 0.04
            )
            params["iterations"] = params.get("iterations", 4)

    # ===== MULTI OBJECTIVE =====
    elif mission_type == "multi_objective":
        # Balanced approach - enough variety for all objectives
        if algorithm in ["random_room_placement", "bsp", "hybrid_rooms_caves"]:
            adjusted["max_rooms"] = min(22, layout.get("max_rooms", 15) + 3)
            adjusted["room_size_min"] = layout.get("room_size_min", 4)
            adjusted["room_size_max"] = max(14, layout.get("room_size_max", 12) + 2)

        elif algorithm == "drunkards_walk":
            adjusted["target_floor_percent"] = min(
                0.30, layout.get("target_floor_percent", 0.27) + 0.03
            )

        elif algorithm == "cellular_automata":
            # Balanced structure
            if "cellular_params" not in adjusted:
                adjusted["cellular_params"] = layout.get("cellular_params", {}).copy()
            params = adjusted["cellular_params"]
            params["initial_wall_probability"] = min(
                0.53, params.get("initial_wall_probability", 0.50) + 0.03
            )
            params["iterations"] = params.get("iterations", 4)

    # ===== ENSURE BOSS ROOM =====
    if needs_boss_room:
        if algorithm in ["random_room_placement", "bsp", "hybrid_rooms_caves"]:
            # Guarantee at least one very large room
            adjusted["room_size_max"] = max(adjusted.get("room_size_max", 12), 18)

    # ===== ENSURE DEAD ENDS =====
    if needs_dead_ends and algorithm in [
        "random_room_placement",
        "bsp",
        "hybrid_rooms_caves",
    ]:
        # More rooms = more potential dead ends
        adjusted["max_rooms"] = max(adjusted.get("max_rooms", 15), 12 + dead_end_count)

    # ===== ENSURE LARGE ROOMS =====
    if needs_large_rooms and algorithm in [
        "random_room_placement",
        "bsp",
        "hybrid_rooms_caves",
    ]:
        adjusted["room_size_min"] = max(adjusted.get("room_size_min", 4), 6)
        adjusted["room_size_max"] = max(adjusted.get("room_size_max", 12), 14)

    return adjusted


def validate_mission_feasibility(
    layout: dict[str, Any], mission: dict[str, Any]
) -> list[str]:
    """
    Check if the mission objectives can be fulfilled given the layout.
    Returns list of warnings/issues.
    """
    warnings = []
    objectives = mission.get("objectives", [])

    # Count requirements
    total_objectives = sum(obj["count"] for obj in objectives)
    dead_end_needed = sum(
        obj["count"] for obj in objectives if obj["placement_rule"] == "dead_end"
    )

    # Check room-based algorithms
    max_rooms = layout.get("max_rooms", 15)
    if max_rooms < total_objectives:
        warnings.append(
            f"Only {max_rooms} rooms but {total_objectives} objectives - may not all place"
        )

    if dead_end_needed > max_rooms // 2:
        warnings.append(
            f"Need {dead_end_needed} dead-ends but only {max_rooms} rooms - may be insufficient"
        )

    return warnings
