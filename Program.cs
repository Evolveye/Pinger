using System;
using System.Collections.Generic;
using System.Net.NetworkInformation;
using System.Timers;

namespace App {
  class Pinger {
    static int MaxStoredJumps = 60 * 10;
    static List<long> Jumps = new List<long>();
    static ConsoleColor InitialColor = Console.ForegroundColor;
    static int ReallyGood = 25;
    static int Good = 120;
    static int Warn = 180;
    static string address;
    static int redrawHelper = 0;

    static int savedConsoleWidth = 0;
    static int savedConsoleHeight = 0;
    static int scopeSize_leftWidth = 5;
    static int scopeSize_bottomHeight = 1;
    static int scopeSize_graphWidth = Console.WindowWidth - scopeSize_leftWidth - 2;
    static int scopeSize_graphHeight = Console.WindowHeight - scopeSize_bottomHeight - 1;

    struct DrawPingData {
      public float Multiplier;
      public long HighestJump;
      public long HighestCellValue;
    }

    static void Main() {
      Console.Clear();
      Console.Write( "\n Podaj adres do pingowania: ");
      address = Console.ReadLine();

      Console.CursorVisible = false;
      Console.Clear();

      Timer timer = new Timer() {
        Enabled = true,
        Interval = 1000
      };
      timer.Elapsed += new ElapsedEventHandler( (obj, e) => {
        TestSizes();
        Drawer();
      } );
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

    static void TestSizes() {
      if ( redrawHelper++ == 0 ||savedConsoleWidth != Console.WindowWidth || savedConsoleHeight != Console.WindowHeight ) {
        Console.Clear();
        CreateScene( scopeSize_leftWidth, scopeSize_bottomHeight );

        redrawHelper = 30;
        savedConsoleWidth = Console.WindowWidth;
        savedConsoleHeight = Console.WindowHeight;
        scopeSize_graphWidth = Console.WindowWidth - scopeSize_leftWidth - 2;
        scopeSize_graphHeight = Console.WindowHeight - scopeSize_bottomHeight - 1;
      }
    }
    static void Drawer() {
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
    }

    static void FillLeftScope( DrawPingData pingData ) {
      float jumps = scopeSize_graphHeight / 5;
      int [] labels = new int[ (int) jumps ];

      for ( int i = 0;  i < jumps;  ++i )
        labels[ i ] = (int) (pingData.HighestCellValue * (jumps - i) / jumps);

      for ( int i = 0;  i < jumps;  ++i ) {
        Console.CursorLeft = 0;
        Console.CursorTop = (int) (scopeSize_graphHeight * i / jumps);
        Console.Write( "" + labels[ i ] );
      }
    }
    static void FillBottomScope( PingReply pingReply, DrawPingData pingData ) {
      long sum = 0;
      Jumps.ForEach( j => sum += j );

      string str = "Adres: " + Untrim( address, 8 )
        + "   Ping: " + Untrim( pingReply.RoundtripTime, 8 )
        + "   Najwyższy: " + Untrim( pingData.HighestJump, 8 )
        // + "   Mnożnik: " + Untrim( pingData.Multiplier, 8 )
        // + "   Graf H: " + Untrim( scopeSize_graphHeight - 2, 8 )
        + "   Średni (" + ((int) (Jumps.Count / 60)) + "m): " + Untrim( sum / Jumps.Count, 8 )
        ;

      Console.CursorLeft = 0;
      Console.CursorTop = Console.WindowHeight - 1;
      Console.ForegroundColor = ConsoleColor.White;
      Console.Write( Untrim( str, Console.WindowWidth - 1 ) );
    }
    static void CreateScene( int leftBarWidth, int bottomBarHeight ) {
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
    }
    static DrawPingData DrawPing( long ping, int x, int y, int width, int height ) {
      int pingWindowHeight = height;
      bool [,] console = new bool[ pingWindowHeight, width ];
      long highestJump = 0;

      Jumps.Insert( 0, ping );

      for ( int i = Jumps.Count - 1;  i > MaxStoredJumps;  --i )
        Jumps.RemoveAt( i );

      for ( int i = Jumps.Count - 1;  i >= 0;  --i )
        if ( Jumps[ i ] > highestJump )
          highestJump = Jumps[ i ];

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

      return new DrawPingData() {
        HighestJump = highestJump,
        Multiplier = multiplier,
        HighestCellValue = pingForMultiplier
      };
    }
  }
}
