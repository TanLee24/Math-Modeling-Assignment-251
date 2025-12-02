import numpy as np
import xml.etree.ElementTree as ET
from typing import List, Optional

class PetriNet:
    def __init__(
        self,
        place_ids: List[str],
        trans_ids: List[str],
        place_names: List[Optional[str]],
        trans_names: List[Optional[str]],
        I: np.ndarray,
        O: np.ndarray,
        M0: np.ndarray
    ):
        self.place_ids = place_ids
        self.trans_ids = trans_ids
        self.place_names = place_names
        self.trans_names = trans_names
        self.I = I
        self.O = O
        self.M0 = M0

    @classmethod
    def from_pnml(cls, filename: str) -> "PetriNet":
        """
        Parses a PNML file to construct a PetriNet instance.
        """
        # 1. XML Parsing Setup
        # Load the XML file into an ElementTree object
        tree = ET.parse(filename)
        # Get the root element of the XML tree
        root = tree.getroot()

        # Define the XML namespace URL for PNML (version 2009)
        ns_url = "http://www.pnml.org/version-2009/grammar/pnml"
        # Create a dictionary to map the 'pnml' prefix to the URL. 
        # This is required for find/findall methods to locate tags correctly.
        ns = {'pnml': ns_url}

        # 2. Extract Raw XML Elements
        # Find all 'place', 'transition', and 'arc' elements anywhere in the document
        places_xml = root.findall(".//pnml:place", ns)
        trans_xml = root.findall(".//pnml:transition", ns)
        arcs_xml = root.findall(".//pnml:arc", ns)

        # 3. Process Places
        place_ids = []
        place_names = []
        m0_list = []
        # Dictionary to map Place ID (string, e.g., "p1") to Matrix Index (int, e.g., 0)
        place_id_to_idx = {}

        # Loop through each place element with its index (0, 1, 2...)
        for idx, p in enumerate(places_xml):
            # Extract the unique 'id' attribute
            pid = p.get('id')
            place_ids.append(pid)
            # Map the string ID to the integer index for later matrix construction
            place_id_to_idx[pid] = idx

            # Extract the name/text tag if it exists
            name_tag = p.find("pnml:name/pnml:text", ns)
            # Store the name text, or None if missing
            place_names.append(name_tag.text if name_tag is not None else None)

            # Extract the initial marking (number of tokens)
            marking_tag = p.find("pnml:initialMarking/pnml:text", ns)
            if marking_tag is not None:
                # If found, convert text to integer
                m0_list.append(int(marking_tag.text))
            else:
                # Default to 0 tokens if not specified
                m0_list.append(0)

        # 4. Process Transitions
        trans_ids = []
        trans_names = []
        # Dictionary to map Transition ID (string, e.g., "t1") to Matrix Index (int, e.g., 0)
        trans_id_to_idx = {}

        # Loop through each transition element with its index
        for idx, t in enumerate(trans_xml):
            tid = t.get('id')
            trans_ids.append(tid)
            # Map the string ID to the integer index
            trans_id_to_idx[tid] = idx

            # Extract the name/text tag
            name_tag = t.find("pnml:name/pnml:text", ns)
            trans_names.append(name_tag.text if name_tag is not None else None)

        # 5. Initialize Matrices (Mathematical Representation)
        num_places = len(place_ids)
        num_trans = len(trans_ids)

        # Create zero-filled matrices for Input (Pre) and Output (Post) incidence matrices.
        # Shape: Rows = Transitions, Columns = Places
        I = np.zeros((num_trans, num_places), dtype=int)
        O = np.zeros((num_trans, num_places), dtype=int)
        # Convert the initial marking list to a numpy array
        M0 = np.array(m0_list, dtype=int)

        # 6. Process Arcs (Connectivity)
        for arc in arcs_xml:
            source = arc.get('source')  # The ID where the arc starts
            target = arc.get('target')  # The ID where the arc ends

            # Case A: Arc from Place -> Transition (Input/Pre-condition arc)
            if source in place_id_to_idx and target in trans_id_to_idx:
                p_idx = place_id_to_idx[source]  # Get column index for Place
                t_idx = trans_id_to_idx[target]  # Get row index for Transition
                # Set value to 1 in Input matrix I
                I[t_idx, p_idx] = 1

            # Case B: Arc from Transition -> Place (Output/Post-condition arc)
            elif source in trans_id_to_idx and target in place_id_to_idx:
                t_idx = trans_id_to_idx[source]  # Get row index for Transition
                p_idx = place_id_to_idx[target]  # Get column index for Place
                # Set value to 1 in Output matrix O
                O[t_idx, p_idx] = 1

        # 7. Return the constructed PetriNet instance
        return cls(place_ids, trans_ids, place_names, trans_names, I, O, M0)
        pass

    def __str__(self) -> str:
        s = []
        s.append("Places: " + str(self.place_ids))
        s.append("Place names: " + str(self.place_names))
        s.append("\nTransitions: " + str(self.trans_ids))
        s.append("Transition names: " + str(self.trans_names))
        s.append("\nI (input) matrix:")
        s.append(str(self.I))
        s.append("\nO (output) matrix:")
        s.append(str(self.O))
        s.append("\nInitial marking M0:")
        s.append(str(self.M0))
        return "\n".join(s)