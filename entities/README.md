# Game Entities & Physics Package

This package manages all actor entities, projectile physics, enemy artificial intelligence, interactive level objects, and player mechanics for **MOMENTUM: Chrono Blade**.

## Files & Purposes

- [`base.py`](file:///C:/Users/moham/Downloads/momentum_game/entities/base.py): Base class `Entity` with position, radius, velocity, smooth sliding wall collision resolvers, and geometric angle helpers.
- [`weapons.py`](file:///C:/Users/moham/Downloads/momentum_game/entities/weapons.py): Kinetic projectile system featuring `Bullet` with ricochet bounce calculations, deflected bullet re-targeting, spinning `Shuriken`, and `TemporalGrenade` with expanding stasis EMP field.
- [`environment.py`](file:///C:/Users/moham/Downloads/momentum_game/entities/environment.py): Interactive world obstacles including solid `Wall`, destructible `DestructibleCrate`, volatile `ExplosiveBarrel`, breakable `GlassWindow`, hackable `SecurityTurret`, and floating pickups (`AmmoPack`, `ChronoCell`).
- [`player.py`](file:///C:/Users/moham/Downloads/momentum_game/entities/player.py): Protagonist controller managing multi-weapon arsenal, Katana light deflect slash, heavy charged blade surge, Chrono Dash with phantom afterimages, and Chrono Focus bullet-time battery.
- [`enemy.py`](file:///C:/Users/moham/Downloads/momentum_game/entities/enemy.py): Complete AI state machine hierarchy supporting Troopers, Shotgun Enforcers, Marksmen, Cyber Ninjas, Shield Wardens, Seeker Drones, and the multi-phase boss `BossChronoWarden`.
- [`__init__.py`](file:///C:/Users/moham/Downloads/momentum_game/entities/__init__.py): Exposes entity classes and combat math.
