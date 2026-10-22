from scapy.all import rdpcap
import xml.etree.ElementTree as ET
import os

# Hàm tính toán thông lượng (Throughput) theo từng giây
def analyze_throughput(pcap_file):
    throughput = {}
    try:
        packets = rdpcap(pcap_file)
        if not packets:
            return throughput
            
        start_time = float(packets[0].time)
        
        for pkt in packets:
            # Tính mốc thời gian (giây) kể từ lúc bắt đầu
            time_sec = int(float(pkt.time) - start_time)
            length = len(pkt)
            
            if time_sec in throughput:
                throughput[time_sec] += length
            else:
                throughput[time_sec] = length
    except Exception as e:
        print(f"[!] Lỗi khi đọc file {pcap_file}: {e}")
        
    return throughput

# Hàm tạo file XML từ dữ liệu đã phân tích
def export_to_xml(data_dict, output_file):
    root = ET.Element("SimulationMetrics")
    
    for case_name, metrics in data_dict.items():
        case_node = ET.SubElement(root, "Scenario", name=case_name)
        
        for time_sec, bytes_count in sorted(metrics.items()):
            # Chuyển đổi Bytes sang Kilobits per second (Kbps)
            kbps = (bytes_count * 8) / 1000 
            
            point = ET.SubElement(case_node, "DataPoint", time=str(time_sec))
            point.set("unit", "Kbps")
            point.text = f"{kbps:.2f}"
            
    # Ghi ra file
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    # Nhóm các file pcap theo từng Case riêng biệt
    cases_to_analyze = {
        "case1": ["case1-tcp-1-0.pcap", "case1-udp-1-0.pcap"],
        "case2": ["case2-lfn-1-0.pcap"],
        "case3": ["case3-http2-tcp-0-0.pcap", "case3-http3-quic-0-0.pcap"]
    }
    
    print("Đang xử lý dữ liệu, vui lòng chờ...")
    
    # Lặp qua từng Case và xuất ra file XML tương ứng
    for case_name, file_list in cases_to_analyze.items():
        case_metrics = {}
        for f in file_list:
            if os.path.exists(f):
                case_metrics[f] = analyze_throughput(f)
                print(f"[*] Đã phân tích xong: {f}")
            else:
                print(f"[!] Không tìm thấy file: {f}")
                
        # Nếu Case này có dữ liệu, xuất ra file XML riêng
        if case_metrics:
            export_output = f"{case_name}_metrics.xml"
            export_to_xml(case_metrics, export_output)
            print(f"[+] Đã tạo file: {export_output}\n")
