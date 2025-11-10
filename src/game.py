from pathlib import Path
import json
import locale
from typing import Any

import pygame

from src.pcg_generator import generate_level
from src.renderer import Renderer, TILE_SIZE

class Game:
    """
    Singleton class to manage the DunGen top-down dungeon crawler game.

    A rogue-like game that uses PCG and LLMs to automatically generate levels
    based on the input that a user gives. This object manages the behavior
    related to game logic, rendering, and user input.

    Public methods:
        run(): Manages the game loop after the Game obj is created.

    Attributes:
        _instance: Class attribute to hold the single instance of the class.
    """

    def __init__(self):
        """
        Create singleton instance of the game object. This object handles the
        interface for game logic, rendering, and user input.
        """
        self.cwd: Path = Path.cwd()
        self.x = 120
        self.y = 120
        self.running = True
        self.window = None
        self.clock = None
        self.game_renderer = None

    def run(self):
        self.on_init()
        while self.running:
            self.on_event()
            self.update()
            self.render()
            self.clock.tick(60)
        self.on_cleanup()

    def on_init(self):
        print("=== DunGen: Mission-Driven PCG Roguelike ===")
        print("\nDESCRIBE THE SETTING - The LLM will design a fitting mission!")
        print("\nQuick select (showcases all 6 algorithms):")
        print("  1. Classic dungeon with scattered rooms")
        print("  2. Organized military fortress")
        print("  3. Tight winding maze")
        print("  4. Natural underground cave")
        print("  5. Ancient citadel with hidden tunnels")
        print("  6. Gladiator arena with battle chambers")
        print("\nOr describe your own setting:")
        print("  TIP: Describe the ATMOSPHERE and PLACE!")
        print("  Examples:")
        print("    - 'creepy abandoned tomb with narrow passages'")
        print("    - 'grand cathedral with huge open chambers'")
        print("    - 'twisting natural caverns full of secrets'")
        print("    - 'tight military compound with organized rooms'")
        
        user_input: str = input("\nEnter 1-6 or describe setting (Enter for #1): ").strip()
        
        # Check if numeric choice - designed to showcase all 6 algorithms
        default_prompts = {
            "1": "classic dungeon with scattered rooms",
            "2": "organized military fortress",
            "3": "tight winding maze",
            "4": "natural underground cave",
            "5": "ancient citadel with hidden tunnels",
            "6": "gladiator arena with battle chambers"
        }
        
        user_prompt = default_prompts.get(user_input, user_input)
        
        if user_prompt:
            # Generate config from LLM
            print("\nGenerating level from your description...")
            from src.llm import generate_level_config, DEFAULT_MODEL
            from datetime import datetime
            
            try:
                level_config, log_data = generate_level_config(user_prompt, DEFAULT_MODEL)
                self.config: dict[str, Any] = level_config.model_dump()
                print(f"\nGenerated {self.config['algorithm']} level with {DEFAULT_MODEL}")
                
                # Show mission design (LLM invented this based on setting)
                if 'mission' in self.config:
                    mission = self.config['mission']
                    print(f"\n{'='*60}")
                    print(f"  LLM-DESIGNED MISSION: {mission['mission_type'].upper()}")
                    print(f"{'='*60}")
                    print(f"Based on your setting, the LLM created this mission:")
                    print(f"  {mission['description']}")
                    print(f"\nObjectives to complete:")
                    for i, obj in enumerate(mission['objectives'], 1):
                        obj_name = obj['objective_type'].replace('_', ' ').title()
                        print(f"  {i}. {obj_name} x{obj['count']} - {obj['description']}")
                    print(f"{'='*60}")
                
                # Save logs
                logs_dir = Path("logs")
                logs_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = logs_dir / f"generation_{timestamp}.json"
                
                with open(log_file, "w", encoding="utf-8") as f:
                    json.dump(log_data, f, indent=2)
                print(f"Log saved to: {log_file}")
                
            except Exception as e:
                print(f"Error generating config: {e}")
                print("Loading default config instead...")
                config_file_path = Path.joinpath(Path.cwd(), "jsons", "sample.json")
                with open(config_file_path, "r", encoding=locale.getencoding()) as f:
                    self.config = json.load(f)
        else:
            # Load default config
            print("Loading default config...")
            config_file_path = Path.joinpath(Path.cwd(), "jsons", "sample.json")
            try:
                with open(config_file_path, "r", encoding=locale.getencoding()) as f:
                    self.config = json.load(f)
            except FileNotFoundError:
                print("Error: default config not found!")
                return
            except json.JSONDecodeError:
                print("Error: config file is not valid JSON!")
                return
         # --- 2. Generate Level ---
        try:
            # Adjust layout parameters based on mission (if present)
            if 'mission' in self.config:
                from src.mission_to_geometry import adjust_layout_for_mission
                
                original_layout = self.config['layout'].copy()
                self.config['layout'] = adjust_layout_for_mission(
                    self.config['layout'],
                    self.config['mission'],
                    self.config['algorithm']
                )
                
                print(f"\n{'='*60}")
                print(f"  MISSION-DRIVEN GEOMETRY ADJUSTMENTS")
                print(f"{'='*60}")
                # Show what changed
                changes = []
                for key in self.config['layout']:
                    if key in original_layout and original_layout[key] != self.config['layout'][key]:
                        old_val = original_layout[key]
                        new_val = self.config['layout'][key]
                        if isinstance(old_val, (int, float)) and old_val != 0:
                            pct_change = ((new_val - old_val) / old_val) * 100
                            changes.append(f"  {key}: {old_val} -> {new_val} ({pct_change:+.0f}%)")
                        else:
                            changes.append(f"  {key}: {old_val} -> {new_val}")
                if changes:
                    print("Mission requirements adjusted PCG parameters:")
                    for change in changes:
                        print(change)
                    print("\nThe level geometry now FITS your mission!")
                else:
                    print("Algorithm already optimal for this mission - no changes needed!")
                print(f"{'='*60}")
            
            self.level_grid: list[list[int]] = generate_level(self.config)
            
            # Place mission objectives if mission exists
            if 'mission' in self.config:
                from src.mission_processor import place_objectives
                result = place_objectives(self.level_grid, self.config['mission'])
                
                if 'error' not in result:
                    print(f"\n{'='*60}")
                    print(f"  LEVEL GENERATION COMPLETE!")
                    print(f"{'='*60}")
                    print(f"Map Size: {len(self.level_grid[0])}x{len(self.level_grid)})")
                    print(f"Rooms Found: {result['num_rooms']}")
                    print(f"Starting Position: {result['start_pos']}")
                    print(f"Max Distance from Start: {result['max_distance']} tiles")
                    
                    total_objectives = sum(obj['count'] for obj in self.config['mission']['objectives'])
                    print(f"\nObjectives Placed: {len(result['placements'])}/{total_objectives}")
                    
                    # Group by type
                    from collections import defaultdict
                    by_type = defaultdict(list)
                    for p in result['placements']:
                        by_type[p['objective_type']].append(p['placement_rule'])
                    
                    for obj_type, rules in sorted(by_type.items()):
                        print(f"  - {obj_type.replace('_', ' ').title()}: {len(rules)} placed")
                    
                    print(f"\n*** Mission-optimized level ready! ***")
                    print(f"{'='*60}\n")
                    
                    # Save placement info to config for rendering
                    self.config['objective_placements'] = result['placements']
                    self.config['start_position'] = result['start_pos']
                
        except KeyError as e:
            print(f"Error: Missing key in config JSON: {e}")
            return
        except Exception as e:  # Catch other potential errors during generation
            print(f"Error during level generation: {e}")
            return
        # --- 3. Initialize Pygame and Renderer (AFTER config is loaded) ---
        pygame.init()
        
        map_width: int | float = self.config['layout']['map_width']
        map_height: int | float = self.config['layout']['map_height']
        screen_width: int | float = map_width * TILE_SIZE
        screen_height: int | float = map_height * TILE_SIZE

        self.game_renderer = Renderer(int(screen_width), int(screen_height))
        self.window = self.game_renderer.screen
        
        # Set icon and caption
        icon_path: Path = self.cwd / "assets" / "icon.png"
        pygame.display.set_icon(pygame.image.load(icon_path))
        pygame.display.set_caption("DunGen: A User Driven PCG Game")
        
        self.clock = pygame.time.Clock()
        
        print(f"\nGame window opened: {int(screen_width)}x{int(screen_height)}")
        return 

    def on_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                elif event.key == pygame.K_SPACE:
                    print("Regenerating level...")
                    try:
                        self.level_grid = generate_level(self.config)
                    except Exception as e:
                        print(f"Error during level regeneration: {e}")
                        # Keep the old grid if regeneration fails
                elif event.key == pygame.K_RIGHT:
                    self.x += 8
                elif event.key == pygame.K_LEFT:
                    self.x -= 8
                elif event.key == pygame.K_DOWN:
                    self.y += 8
                elif event.key == pygame.K_UP:
                    self.y -= 8

    def update(self):
        pass

    def render(self):
        # self.window.fill((0, 0, 0))
        # pygame.draw.rect(self.window, (0, 0, 255), (self.x, self.y, 400, 240))
        # pygame.display.update()
        # Drawing
        if not self.running:
            return
        self.game_renderer.draw_level(self.level_grid)
        pygame.display.flip()  # Update the full screen

    def on_cleanup(self):
        """ Quits Pygame. """
        pygame.quit()