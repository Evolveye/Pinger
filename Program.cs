using System;
using System.Collections.Generic;
using System.Net.NetworkInformation;
using System.Threading;

namespace App {
  class Pinger {
    static List<long> Jumps = new List<long>();
    static ConsoleColor InitialColor = Console.ForegroundColor;
    static int ReallyGood = 25;
    static int Good = 120;
    static int Warn = 180;
    static string address = "login.p1.worldoftanks.eu";

    // static string row = "═";
    // static string column = "║";
    // static string cornerLT = "╔";
    // static string cornerLB = "╚";
    // static string cornerRT = "╗";
    // static string cornerRB = "╝";

    struct DrawPingData {
      public float Multiplier;
      public long HighestJump;
    }

    static void Main() {
      int scopeSize_leftWidth = 5;
      int scopeSize_bottomHeight = 1;
      int scopeSize_graphWidth = Console.WindowWidth - scopeSize_leftWidth - 2;
      int scopeSize_graphHeight = Console.WindowHeight - scopeSize_bottomHeight - 1;

      CreateScene( scopeSize_leftWidth, scopeSize_bottomHeight );

      Timer timer = new Timer( t => {
        try {
          Ping ping = new Ping();
          PingReply pingReply = ping.Send( address );

          DrawPingData pingData = DrawPing(
            pingReply.RoundtripTime,
            scopeSize_leftWidth + 1,
            0,
            scopeSize_graphWidth,
            scopeSize_graphHeight
          );

          FillLeftScope( pingData );
          FillBottomScope( pingReply, pingData );
        } catch ( Exception ) {}
      }, null, 1, 1000 );

      Console.ReadKey();
    }

    static string Untrim( int num, int length ) => Untrim( "" + num, length );
    static string Untrim( long num, int length ) => Untrim( "" + num, length );
    static string Untrim( float num, int length ) => Untrim( "" + num, length );
    static string Untrim( string str, int length ) {
      for ( int i = str.Length;  i < length;  ++i )
        str += " ";

      return str;
    }

    static void FillLeftScope( DrawPingData pingData ) {

    }
    static void FillBottomScope( PingReply pingReply, DrawPingData pingData ) {
      string str = "Adres: " + Untrim( address, 8 )
        + "   Ping: " + Untrim( pingReply.RoundtripTime, 8 )
        + "   Najwyższy: " + Untrim( pingData.HighestJump, 8 )
        + "   Mnożnik: " + Untrim( pingData.Multiplier, 8 )
        + "   Wysokość: " + Untrim( Console.WindowHeight - 2, 8 )
        ;

      Console.CursorLeft = 0;
      Console.CursorTop = Console.WindowHeight - 1;
      Console.ForegroundColor = ConsoleColor.White;
      Console.Write( Untrim( str, Console.WindowWidth - 1 ) );
    }
    static void CreateScene( int leftBarWidth, int bottomBarHeight ) {
      Console.CursorVisible = false;
      Console.Clear();

      int width = Console.WindowWidth - 1;
      int height = Console.WindowHeight - 1;

      for ( int i = height - bottomBarHeight;  i >= 0;  --i ) {
        Console.CursorLeft = leftBarWidth;
        Console.CursorTop = i;
        Console.Write( "║" );
      }

      Console.CursorLeft = 0;
      Console.CursorTop = height - bottomBarHeight;
      for ( int i = width;  i >= 0;  --i )
        Console.Write( "═" );

      Console.CursorLeft = leftBarWidth;
      Console.CursorTop = height - bottomBarHeight;
      Console.Write( "╩" );


      // for ( int y = 0;  y <= height;  ++y ) {
      //   for ( int x = 0;  x <= width;  ++x )
      //     if ( y == 0 || y == height ) {
      //       if ( x == 0 && y == 0 )
      //         Console.Write( cornerLT );
      //       else if ( x == 0 && y == height )
      //         Console.Write( cornerLB );
      //       else if ( x == width && y == 0 )
      //         Console.Write( cornerRT );
      //       else if ( x == width && y == height )
      //         Console.Write( cornerRB );
      //       else
      //         Console.Write( row );
      //     }
      //     else if ( x == 0 || x == width )
      //       Console.Write( column );
      //     else
      //       Console.Write( " " );
      // }
    }
    static DrawPingData DrawPing( long ping, int x, int y, int width, int height ) {
      int pingWindowHeight = height;
      bool [,] console = new bool[ pingWindowHeight, width ];
      long highestJump = 0;

      Jumps.Insert( 0, ping );

      for ( int i = Jumps.Count - 1;  i > width;  --i )
        Jumps.RemoveAt( i );

      Jumps.ForEach( jump => {
        if ( jump > highestJump )
          highestJump = jump;
      } );

      long pingForMultiplier = highestJump;

      if ( pingForMultiplier < Good )
        pingForMultiplier = Good;

      float multiplier = (float) pingWindowHeight / pingForMultiplier;
      float ping_rGood = ReallyGood * multiplier;
      float ping_good = Good * multiplier;
      float ping_warn = Warn * multiplier;

      for ( int i = 0;  i < pingWindowHeight;  ++i )
        for ( int j = 0;  j < width;  ++j ) {
          bool cell;

          if ( j < Jumps.Count )
            cell = Jumps[ j ] * multiplier >= i;
          else
            cell = false;

          console[ i, j ] = cell;
        }

      string str = "";

      for ( int i = pingWindowHeight - 1, iteration = 0;  i >= 0;  --i, ++iteration ) {
        Console.CursorLeft = x;
        Console.CursorTop = y + iteration;

        if ( i < ping_rGood )
          Console.ForegroundColor = ConsoleColor.Green;
        else if ( i < ping_good )
          Console.ForegroundColor = ConsoleColor.DarkGreen;
        else if ( i < ping_warn )
          Console.ForegroundColor = ConsoleColor.Yellow;
        else
          Console.ForegroundColor = ConsoleColor.Red;

        str = "";

        for ( int j = 0;  j < width;  ++j )
          str += console[ i, j ]  ?  "#"  :  " ";

        Console.Write( str );
      }

      Console.ResetColor();

      return new DrawPingData() { HighestJump=highestJump, Multiplier=multiplier };
    }
  }
}
