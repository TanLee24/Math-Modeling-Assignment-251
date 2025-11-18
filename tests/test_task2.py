import sys
import os

# Thêm thư mục cha (thư mục gốc dự án) vào sys.path để Python nhìn thấy folder 'src'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import parse_pnml, get_reachable_markings_bfs

def test_explicit_reachability():
    # Đường dẫn file test nằm cùng thư mục tests
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, "petri_net.pnml")
    
    print(f"--- Running Task 2 Test on {input_file} ---")
    
    # 1. Parse
    net = parse_pnml(input_file)
    if not net:
        print("FAILED: Could not parse PNML file.")
        return

    # 2. Run BFS
    markings, edges = get_reachable_markings_bfs(net)

    # 3. In kết quả
    print("\n--- Reachable Markings Found ---")
    for idx, m in enumerate(markings):
        sorted_m = sorted(list(m)) # Sort để in cho đẹp
        print(f"M{idx}: {sorted_m}")

    print(f"\nTotal Markings: {len(markings)}")
    
    # Kiểm tra kết quả (Dựa trên file petri_net.pnml mẫu)
    if len(markings) == 3:
        print("\n[PASSED] ✅ Test passed successfully!")
    else:
        print(f"\n[FAILED] ❌ Expected 3 markings, but found {len(markings)}.")

if __name__ == "__main__":
    test_explicit_reachability()