import xml.etree.ElementTree as ET
import plotly.graph_objects as go
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

print("Đang khởi tạo biểu đồ HTML tương tác, vui lòng chờ...")

# ==========================================
# 1. Vẽ biểu đồ Case 1 (TCP vs UDP)
# ==========================================
data1 = parse_xml("case1_metrics.xml")
if data1:
    fig = go.Figure()
    for name, (t, v) in data1.items():
        label = "UDP (Không bị HoL Blocking)" if "udp" in name else "TCP (Bị HoL Blocking)"
        color = "#00b894" if "udp" in name else "#d63031" # Xanh lục và Đỏ
        fig.add_trace(go.Scatter(x=t, y=v, mode='lines+markers', name=label, line=dict(color=color, width=3)))
        
    fig.update_layout(title="Case 1: Tác động của Packet Loss (2%) lên Thông lượng TCP vs UDP",
                      xaxis_title="Thời gian (giây)", yaxis_title="Thông lượng (Kbps)",
                      template="plotly_white", hovermode="x unified")
    fig.write_html("case1_chart.html")
    print("[+] Đã xuất biểu đồ: case1_chart.html")

# ==========================================
# 2. Vẽ biểu đồ Case 2 (Mạng LFN)
# ==========================================
data2 = parse_xml("case2_metrics.xml")
if data2:
    fig = go.Figure()
    for name, (t, v) in data2.items():
        fig.add_trace(go.Scatter(x=t, y=v, mode='lines', name="TCP Reno/Cubic", line=dict(color="#d63031", width=3)))
        
    fig.update_layout(title="Case 2: Hiện tượng sụt giảm thông lượng TCP trên mạng LFN (RTT 600ms)",
                      xaxis_title="Thời gian (giây)", yaxis_title="Thông lượng (Kbps)",
                      template="plotly_white", hovermode="x unified")
    fig.write_html("case2_chart.html")
    print("[+] Đã xuất biểu đồ: case2_chart.html")

# ==========================================
# 3. Vẽ biểu đồ Case 3 (HTTP/2 vs HTTP/3)
# ==========================================
data3 = parse_xml("case3_metrics.xml")
if data3:
    fig = go.Figure()
    for name, (t, v) in data3.items():
        label = "HTTP/3 QUIC (0-RTT)" if "quic" in name else "HTTP/2 TCP (3-way Handshake)"
        color = "#00b894" if "quic" in name else "#d63031"
        fig.add_trace(go.Scatter(x=t, y=v, mode='lines+markers', name=label, line=dict(color=color, width=3), marker=dict(size=8)))
        
    fig.update_layout(title="Case 3: Độ trễ khởi tạo kết nối - HTTP/2 (TCP) vs HTTP/3 (QUIC)",
                      xaxis_title="Thời gian (giây)", yaxis_title="Thông lượng (Kbps)",
                      template="plotly_white", hovermode="x unified",
                      xaxis=dict(range=[0, 5])) # Zoom vào 5 giây đầu
    fig.write_html("case3_chart.html")
    print("[+] Đã xuất biểu đồ: case3_chart.html")
