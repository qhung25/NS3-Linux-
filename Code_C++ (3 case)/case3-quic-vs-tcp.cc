#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"

using namespace ns3;

int main (int argc, char *argv[])
{
  NodeContainer nodes;
  nodes.Create (2);

  PointToPointHelper pointToPoint;
  // Cấu hình độ trễ mạng cao (100ms) để thấy rõ độ trễ thiết lập kết nối của TCP
  pointToPoint.SetDeviceAttribute ("DataRate", StringValue ("10Mbps"));
  pointToPoint.SetChannelAttribute ("Delay", StringValue ("100ms"));

  NetDeviceContainer devices;
  devices = pointToPoint.Install (nodes);

  InternetStackHelper stack;
  stack.Install (nodes);
  Ipv4AddressHelper address;
  address.SetBase ("10.1.3.0", "255.255.255.0");
  Ipv4InterfaceContainer interfaces = address.Assign (devices);

  uint16_t tcpPort = 80;
  uint16_t udpPort = 443;

  // 1. Luồng TCP (Mô phỏng HTTP/1.1 hoặc HTTP/2 bị trễ do 3-way handshake)
  BulkSendHelper tcpSource ("ns3::TcpSocketFactory", InetSocketAddress (interfaces.GetAddress (1), tcpPort));
  tcpSource.SetAttribute ("MaxBytes", UintegerValue (50000)); 
  ApplicationContainer tcpApps = tcpSource.Install (nodes.Get (0));
  tcpApps.Start (Seconds (1.0)); // Lệnh bắt đầu gọi lúc 1.0s
  tcpApps.Stop (Seconds (10.0));

  PacketSinkHelper tcpSink ("ns3::TcpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), tcpPort));
  ApplicationContainer tcpSinkApps = tcpSink.Install (nodes.Get (1));
  tcpSinkApps.Start (Seconds (0.0));
  tcpSinkApps.Stop (Seconds (10.0));

  // 2. Luồng UDP (Mô phỏng QUIC/HTTP3 - Truyền dữ liệu ngay lập tức không cần bắt tay)
  UdpClientHelper udpClient (interfaces.GetAddress (1), udpPort);
  udpClient.SetAttribute ("MaxPackets", UintegerValue (50));
  udpClient.SetAttribute ("Interval", TimeValue (Seconds (0.01)));
  udpClient.SetAttribute ("PacketSize", UintegerValue (1000));
  ApplicationContainer udpApps = udpClient.Install (nodes.Get (0));
  udpApps.Start (Seconds (1.0)); // Gọi cùng lúc 1.0s để so sánh
  udpApps.Stop (Seconds (10.0));

  UdpServerHelper udpServer (udpPort);
  ApplicationContainer udpServerApps = udpServer.Install (nodes.Get (1));
  udpServerApps.Start (Seconds (0.0));
  udpServerApps.Stop (Seconds (10.0));

  // Xuất 2 file pcap riêng biệt để so sánh trên Wireshark
  pointToPoint.EnablePcap ("case3-http2-tcp", devices.Get(0), false);
  pointToPoint.EnablePcap ("case3-http3-quic", devices.Get(0), false);

  Simulator::Run ();
  Simulator::Destroy ();
  return 0;
}
