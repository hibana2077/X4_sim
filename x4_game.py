import json
import random
import yaml
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import os

class TerrainType(Enum):
    PLAINS = "plains"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    COAST = "coast"
    DESERT = "desert"

@dataclass
class Territory:
    id: str
    name: str
    terrain_type: TerrainType
    size: int  # 1-5, affects population capacity
    defense_bonus: float  # 0.0-1.0
    resource_multiplier: float  # affects population growth
    population: int
    owner: Optional[str]  # player_id
    neighbors: List[str]  # territory_ids
    
    def get_capacity(self) -> int:
        """Maximum population this territory can hold"""
        base_capacity = self.size * 1000
        terrain_modifier = {
            TerrainType.PLAINS: 1.2,
            TerrainType.FOREST: 1.0,
            TerrainType.MOUNTAIN: 0.7,
            TerrainType.COAST: 1.1,
            TerrainType.DESERT: 0.6
        }
        return int(base_capacity * terrain_modifier[self.terrain_type])
    
    def get_growth_rate(self) -> float:
        """Population growth rate per turn"""
        base_rate = 2.5  # 用戶要求的2/5倍（2.5倍）
        return base_rate * self.resource_multiplier

@dataclass
class Player:
    id: str
    name: str
    color: str
    is_ai: bool
    total_population: int
    territories_owned: List[str]
    last_action: str
    
    def get_total_population(self, game_map: Dict[str, Territory]) -> int:
        """Calculate total population across all owned territories"""
        total = 0
        for territory_id in self.territories_owned:
            if territory_id in game_map:
                total += game_map[territory_id].population
        return total

@dataclass
class GameState:
    turn: int
    max_turns: int
    players: Dict[str, Player]
    territories: Dict[str, Territory]
    game_log: List[str]
    winner: Optional[str]
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'turn': self.turn,
            'max_turns': self.max_turns,
            'players': {pid: asdict(player) for pid, player in self.players.items()},
            'territories': {tid: {**asdict(territory), 'terrain_type': territory.terrain_type.value} 
                          for tid, territory in self.territories.items()},
            'game_log': self.game_log,
            'winner': self.winner
        }

class X4Game:
    def __init__(self, openrouter_api_key: str):
        self.api_key = openrouter_api_key
        self.game_state: Optional[GameState] = None
        
    def create_map(self, size: int = 15) -> Dict[str, Territory]:
        """Create a random map with irregular territories"""
        territories = {}
        
        # Create territories with random properties
        territory_names = [
            "Northlands", "Greenvalley", "Ironpeak", "Goldshore", "Shadowmere",
            "Sunfield", "Frostheim", "Redstone", "Bluewater", "Silverwood",
            "Dragonspine", "Moonhaven", "Stormport", "Wildlands", "Crystalvale"
        ]
        
        for i in range(size):
            terrain = random.choice(list(TerrainType))
            territory = Territory(
                id=f"t{i:02d}",
                name=territory_names[i % len(territory_names)] + f" ({i+1})",
                terrain_type=terrain,
                size=random.randint(1, 5),
                defense_bonus=random.uniform(0.0, 0.5),
                resource_multiplier=random.uniform(0.8, 1.3),
                population=random.randint(100, 500) if i < 4 else 0,  # First 4 have starting population
                owner=None,
                neighbors=[]
            )
            territories[territory.id] = territory
        
        # Create connections (simplified grid-based with some randomness)
        territory_ids = list(territories.keys())
        for i, territory_id in enumerate(territory_ids):
            neighbors = []
            # Connect to 2-4 neighboring territories
            num_neighbors = random.randint(2, 4)
            possible_neighbors = [tid for tid in territory_ids if tid != territory_id]
            neighbors = random.sample(possible_neighbors, min(num_neighbors, len(possible_neighbors)))
            territories[territory_id].neighbors = neighbors
            
            # Make connections bidirectional
            for neighbor_id in neighbors:
                if territory_id not in territories[neighbor_id].neighbors:
                    territories[neighbor_id].neighbors.append(territory_id)
        
        return territories
    
    def create_players(self, num_players: int = 4) -> Dict[str, Player]:
        """Create players (AI and human)"""
        colors = ["🔴", "🔵", "🟢", "🟡", "🟣", "🟠"]
        players = {}
        
        for i in range(num_players):
            player = Player(
                id=f"player_{i}",
                name=f"Player {i+1}",
                color=colors[i % len(colors)],
                is_ai=True,  # All AI for now
                total_population=0,
                territories_owned=[],
                last_action=""
            )
            players[player.id] = player
        
        return players
    
    def initialize_game(self, num_players: int = 4, map_size: int = 15, max_turns: int = 20):
        """Initialize a new game"""
        territories = self.create_map(map_size)
        players = self.create_players(num_players)
        
        # Assign starting territories to players
        starting_territories = [tid for tid, t in territories.items() if t.population > 0]
        for i, player_id in enumerate(players.keys()):
            if i < len(starting_territories):
                territory_id = starting_territories[i]
                territories[territory_id].owner = player_id
                players[player_id].territories_owned.append(territory_id)
        
        self.game_state = GameState(
            turn=1,
            max_turns=max_turns,
            players=players,
            territories=territories,
            game_log=[],
            winner=None
        )
        
        self.log_action("Game initialized!")
        self.save_game_state()
    
    def log_action(self, message: str):
        """Add message to game log"""
        if self.game_state:
            self.game_state.game_log.append(f"Turn {self.game_state.turn}: {message}")
    
    def save_game_state(self):
        """Save current game state to files"""
        if not self.game_state:
            return
            
        # Save as JSON
        with open('/Users/lixuanhao/Desktop/專案/X4_sim/game_state.json', 'w', encoding='utf-8') as f:
            json.dump(self.game_state.to_dict(), f, ensure_ascii=False, indent=2)
        
        # Save as YAML for human readability
        with open('/Users/lixuanhao/Desktop/專案/X4_sim/game_state.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(self.game_state.to_dict(), f, allow_unicode=True, default_flow_style=False)
    
    def get_llm_response(self, prompt: str, player_name: str) -> str:
        """Get response from OpenRouter LLM"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "google/gemini-2.0-flash-lite-001",  # Fast and cost-effective
            "messages": [
                {
                    "role": "system", 
                    "content": f"You are {player_name}, a strategic commander in a territory conquest game. You must make tactical decisions to expand your empire. Be strategic but concise in your responses."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 200
        }
        
        try:
            response = requests.post("https://openrouter.ai/api/v1", 
                                   headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"AI思考中... (Error: {str(e)})"
    
    def get_player_action(self, player: Player) -> Dict:
        """Get action from player (AI or human)"""
        if not player.is_ai:
            # Human player input (simplified for now)
            return {"action": "wait"}
        
        # AI player
        game_info = self.get_game_situation_for_player(player.id)
        prompt = f"""
Current game situation:
{game_info}

Your goal is to expand your territory and population. You can:
1. MOVE population from one territory to attack/reinforce another
2. WAIT to grow population in current territories

Respond with JSON format:
{{"action": "move", "from": "territory_id", "to": "territory_id", "population": number}}
or
{{"action": "wait"}}

Be strategic - consider territory capacity, defense bonuses, and growth potential.
"""
        
        llm_response = self.get_llm_response(prompt, player.name)
        
        try:
            # Try to parse JSON from LLM response
            import re
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                action = json.loads(json_match.group())
                return action
        except:
            pass
        
        # Fallback to simple AI logic
        return self.simple_ai_action(player)
    
    def simple_ai_action(self, player: Player) -> Dict:
        """Simple AI fallback logic"""
        owned_territories = [tid for tid in player.territories_owned 
                           if tid in self.game_state.territories]
        
        if not owned_territories:
            return {"action": "wait"}
        
        # Try to expand to neighboring unoccupied territory
        for territory_id in owned_territories:
            territory = self.game_state.territories[territory_id]
            if territory.population > 200:  # Have enough population to expand
                for neighbor_id in territory.neighbors:
                    neighbor = self.game_state.territories[neighbor_id]
                    if neighbor.owner is None:  # Unoccupied
                        return {
                            "action": "move",
                            "from": territory_id,
                            "to": neighbor_id,
                            "population": territory.population // 2
                        }
        
        return {"action": "wait"}
    
    def get_game_situation_for_player(self, player_id: str) -> str:
        """Get current game situation description for a player"""
        player = self.game_state.players[player_id]
        info = []
        
        info.append(f"=== Turn {self.game_state.turn}/{self.game_state.max_turns} ===")
        info.append(f"You are {player.name} {player.color}")
        
        # Player's territories
        info.append("\nYour territories:")
        for territory_id in player.territories_owned:
            territory = self.game_state.territories[territory_id]
            info.append(f"  {territory.name}: {territory.population} population "
                       f"(capacity: {territory.get_capacity()}, growth: {territory.get_growth_rate():.1f}x)")
        
        # Nearby opportunities
        info.append("\nNearby territories:")
        nearby = set()
        for territory_id in player.territories_owned:
            territory = self.game_state.territories[territory_id]
            for neighbor_id in territory.neighbors:
                if neighbor_id not in player.territories_owned:
                    nearby.add(neighbor_id)
        
        for territory_id in list(nearby)[:5]:  # Show up to 5 nearby territories
            territory = self.game_state.territories[territory_id]
            owner_info = f"owned by {self.game_state.players[territory.owner].name}" if territory.owner else "unoccupied"
            info.append(f"  {territory.name}: {territory.population} population, {owner_info}")
        
        return "\n".join(info)
    
    def execute_action(self, player_id: str, action: Dict):
        """Execute player action"""
        player = self.game_state.players[player_id]
        
        if action.get("action") == "move":
            self.execute_move_action(player_id, action)
        elif action.get("action") == "wait":
            player.last_action = "Waited and focused on growth"
            self.log_action(f"{player.name} chose to wait and grow")
    
    def execute_move_action(self, player_id: str, action: Dict):
        """Execute move/attack action"""
        player = self.game_state.players[player_id]
        from_id = action.get("from")
        to_id = action.get("to")
        population = action.get("population", 0)
        
        # Validate action
        if (from_id not in player.territories_owned or 
            from_id not in self.game_state.territories or
            to_id not in self.game_state.territories):
            player.last_action = "Invalid move attempted"
            return
        
        from_territory = self.game_state.territories[from_id]
        to_territory = self.game_state.territories[to_id]
        
        # Check if territories are connected
        if to_id not in from_territory.neighbors:
            player.last_action = "Tried to move to non-adjacent territory"
            return
        
        # Check if enough population
        if population > from_territory.population or population <= 0:
            player.last_action = "Insufficient population for move"
            return
        
        # Execute move
        from_territory.population -= population
        
        if to_territory.owner is None:
            # Occupy empty territory
            to_territory.owner = player_id
            to_territory.population = population
            player.territories_owned.append(to_id)
            player.last_action = f"Occupied {to_territory.name} with {population} population"
            self.log_action(f"{player.name} occupied {to_territory.name}")
            
        elif to_territory.owner == player_id:
            # Reinforce own territory
            to_territory.population += population
            player.last_action = f"Reinforced {to_territory.name} with {population} population"
            self.log_action(f"{player.name} reinforced {to_territory.name}")
            
        else:
            # Attack enemy territory
            self.resolve_combat(player_id, from_id, to_id, population)
    
    def resolve_combat(self, attacker_id: str, from_id: str, to_id: str, attacking_population: int):
        """Resolve combat between players"""
        attacker = self.game_state.players[attacker_id]
        defender_territory = self.game_state.territories[to_id]
        defender_id = defender_territory.owner
        defender = self.game_state.players[defender_id]
        
        # Calculate combat strength
        attack_strength = attacking_population
        defense_strength = int(defender_territory.population * (1 + defender_territory.defense_bonus))
        
        # Add randomness
        attack_roll = random.uniform(0.8, 1.2)
        defense_roll = random.uniform(0.8, 1.2)
        
        final_attack = int(attack_strength * attack_roll)
        final_defense = int(defense_strength * defense_roll)
        
        if final_attack > final_defense:
            # Attacker wins
            remaining_attackers = final_attack - final_defense
            defender_territory.owner = attacker_id
            defender_territory.population = remaining_attackers
            attacker.territories_owned.append(to_id)
            defender.territories_owned.remove(to_id)
            
            attacker.last_action = f"Successfully conquered {defender_territory.name}!"
            self.log_action(f"{attacker.name} conquered {defender_territory.name} from {defender.name}!")
        else:
            # Defender wins
            remaining_defenders = final_defense - final_attack
            defender_territory.population = remaining_defenders
            
            attacker.last_action = f"Failed to conquer {defender_territory.name}"
            self.log_action(f"{attacker.name} failed to conquer {defender_territory.name}")
    
    def grow_population(self):
        """Grow population in all territories"""
        for territory in self.game_state.territories.values():
            if territory.owner and territory.population > 0:
                growth_rate = territory.get_growth_rate()
                new_population = int(territory.population * growth_rate)
                capacity = territory.get_capacity()
                territory.population = min(new_population, capacity)
    
    def check_victory_conditions(self) -> Optional[str]:
        """Check if any player has won"""
        total_territories = len(self.game_state.territories)
        
        for player_id, player in self.game_state.players.items():
            # Win by controlling 60% of territories
            if len(player.territories_owned) >= total_territories * 0.6:
                return player_id
            
            # Win by having 50% of total population
            total_pop = sum(t.population for t in self.game_state.territories.values())
            player_pop = sum(self.game_state.territories[tid].population 
                           for tid in player.territories_owned 
                           if tid in self.game_state.territories)
            if total_pop > 0 and player_pop >= total_pop * 0.5:
                return player_id
        
        return None
    
    def play_turn(self):
        """Play one turn of the game"""
        if not self.game_state or self.game_state.winner:
            return
        
        self.log_action(f"=== Starting Turn {self.game_state.turn} ===")
        
        # Each player takes an action
        for player_id, player in self.game_state.players.items():
            if player.territories_owned:  # Only active players
                action = self.get_player_action(player)
                self.execute_action(player_id, action)
        
        # Grow population
        self.grow_population()
        
        # Update player stats
        for player_id, player in self.game_state.players.items():
            player.total_population = player.get_total_population(self.game_state.territories)
        
        # Check victory conditions
        winner = self.check_victory_conditions()
        if winner:
            self.game_state.winner = winner
            self.log_action(f"🎉 {self.game_state.players[winner].name} wins the game!")
        
        # Check turn limit
        elif self.game_state.turn >= self.game_state.max_turns:
            # Find winner by most territories
            best_player = max(self.game_state.players.items(), 
                            key=lambda x: len(x[1].territories_owned))
            self.game_state.winner = best_player[0]
            self.log_action(f"🎉 Game ended! {best_player[1].name} wins by territory control!")
        
        self.game_state.turn += 1
        self.save_game_state()
    
    def display_game_state(self):
        """Display current game state in a nice format"""
        if not self.game_state:
            print("No game in progress")
            return
        
        print(f"\n{'='*50}")
        print(f"🎮 X4 Conquest Game - Turn {self.game_state.turn}/{self.game_state.max_turns}")
        print(f"{'='*50}")
        
        # Player status
        print("\n📊 Player Status:")
        for player_id, player in self.game_state.players.items():
            territories_count = len(player.territories_owned)
            total_pop = sum(self.game_state.territories[tid].population 
                           for tid in player.territories_owned 
                           if tid in self.game_state.territories)
            print(f"  {player.color} {player.name}: {territories_count} territories, {total_pop:,} population")
            if player.last_action:
                print(f"    Last action: {player.last_action}")
        
        # Map overview
        print("\n🗺️  Territory Overview:")
        for territory_id, territory in list(self.game_state.territories.items())[:10]:  # Show first 10
            owner_info = ""
            if territory.owner:
                owner = self.game_state.players[territory.owner]
                owner_info = f" ({owner.color} {owner.name})"
            print(f"  {territory.name}: {territory.population:,} pop{owner_info}")
        
        # Recent actions
        print(f"\n📜 Recent Actions:")
        for log_entry in self.game_state.game_log[-5:]:  # Last 5 actions
            print(f"  {log_entry}")
        
        if self.game_state.winner:
            winner = self.game_state.players[self.game_state.winner]
            print(f"\n🏆 GAME OVER! {winner.color} {winner.name} WINS! 🏆")
        
        print(f"\n{'='*50}\n")

if __name__ == "__main__":
    # Example usage
    print("🎮 X4 Conquest Game")
    print("This game requires an OpenRouter API key.")
    print("Set your API key as environment variable: export OPENROUTER_API_KEY='your_key_here'")
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("⚠️  No API key found. Using demo mode (simple AI only).")
        api_key = "demo_key"
    
    game = X4Game(api_key)
    game.initialize_game(num_players=4, map_size=12, max_turns=15)
    
    print("Game initialized! Check game_state.yaml and game_state.json for detailed state.")
    game.display_game_state()
