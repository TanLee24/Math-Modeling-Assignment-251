import xml.etree.ElementTree as ET
from xml.dom import minidom

def generate_large_pnml(filename="tests/large_net.pnml", num_processes=16):
    """
    Tạo mạng Petri với 'num_processes' luồng chạy song song.
    Mỗi luồng: p_start -> transition -> p_end
    Tổng số trạng thái reachable = 2^num_processes
    Ví dụ: n=14 -> 16,384 states. n=20 -> 1 triệu states (BFS sẽ crash, BDD vẫn chạy tốt).
    """
    root = ET.Element("pnml", xmlns="http://www.pnml.org/version-2009/grammar/pnml")
    net = ET.SubElement(root, "net", id="large_parallel_net", type="http://www.pnml.org/version-2009/grammar/ptnet")
    page = ET.SubElement(net, "page", id="page1")

    print(f"Creating Petri Net with {num_processes} parallel processes...")
    print(f"Estimated Reachable Markings: 2^{num_processes} = {2**num_processes:,}")

    for i in range(num_processes):
        # Place Start (có token)
        p_start = ET.SubElement(page, "place", id=f"p{i}_start")
        ET.SubElement(ET.SubElement(p_start, "name"), "text").text = f"Process {i} Start"
        # Initial Marking = 1
        init_mark = ET.SubElement(p_start, "initialMarking")
        ET.SubElement(init_mark, "text").text = "1"

        # Place End (không có token)
        p_end = ET.SubElement(page, "place", id=f"p{i}_end")
        ET.SubElement(ET.SubElement(p_end, "name"), "text").text = f"Process {i} End"

        # Transition
        trans = ET.SubElement(page, "transition", id=f"t{i}")
        ET.SubElement(ET.SubElement(trans, "name"), "text").text = f"Trans {i}"

        # Arcs
        ET.SubElement(page, "arc", id=f"arc{i}_1", source=f"p{i}_start", target=f"t{i}")
        ET.SubElement(page, "arc", id=f"arc{i}_2", source=f"t{i}", target=f"p{i}_end")

    # Format XML đẹp (Pretty print)
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(xmlstr)
    print(f"Done! File saved to: {filename}")

if __name__ == "__main__":
    # Bạn có thể tăng số này lên 15, 16, 18 để thấy BFS chậm dần
    generate_large_pnml("large_net.pnml", num_processes=16)