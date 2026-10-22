#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"

using namespace ns3;

// Hàm kích hoạt lỗi nhiễu sóng sau khi đã kết nối TCP an toàn
void EnableErrorModel(Ptr<NetDevice> device) {
  Ptr<RateErrorModel> em = CreateObject<RateErrorModel>();
  em->SetAttribute("ErrorRate", DoubleValue(0.0001)); // Tỷ lệ lỗi cực nhỏ nhưng đủ gây giảm tốc
  device->SetAttribute("ReceiveErrorModel", PointerValue(em));
}

int main (int argc, char *argv[])
{
  NodeContainer nodes;
  nodes.Create (2);

  PointToPointHelper pointToPoint;
  // Cấu hình mạng LFN: Băng thông khổng lồ 1 Gbps, RTT 600ms (Độ trễ 1 chiều = 300ms)
  pointToPoint.SetDeviceAttribute ("DataRate", StringValue ("1Gbps"));
  pointToPoint.SetChannelAttribute ("Delay", StringValue ("300ms"));

  NetDeviceContainer devices;
  devices = pointToPoint.Install (nodes);

  InternetStackHelper stack;
  stack.Install (nodes);

  Ipv4AddressHelper address;
  address.SetBase ("10.1.2.0", "255.255.255.0");
  Ipv4InterfaceContainer interfaces = address.Assign (devices);
  Ipv4GlobalRoutingHelper::PopulateRoutingTables();

  uint16_t port = 9;

  // Mô phỏng truyền file 50GB (Truyền liên tục) bằng TCP
  BulkSendHelper tcpSource ("ns3::TcpSocketFactory", InetSocketAddress (interfaces.GetAddress (1), port));
  tcpSource.SetAttribute ("MaxBytes", UintegerValue (0));
  ApplicationContainer tcpApps = tcpSource.Install (nodes.Get (0));
  tcpApps.Start (Seconds (1.0));
  tcpApps.Stop (Seconds (30.0));

  PacketSinkHelper tcpSink ("ns3::TcpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), port));
  ApplicationContainer sinkApps = tcpSink.Install (nodes.Get (1));
  sinkApps.Start (Seconds (0.0));
  sinkApps.Stop (Seconds (30.0));

  // Kích hoạt nhiễu sóng ở giây thứ 5 để thấy rõ tốc độ tụt thảm hại
  Simulator::Schedule(Seconds(5.0), &EnableErrorModel, devices.Get(1));

  // Xuất file pcap
  pointToPoint.EnablePcapAll ("case2-lfn");

  Simulator::Stop (Seconds (30.0));
  Simulator::Run ();
  Simulator::Destroy ();
  return 0;
}
