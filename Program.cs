using System;
using System.Collections.Generic;
using System.Net.NetworkInformation;
using System.Threading;

namespace App {
  class Pinger {
    static List<long> Jumps = new List<long>();
    static ConsoleColor InitialColor = Console.ForegroundColor;
    static float Good = 7;
    static float Warn = 15;

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
      long highestJump = 0;

      Console.Clear();

      Jumps.Insert( 0, pingReply.RoundtripTime ); // pingReply.RoundtripTime

      for ( int i = Jumps.Count - 1;  i > x;  --i )
        Jumps.RemoveAt( i );

      Jumps.ForEach( jump => {
        if ( jump > highestJump )
          highestJump = jump;
      } );

      float multiplier = (float) y / highestJump;
      float ping_good = Good * multiplier;
      float ping_warn = Warn * multiplier;

      for ( int i = 0;  i < y;  ++i )
        for ( int j = 0;  j < x;  ++j ) {
          bool cell;

          if ( j < Jumps.Count )
            cell = Jumps[ j ] * multiplier >= i;
          else
            cell = false;

          console[ i, j ] = cell;
        }

      for ( int i = y - 1;  i >= 0;  --i ) {
        Console.Write( "\n" );

        if ( i < ping_good )
          Console.ForegroundColor = ConsoleColor.Green;
        else if ( i < ping_warn )
          Console.ForegroundColor = ConsoleColor.Yellow;
        else
          Console.ForegroundColor = ConsoleColor.Red;

        for ( int j = 0;  j < x;  ++j )
          Console.Write( console[ i, j ]  ?  "#"  :  " " );
      }

      Console.ForegroundColor = ConsoleColor.White;
      Console.Write( "\n"
        + " |Wysokość:" + y
        + " |Ping:" + pingReply.RoundtripTime
        + " |Najwyższy:" + highestJump
        + " |Mnożnik:" + multiplier
        + " |GoodLimit:" + ping_good
        + " |Good:" + Good
        + "\n"
      );
      Console.ForegroundColor = InitialColor;
    }
  }
}
