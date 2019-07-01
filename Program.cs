using System;
using System.Net.NetworkInformation;
using System.Threading;

namespace App {
  class Program {
    static void Main(string[] args) {
      Timer timer = new Timer( t => _Ping(), null, 1, 1000 );

      Console.ReadKey();
    }

    static void _Ping() {
      Ping ping = new Ping();
      PingReply pingReply = ping.Send( "google.com" );

      Console.WriteLine();
      Console.WriteLine( "Address: " + pingReply.Address );
      Console.WriteLine( "Roundtrip time: " + pingReply.RoundtripTime );
      Console.WriteLine( "TTL (Time To Live): " + pingReply.Options.Ttl );
    }
  }
}
