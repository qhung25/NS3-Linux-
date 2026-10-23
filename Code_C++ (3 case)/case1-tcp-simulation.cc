#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"

using namespace ns3;

// Hàm thủ thuật: Chỉ kích hoạt rớt gói 2% sau khi TCP đã kết nối thành công
void EnableErrorModel(Ptr<NetDevice> device) {
    Ptr<RateErrorModel> em = CreateObject<RateErrorModel>();
    
    // Thêm dòng này để ns-3 hiểu 2% là rớt theo Gói tin (Packet) chứ không phải Byte
    em->SetAttribute("ErrorUnit", StringValue("ERROR_UNIT_PACKET")); 
    
    em->SetAttribute("ErrorRate", DoubleValue(0.02));
    device->SetAttribute("ReceiveErrorModel", PointerValue(em));
}

int main (int argc, char *argv[])
{
// Đổi thuật toán TCP sang BBR (hoặc TcpCubic) để chống lại rớt gói ngẫu nhiên
  Config::SetDefault ("ns3::TcpL4Protocol::SocketType", StringValue ("ns3::TcpBbr"));
  
  // Tăng kích thước bộ đệm nhận và gửi lên 1MB để không bị nghẽn cổ chai cục bộ
  Config::SetDefault ("ns3::TcpSocket::RcvBufSize", UintegerValue (1024 * 1024));
  Config::SetDefault ("ns3::TcpSocket::SndBufSize", UintegerValue (1024 * 1024));
  NodeContainer nodes;
  nodes.Create (2);

  PointToPointHelper pointToPoint;
  pointToPoint.SetDeviceAttribute ("DataRate", StringValue ("10Mbps"));
  pointToPoint.SetChannelAttribute ("Delay", StringValue ("2ms"));

  NetDeviceContainer devices;
  devices = pointToPoint.Install (nodes);

  InternetStackHelper stack;
  stack.Install (nodes);

  Ipv4AddressHelper address;
  address.SetBase ("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer interfaces = address.Assign (devices);

  // Bổ sung định tuyến để chống lỗi kết nối
  Ipv4GlobalRoutingHelper::PopulateRoutingTables();

  uint16_t port = 9;

  BulkSendHelper tcpSource ("ns3::TcpSocketFactory", InetSocketAddress (interfaces.GetAddress (1), port));
  tcpSource.SetAttribute ("MaxBytes", UintegerValue (0));
  ApplicationContainer tcpApps = tcpSource.Install (nodes.Get (0));
  tcpApps.Start (Seconds (1.0));
  tcpApps.Stop (Seconds (60.0));

  PacketSinkHelper tcpSink ("ns3::TcpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), port));
  ApplicationContainer sinkApps = tcpSink.Install (nodes.Get (1));
  sinkApps.Start (Seconds (0.0));
  sinkApps.Stop (Seconds (60.0));

  // Kích hoạt hàm thủ thuật ở giây thứ 2.0
  Simulator::Schedule(Seconds(2.0), &EnableErrorModel, devices.Get(1));

  pointToPoint.EnablePcapAll ("case1-tcp");

  Simulator::Stop (Seconds (60.0));
  Simulator::Run ();
  Simulator::Destroy ();
  return 0;
}
