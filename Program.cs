using System;
using System.Collections.Generic;
using System.Net.NetworkInformation;
using System.Threading;

namespace App {
  class Pinger {
    static List<long> _jumps = new List<long>();

    static void Main(string[] args) {
      Timer timer = new Timer( t => Ping(), null, 1, 1000 );
      Console.ReadKey();
    }

    static void Ping() {
      Ping ping = new Ping();
      PingReply pingReply = ping.Send( "google.com" );
      int different = 3;
      int x = Console.WindowWidth - different; // 25;
      int y = Console.WindowHeight - different; // 5;

      bool [,] console = new bool[ y, x ];
      long highestJump = y * 3;
      float multiplier;

      Console.Clear();

      _jumps.Insert( 0, pingReply.RoundtripTime );
      _jumps.ForEach( jump => {
        if ( jump > highestJump )
          highestJump = jump;
      } );

      multiplier = (float) y / (float) highestJump;

      for ( int i = 0;  i < y;  ++i )
        for ( int j = 0;  j < x;  ++j ) {
          bool cell;

          if ( j < _jumps.Count )
            cell = _jumps[ j ] * multiplier >= i;
          else
            cell = false;

          console[ i, j ] = cell;
        }

      for ( int i = y - 1;  i >= 0;  --i ) {
        Console.Write( "\n" );

        for ( int j = 0;  j < x;  ++j )
          Console.Write( console[ i, j ]  ?  "#"  :  " " );
      }
    }
  }
}
