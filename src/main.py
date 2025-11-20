import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from collections import deque
import os
from src.task_3_symbolic import symbolic_reachability
@dataclass
class PetriNet:
    places: set[str] = field(default_factory=set)
    transitions: set[str] = field(default_factory=set)
    arcs_pt: set[tuple[str, str]] = field(default_factory=set)
    arcs_tp: set[tuple[str, str]] = field(default_factory=set)
    initial_marking: set[str] = field(default_factory=set)

    def __str__(self):
        return (
            f"--- Petri Net ---\n"
            f"Places: {self.places}\n"
            f"Transitions: {self.transitions}\n"
            f"Initial Marking (1-safe): {self.initial_marking}\n"
            f"-----------------"
        )

    def get_preset(self, trans_id: str) -> set[str]:
        if trans_id not in self.transitions:
            raise ValueError(f"Transition '{trans_id}' does not exist.")
        preset_places = set()
        for (place, transition) in self.arcs_pt:
            if transition == trans_id:
                preset_places.add(place)
        return preset_places

    def get_postset(self, trans_id: str) -> set[str]:
        if trans_id not in self.transitions:
            raise ValueError(f"Transition '{trans_id}' does not exist.")
        postset_places = set()
        for (transition, place) in self.arcs_tp:
            if transition == trans_id:
                postset_places.add(place)
        return postset_places

    def is_enabled(self, trans_id: str, current_marking: set[str]) -> bool:
        preset = self.get_preset(trans_id)
        if not preset:
            return True
        return preset.issubset(current_marking)

    def fire_transition(self, trans_id: str, current_marking: set[str]) -> set[str]:
        if not self.is_enabled(trans_id, current_marking):
            raise ValueError(f"Transition {trans_id} is not enabled!")
            
        preset = self.get_preset(trans_id)
        postset = self.get_postset(trans_id)
        
        # Logic cho 1-safe
        new_marking = current_marking.difference(preset).union(postset)
        return new_marking

def get_reachable_markings_bfs(net: PetriNet):
    """
    Thuật toán BFS tìm kiếm không gian trạng thái (Task 2).
    Trả về: (Danh sách các marking, Danh sách các cạnh đồ thị)
    """
    print("--- Starting BFS Reachability Analysis ---")
    
    initial_m = frozenset(net.initial_marking)
    visited = set()
    queue = deque()
    
    visited.add(initial_m)
    queue.append(initial_m)
    
    edges = [] 
    
    while queue:
        current_m_frozen = queue.popleft()
        current_m = set(current_m_frozen)
        
        for t in net.transitions:
            if net.is_enabled(t, current_m):
                next_m = net.fire_transition(t, current_m)
                next_m_frozen = frozenset(next_m)
                
                edges.append((set(current_m_frozen), t, next_m))
                
                if next_m_frozen not in visited:
                    visited.add(next_m_frozen)
                    queue.append(next_m_frozen)
                    
    print(f"BFS Completed. Found {len(visited)} reachable markings.")
    return list(visited), edges

def verify_consistency(places: set, transitions: set, all_arc_tuples: list):
    all_nodes = places.union(transitions)
    for (src, tgt) in all_arc_tuples:
        if src not in all_nodes:
            raise ValueError(f"Consistency Error: Node '{src}' or '{tgt}' in arc does not exist.")
    # print("Consistency check: OK.")

def parse_pnml(pnml_file: str) -> PetriNet | None:
    """
    Đọc file PNML và trả về đối tượng PetriNet (Task 1).
    """
    print(f"Parsing file: {pnml_file}...")
    if not os.path.exists(pnml_file):
        print(f"Error: File not found at {os.path.abspath(pnml_file)}")
        return None

    places = set()
    transitions = set()
    arcs_pt = set()
    arcs_tp = set()
    initial_marking = set()
    all_arc_tuples = []

    try:
        tree = ET.parse(pnml_file)
        root = tree.getroot()

        namespace = ''
        if '}' in root.tag:
            namespace = root.tag.split('}')[0].strip('{')
        ns_map = {'pnml': namespace} if namespace else {}

        def find_all(elem, path):
            if namespace:
                parts = path.split('/')
                new_parts = [f"pnml:{p}" if p and p != '.' else p for p in parts]
                return elem.findall('/'.join(new_parts), ns_map)
            else:
                return elem.findall(path)

        for place in find_all(root, './/place'):
            place_id = place.get('id')
            if place_id:
                places.add(place_id)
                marking_node = place.find(f".//{'pnml:' if namespace else ''}initialMarking/{'pnml:' if namespace else ''}text", ns_map)
                if marking_node is not None and marking_node.text:
                     try:
                        if int(marking_node.text) > 0:
                            initial_marking.add(place_id)
                     except: pass

        for trans in find_all(root, './/transition'):
            trans_id = trans.get('id')
            if trans_id:
                transitions.add(trans_id)

        for arc in find_all(root, './/arc'):
            src = arc.get('source')
            tgt = arc.get('target')
            if src and tgt:
                all_arc_tuples.append((src, tgt))

        verify_consistency(places, transitions, all_arc_tuples)

        for (src, tgt) in all_arc_tuples:
            if src in places and tgt in transitions:
                arcs_pt.add((src, tgt))
            elif src in transitions and tgt in places:
                arcs_tp.add((src, tgt))

        return PetriNet(places, transitions, arcs_pt, arcs_tp, initial_marking)

    except Exception as e:
        print(f"Error parsing PNML: {e}")
        return None

# Block main để trống hoặc chỉ pass, để file này có thể import được
if __name__ == "__main__":
    pass