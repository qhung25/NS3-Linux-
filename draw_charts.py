import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import os

# Hàm dùng chung để đọc dữ liệu từ file XML
def parse_xml(file_path):
    data = {}
    if not os.path.exists(file_path):
        print(f"[!] Không tìm thấy file {file_path}")
        return data
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    for scenario in root.findall('Scenario'):
        name = scenario.get('name')
        times = []
        values = []
        for point in scenario.findall('DataPoint'):
            times.append(float(point.get('time')))
            values.append(float(point.text))
        data[name] = (times, values)
    return data

print("Đang khởi tạo biểu đồ, vui lòng chờ...")

# ==========================================
# 1. Vẽ biểu đồ Case 1 (TCP vs UDP)
# ==========================================
data1 = parse_xml("case1_metrics.xml")
if data1:
    plt.figure(figsize=(10, 5))
    for name, (t, v) in data1.items():
        # Phân loại màu sắc và nhãn dựa trên tên file
        label = "UDP (Không bị HoL Blocking)" if "udp" in name else "TCP (Bị HoL Blocking)"
        color = "green" if "udp" in name else "red"
        plt.plot(t, v, label=label, color=color, linewidth=2, marker='o', markersize=4)
        
    plt.title("Case 1: Tác động của Packet Loss (2%) lên Thông lượng TCP vs UDP", fontsize=14)
    plt.xlabel("Thời gian (giây)", fontsize=12)
    plt.ylabel("Thông lượng (Kbps)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig("case1_chart.png", dpi=300)
    plt.close()
    print("[+] Đã xuất biểu đồ: case1_chart.png")

# ==========================================
# 2. Vẽ biểu đồ Case 2 (Mạng LFN)
# ==========================================
data2 = parse_xml("case2_metrics.xml")
if data2:
    plt.figure(figsize=(10, 5))
    for name, (t, v) in data2.items():
        plt.plot(t, v, label="TCP Reno/Cubic", color="red", linewidth=2)
        
    plt.title("Case 2: Hiện tượng sụt giảm thông lượng TCP trên mạng LFN (RTT 600ms)", fontsize=14)
    plt.xlabel("Thời gian (giây)", fontsize=12)
    plt.ylabel("Thông lượng (Kbps)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig("case2_chart.png", dpi=300)
    plt.close()
    print("[+] Đã xuất biểu đồ: case2_chart.png")

# ==========================================
# 3. Vẽ biểu đồ Case 3 (HTTP/2 vs HTTP/3)
# ==========================================
data3 = parse_xml("case3_metrics.xml")
if data3:
    plt.figure(figsize=(10, 5))
    for name, (t, v) in data3.items():
        label = "HTTP/3 QUIC (0-RTT)" if "quic" in name else "HTTP/2 TCP (3-way Handshake)"
        color = "green" if "quic" in name else "red"
        plt.plot(t, v, label=label, color=color, linewidth=2, marker='s', markersize=5)
        
    plt.title("Case 3: Độ trễ khởi tạo kết nối - HTTP/2 (TCP) vs HTTP/3 (QUIC)", fontsize=14)
    plt.xlabel("Thời gian (giây)", fontsize=12)
    plt.ylabel("Thông lượng (Kbps)", fontsize=12)
    # Giới hạn trục X ở 5 giây đầu tiên để zoom cận cảnh vào khoảng thời gian độ trễ khởi tạo
    plt.xlim(0, 5) 
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig("case3_chart.png", dpi=300)
    plt.close()
    print("[+] Đã xuất biểu đồ: case3_chart.png")
