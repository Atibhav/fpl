from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpBinary, LpStatus, PULP_CBC_CMD
from typing import List, Dict, Any, Optional


POSITION_REQUIREMENTS = {
    'GKP': 2,
    'DEF': 5,
    'MID': 5,
    'FWD': 3
}

POSITION_ORDER = list(POSITION_REQUIREMENTS.keys())

MAX_PLAYERS_PER_TEAM = 3
SQUAD_SIZE = 15
DEFAULT_BUDGET = 100.0


def get_position_sort_index(position: str) -> int:
    try:
        return POSITION_ORDER.index(position)
    except ValueError:
        return len(POSITION_ORDER)


def get_player_team(player: Dict[str, Any]) -> str:
    return player.get('team_name') or player.get('team') or 'Unknown'


def normalize_position(position: str) -> str:
    position_aliases = {
        'GK': 'GKP',
        'GKP': 'GKP',
        'DEF': 'DEF',
        'MID': 'MID',
        'FWD': 'FWD',
        'FW': 'FWD',
    }
    return position_aliases.get(position, 'MID')


def optimize_squad(
    players: List[Dict[str, Any]], 
    budget: float = DEFAULT_BUDGET,
    existing_squad: Optional[List[int]] = None,
    max_transfers: Optional[int] = None
) -> Dict[str, Any]:
    
    if not players:
        return {
            'squad': [],
            'total_cost': 0.0,
            'expected_points': 0.0,
            'status': 'No players provided'
        }
    
    prob = LpProblem("FPL_Squad_Optimization", LpMaximize)
    
    valid_players = [p for p in players if p.get('id') is not None]
    if not valid_players:
        return {
            'squad': [],
            'total_cost': 0.0,
            'expected_points': 0.0,
            'status': 'No valid players (missing id field)'
        }
    
    player_ids = [p.get('id') for p in valid_players]
    player_lookup = {p.get('id'): p for p in valid_players}
    
    pick = {pid: LpVariable(f"pick_{pid}", cat=LpBinary) for pid in player_ids}
    
    prob += lpSum(
        player_lookup[pid].get('predicted_points', 0) * pick[pid] 
        for pid in player_ids
    )
    
    prob += lpSum(pick[pid] for pid in player_ids) == SQUAD_SIZE
    
    prob += lpSum(
        player_lookup[pid].get('price', 0) * pick[pid] 
        for pid in player_ids
    ) <= budget
    
    for position, required in POSITION_REQUIREMENTS.items():
        position_players = [
            pid for pid in player_ids 
            if normalize_position(player_lookup[pid].get('position', 'MID')) == position
        ]
        prob += lpSum(pick[pid] for pid in position_players) == required
    
    teams = set(get_player_team(p) for p in valid_players)
    for team in teams:
        team_players = [
            pid for pid in player_ids 
            if get_player_team(player_lookup[pid]) == team
        ]
        prob += lpSum(pick[pid] for pid in team_players) <= MAX_PLAYERS_PER_TEAM
    
    if existing_squad and max_transfers is not None:
        existing_set = set(existing_squad)
        transfers_out = lpSum(
            1 - pick[pid] for pid in player_ids if pid in existing_set
        )
        prob += transfers_out <= max_transfers
    
    solver = PULP_CBC_CMD(msg=0)
    prob.solve(solver)
    
    status = LpStatus[prob.status]
    
    if status != 'Optimal':
        return {
            'squad': [],
            'total_cost': 0.0,
            'expected_points': 0.0,
            'status': f'Optimization failed: {status}'
        }
    
    selected_squad = []
    total_cost = 0.0
    expected_points = 0.0
    
    for pid in player_ids:
        if pick[pid].value() == 1:
            player = player_lookup[pid]
            selected_squad.append(player)
            total_cost += player.get('price', 0)
            expected_points += player.get('predicted_points', 0)
    
    selected_squad.sort(key=lambda p: (
        get_position_sort_index(normalize_position(p.get('position', 'MID'))),
        -p.get('predicted_points', 0)
    ))
    
    return {
        'squad': selected_squad,
        'total_cost': round(total_cost, 1),
        'expected_points': round(expected_points, 2),
        'status': status,
        'budget_remaining': round(budget - total_cost, 1)
    }


def select_starting_eleven(squad: List[Dict[str, Any]]) -> Dict[str, Any]:
    
    if len(squad) != 15:
        starters = squad[:11] if len(squad) >= 11 else squad
        bench = squad[11:15] if len(squad) > 11 else []
        return {
            'starters': starters, 
            'bench': bench, 
            'formation': 'Invalid',
            'expected_points': sum(p.get('predicted_points', 0) for p in starters)
        }
    
    by_position = {pos: [] for pos in POSITION_REQUIREMENTS.keys()}
    for player in squad:
        pos = normalize_position(player.get('position', 'MID'))
        by_position[pos].append(player)
    
    if len(by_position['GKP']) < 2:
        return {
            'starters': squad[:11] if len(squad) >= 11 else squad,
            'bench': squad[11:] if len(squad) > 11 else [],
            'formation': 'Invalid',
            'expected_points': sum(p.get('predicted_points', 0) for p in squad[:11])
        }
    
    for pos in by_position:
        by_position[pos].sort(key=lambda p: -p.get('predicted_points', 0))
    
    starters = []
    bench = []
    
    starters.append(by_position['GKP'][0])
    bench.append(by_position['GKP'][1])
    
    best_formation = None
    best_points = -1
    
    valid_formations = [
        (3, 4, 3), (3, 5, 2), (4, 3, 3), (4, 4, 2), (4, 5, 1), (5, 3, 2), (5, 4, 1)
    ]
    
    for num_def, num_mid, num_fwd in valid_formations:
        if num_def > len(by_position['DEF']) or num_mid > len(by_position['MID']) or num_fwd > len(by_position['FWD']):
            continue
        
        formation_points = (
            sum(p.get('predicted_points', 0) for p in by_position['DEF'][:num_def]) +
            sum(p.get('predicted_points', 0) for p in by_position['MID'][:num_mid]) +
            sum(p.get('predicted_points', 0) for p in by_position['FWD'][:num_fwd])
        )
        
        if formation_points > best_points:
            best_points = formation_points
            best_formation = (num_def, num_mid, num_fwd)
    
    if best_formation is None:
        best_formation = (4, 4, 2)
    
    num_def, num_mid, num_fwd = best_formation
    
    starters.extend(by_position['DEF'][:num_def])
    starters.extend(by_position['MID'][:num_mid])
    starters.extend(by_position['FWD'][:num_fwd])
    
    bench.extend(by_position['DEF'][num_def:])
    bench.extend(by_position['MID'][num_mid:])
    bench.extend(by_position['FWD'][num_fwd:])
    
    bench.sort(key=lambda p: -p.get('predicted_points', 0))
    
    formation_str = f"{num_def}-{num_mid}-{num_fwd}"
    starter_points = sum(p.get('predicted_points', 0) for p in starters)
    
    return {
        'starters': starters,
        'bench': bench,
        'formation': formation_str,
        'expected_points': round(starter_points, 2)
    }


def optimize_with_starting_eleven(
    players: List[Dict[str, Any]], 
    budget: float = DEFAULT_BUDGET
) -> Dict[str, Any]:
    
    squad_result = optimize_squad(players, budget)
    
    if squad_result['status'] != 'Optimal':
        return squad_result
    
    eleven_result = select_starting_eleven(squad_result['squad'])
    
    return {
        **squad_result,
        'starters': eleven_result.get('starters', []),
        'bench': eleven_result.get('bench', []),
        'formation': eleven_result.get('formation', 'Unknown'),
        'starting_expected_points': eleven_result.get('expected_points', 0.0)
    }
