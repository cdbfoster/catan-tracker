**Do you ever wonder**, during a game of Catan, just how mad at God you deserve to be?  The answer is yes.  And now you can find out!

![Sample game](sample_game.png)

Here you can see that Chris, poor sod that he is, is the least blessed player.  The tracker shows that Chris, no doubt atoning for his cosmic transgressions, has received the fewest resources per his holdings on the board.  Sissi, on the other hand, has received the most.  In fact, Sissi's *blessedness* surpasses the **baseline** *blessedness*, which means she's received *more* resources from her holdings than can be reasonably expected in a fair and just universe (in which we do not live); a clear indication of providence.

## How it works

### Player *Blessedness*
The tracker determines a player's metaphysical good graces by recording how many resources they *receive* vs how many resources they are *"owed"*.

On every roll, the amount of resources a player is *"owed"* increases per each of their holdings, by the probability that the roll will match the holding.  Cities count as two holdings, and multiple settlements on the same hex each count individually.

For instance, if a player has a settlement on a 4, 6, and 9, on each roll their amount *"owed"* will increase by:

```
3/36 + 5/36 + 4/36 = 0.3333
```

since each of those terms represent the chance of rolling a 4, 6, or 9, respectively.  If that player had a *city* in the same location, they would be *"owed"* twice as much.

Additionally, on every roll, the amount of resources a player *receives* increases by `1` per each of their holdings that matches the value of the roll.

Player *blessedness* is calculated as `received / "owed"`.  The **baseline** *blessedness* indicator sits at `1.0`, a taunting glimpse into a universe in which everyone gets what they're owed.

### Number *Blessedness*
Any seasoned Catan player knows that reading the ju-ju of the numerical landscape is a major skill of the game.  Number *blessedness* works very similarly to player *blessedness*, but the calculation per number is instead `times rolled / "owed"`.

Numbers that are blessed above `1.0` are hotter than they "should" be, and numbers that are below are colder than they "should" be.