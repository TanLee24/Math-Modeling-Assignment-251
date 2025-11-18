import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from collections import deque # [NEW] Cần cho BFS
import os

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
            f"Arcs (P -> T): {self.arcs_pt}\n"
            f"Arcs (T -> P): {self.arcs_tp}\n"
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

    # --- [TASK 2] Thêm hàm Fire Transition ---
    def fire_transition(self, trans_id: str, current_marking: set[str]) -> set[str]:
        """
        Kích hoạt transition và trả về marking mới.
        Công thức: M' = (M \ Preset) U Postset
        """
        if not self.is_enabled(trans_id, current_marking):
            raise ValueError(f"Transition {trans_id} is not enabled!")
            
        preset = self.get_preset(trans_id)
        postset = self.get_postset(trans_id)
        
        # Logic cho 1-safe
        new_marking = current_marking.difference(preset).union(postset)
        return new_marking

# --- [TASK 2] Hàm BFS để tìm Reachable Markings ---
def get_reachable_markings_bfs(net: PetriNet):
    print("--- Starting BFS Reachability Analysis ---")
    
    # Frozenset để lưu được vào set visited (vì set thường không hashable)
    initial_m = frozenset(net.initial_marking)
    
    visited = set()
    queue = deque()
    
    visited.add(initial_m)
    queue.append(initial_m)
    
    edges = [] # Lưu cạnh đồ thị (Source -> Transition -> Target) để debug/vẽ
    
    while queue:
        current_m_frozen = queue.popleft()
        current_m = set(current_m_frozen)
        
        for t in net.transitions:
            if net.is_enabled(t, current_m):
                next_m = net.fire_transition(t, current_m)
                next_m_frozen = frozenset(next_m)
                
                # Lưu lại cạnh chuyển đổi
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
            raise ValueError(f"Consistency Error: Source node '{src}' in arc does not exist.")
        if tgt not in all_nodes:
            raise ValueError(f"Consistency Error: Target node '{tgt}' in arc does not exist.")

    print("Consistency check: OK.")

def parse_pnml(pnml_file: str) -> PetriNet | None:
    print(f"Parsing file: {pnml_file}...")
    
    # Kiểm tra file tồn tại
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

        # Xử lý Namespace
        namespace = ''
        if '}' in root.tag:
            namespace = root.tag.split('}')[0].strip('{')
        ns_map = {'pnml': namespace} if namespace else {}

        # Helper function để tìm với namespace
        def find_all(elem, path):
            if namespace:
                # Thêm prefix pnml: vào mỗi tag trong path
                parts = path.split('/')
                new_parts = [f"pnml:{p}" if p and p != '.' else p for p in parts]
                return elem.findall('/'.join(new_parts), ns_map)
            else:
                return elem.findall(path)

        # Parse Places
        for place in find_all(root, './/place'):
            place_id = place.get('id')
            if place_id:
                places.add(place_id)
                # Tìm initialMarking
                marking_node = place.find(f".//{'pnml:' if namespace else ''}initialMarking/{'pnml:' if namespace else ''}text", ns_map)
                if marking_node is not None and marking_node.text:
                     try:
                        if int(marking_node.text) > 0:
                            initial_marking.add(place_id)
                     except: pass

        # Parse Transitions
        for trans in find_all(root, './/transition'):
            trans_id = trans.get('id')
            if trans_id:
                transitions.add(trans_id)

        # Parse Arcs
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

if __name__ == "__main__":
    # Đường dẫn file: giả định chạy từ thư mục gốc (nơi chứa folder src và tests)
    input_file = os.path.join("tests", "petri_net.pnml")
    
    my_petri_net = parse_pnml(input_file)

    if my_petri_net:
        print("\n--- PNML Parsing Successful! ---")
        
        # --- CHẠY TASK 2 ---
        reachable_markings, graph_edges = get_reachable_markings_bfs(my_petri_net)
        
        print("\n--- Reachable Markings (Explicit) ---")
        for idx, m in enumerate(reachable_markings):
            print(f"M{idx}: {set(m)}")
            
        print("\n--- Reachability Graph Edges ---")
        for (src, t, tgt) in graph_edges:
            print(f"{src} --[{t}]--> {tgt}")