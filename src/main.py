import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

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

def verify_consistency(places: set, transitions: set, all_arc_tuples: list):
    all_nodes = places.union(transitions)

    for (src, tgt) in all_arc_tuples:
        if src not in all_nodes:
            raise ValueError(f"Consistency Error: Source node '{src}' in arc does not exist.")
        if tgt not in all_nodes:
            raise ValueError(f"Consistency Error: Target node '{tgt}' in arc does not exist.")

        if src in places and tgt in places:
            raise ValueError(f"Consistency Error: Invalid P->P arc ({src} -> {tgt}).")
        if src in transitions and tgt in transitions:
            raise ValueError(f"Consistency Error: Invalid T->T arc ({src} -> {tgt}).")

    print("Consistency check: OK.")

def parse_pnml(pnml_file: str) -> PetriNet | None:
    print(f"Parsing file: {pnml_file}...")

    places = set()
    transitions = set()
    arcs_pt = set()
    arcs_tp = set()
    initial_marking = set()
    all_arc_tuples = []

    try:
        tree = ET.parse(pnml_file)
        root = tree.getroot()

        namespace = root.tag.split('}')[0].strip('{')
        ns_map = {'pnml': namespace}

        for place in root.findall('.//pnml:place', ns_map):
            place_id = place.get('id')
            if place_id:
                places.add(place_id)

                marking_node = place.find('.//pnml:initialMarking/pnml:text', ns_map)
                if marking_node is not None:
                    try:
                        if int(marking_node.text) > 0:
                            initial_marking.add(place_id)
                    except (ValueError, TypeError):
                        pass

        for trans in root.findall('.//pnml:transition', ns_map):
            trans_id = trans.get('id')
            if trans_id:
                transitions.add(trans_id)

        for arc in root.findall('.//pnml:arc', ns_map):
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

        net = PetriNet(
            places=places,
            transitions=transitions,
            arcs_pt=arcs_pt,
            arcs_tp=arcs_tp,
            initial_marking=initial_marking
        )
        return net

    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
    except FileNotFoundError:
        print(f"Error: File not found '{pnml_file}'")
    except ValueError as e:
        print(f"Data Error: {e}")
    except Exception as e:
        print(f"An unknown error occurred: {e}")

    return None

if __name__ == "__main__":
    # my_petri_net = parse_pnml('petri_net.pnml')
    my_petri_net = parse_pnml('tests/petri_net.pnml')

    if my_petri_net:
        print("\n--- PNML Parsing Successful! ---")
        print(my_petri_net)