import sys
import os
import time

# Thêm thư mục cha vào sys.path để nhìn thấy folder 'src'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Parser và Task 2 (để làm chuẩn so sánh)
from src.main import parse_pnml, get_reachable_markings_bfs
# Import Task 3 của bạn
from src.task_3_symbolic import symbolic_reachability

def test_symbolic_reachability():
    # Setup đường dẫn file PNML
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, "large_net.pnml")
    
    print(f"--- Running Task 3 (Symbolic) Test on {input_file} ---")
    
    # 1. Parse PNML
    net = parse_pnml(input_file)
    if not net:
        print("FAILED: Could not parse PNML file.")
        return

    # 2. Chạy Task 2 (Explicit BFS) để lấy kết quả chuẩn (Baseline)
    print("\n[Baseline] Running Task 2 (Explicit BFS)...")
    t0 = time.time()
    bfs_markings, _ = get_reachable_markings_bfs(net)
    bfs_time = time.time() - t0
    bfs_count = len(bfs_markings)
    print(f" -> BFS found {bfs_count} markings in {bfs_time:.4f}s")

    # 3. Chạy Task 3 (Symbolic BDD) của bạn
    print("\n[Target] Running Task 3 (Symbolic BDD)...")
    # Hàm symbolic_reachability trả về: (bdd_root, count, time, nodes)
    # Lưu ý: Đảm bảo hàm của bạn trong src/task_3_symbolic.py trả về đúng thứ tự này
    _, sym_count, sym_time, sym_nodes = symbolic_reachability(net)
    
    print(f" -> Symbolic found {sym_count} markings in {sym_time:.4f}s")
    print(f" -> BDD Nodes created: {sym_nodes}")

    # 4. So sánh và Verify
    print("\n--- Verification ---")
    if sym_count == bfs_count:
        print(f"[PASSED] ✅ Result matches Explicit method ({sym_count} markings).")
        
        # So sánh hiệu năng (Optional)
        if sym_time < bfs_time:
            print(f"🚀 Great! Symbolic is faster by {bfs_time - sym_time:.4f}s")
        else:
            print(f"ℹ️ Note: Symbolic was slower (Normal for small nets due to overhead)")
            
    else:
        print(f"[FAILED] ❌ Mismatch! BFS says {bfs_count}, but Symbolic says {sym_count}.")

if __name__ == "__main__":
    test_symbolic_reachability()