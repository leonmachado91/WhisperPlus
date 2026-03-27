# World Generation Reference

Guide for creating custom world generation, biomes, structures, and terrain modifications.

## World Generator Versions

### V1 (Current - Exploration Mode)

- **Development**: 2016-2020
- **Status**: Available at Early Access launch
- **Limitations**: Barriers when creating more zones and complex biomes
- **Future**: Will eventually stop generating new chunks

### V2 (Future - Orbis)

- **Development**: Since 2021
- **Status**: Under construction, accessible via Gateways
- **Features**: Next-generation world generator
- **Compatibility**: Old V1 worlds remain accessible

## V2 Key Features

### Visual Node Editor (No Coding Required)

- **Live-Reload**: World updates in-game as you edit
- **Visual Workflow**: Build advanced procedural content by linking nodes
- **Same tools** used internally by Hytale team

### What You Can Control

| Feature | Description |
|---------|-------------|
| **Terrain Shape** | Control each biome's terrain independently, transitions blend seamlessly |
| **Material Providers** | Fully control which materials terrain is made of |
| **Props System** | Generate localized content (POIs, vegetation, decorations) |

### Pattern Scanning System

Analyze terrain and place content contextually (e.g., grass only where 10+ blocks of air above).

### Official Biomes Available

All Orbis biomes will be shared. You can view, modify, and mix official content.

**Regions**: Emerald Wilds (Plains), Whisperfrost Frontier (Taiga/Rivers), Howling Sands (Desert/Oases)

### Experimental Feature Packs

- Chaotic Stacked Terrain - Vertical layering
- Underwater Caves - Coral and shipwrecks
- Arches Terrain - Natural stone arches
- Floating Islands - Sky islands theme
- Procedural Rings - Alien worlds

## World Structure

Hytale worlds are organized in:
- **Universes**: Top-level container
- **Worlds**: Individual dimensions
- **Chunks**: 16x16x256 block regions
- **Blocks**: Individual voxels

## Biome Creation

### Basic Biome Definition

Create in `Server/Biomes/`:

```json
{
  "Type": "Biome",
  "Identifier": "mypack:frozen_forest",
  "DisplayName": "Frozen Forest",
  "Temperature": -0.5,
  "Humidity": 0.3,
  "Terrain": {
    "BaseHeight": 64,
    "HeightVariation": 8,
    "SurfaceBlock": "hytale:snow_block",
    "SubsurfaceBlock": "hytale:ice",
    "FillerBlock": "hytale:stone"
  },
  "Features": [
    "mypack:frozen_tree",
    "hytale:ice_spike"
  ],
  "Mobs": [
    { "Entity": "hytale:wolf", "Weight": 10 },
    { "Entity": "hytale:polar_bear", "Weight": 5 }
  ]
}
```

### Biome Properties

| Property | Type | Description |
|----------|------|-------------|
| `Temperature` | float (-1 to 1) | Climate temperature |
| `Humidity` | float (0 to 1) | Moisture level |
| `BaseHeight` | int | Base terrain height |
| `HeightVariation` | int | Height randomization |
| `SurfaceBlock` | string | Top layer block |
| `SubsurfaceBlock` | string | Second layer |
| `FillerBlock` | string | Deep layers |

## Terrain Generation

### Noise-Based Terrain

```json
{
  "Type": "TerrainGenerator",
  "Identifier": "mypack:mountainous",
  "Noise": {
    "Type": "Perlin",
    "Octaves": 4,
    "Persistence": 0.5,
    "Scale": 0.01
  },
  "Layers": [
    {
      "Block": "hytale:grass_block",
      "Depth": 1
    },
    {
      "Block": "hytale:dirt",
      "Depth": 3
    },
    {
      "Block": "hytale:stone",
      "Depth": -1
    }
  ]
}
```

### Noise Types

| Type | Description |
|------|-------------|
| `Perlin` | Smooth, natural terrain |
| `Simplex` | Similar to Perlin, faster |
| `Voronoi` | Cell-based patterns |
| `Ridged` | Mountain ridges |

## Structure Generation

### Structure Definition

Create in `Server/Structures/`:

```json
{
  "Type": "Structure",
  "Identifier": "mypack:abandoned_cabin",
  "Schematic": "Server/Schematics/cabin.nbt",
  "Placement": {
    "Type": "Surface",
    "MinHeight": 60,
    "MaxHeight": 100,
    "Spacing": 32,
    "Separation": 16
  },
  "Biomes": [
    "mypack:frozen_forest",
    "hytale:forest"
  ],
  "Chance": 0.1
}
```

### Placement Types

| Type | Description |
|------|-------------|
| `Surface` | On terrain surface |
| `Underground` | Below ground |
| `Floating` | In the air |
| `Underwater` | Below water level |

### Schematic Files

Schematics are NBT files containing structure data. Export from:
1. In-game structure editor
2. Third-party tools

## Feature Generation

### Tree Feature

```json
{
  "Type": "Feature",
  "Identifier": "mypack:frozen_tree",
  "FeatureType": "Tree",
  "TrunkBlock": "hytale:frozen_wood",
  "LeafBlock": "hytale:frozen_leaves",
  "TrunkHeight": {
    "Min": 4,
    "Max": 7
  },
  "LeafRadius": 2,
  "Decorators": [
    {
      "Type": "Vines",
      "Block": "hytale:icicle",
      "Chance": 0.3
    }
  ]
}
```

### Ore Feature

```json
{
  "Type": "Feature",
  "Identifier": "mypack:mythril_ore",
  "FeatureType": "Ore",
  "Block": "mypack:mythril_ore",
  "Size": 8,
  "MinHeight": 5,
  "MaxHeight": 32,
  "Rarity": 2
}
```

### Scatter Feature

```json
{
  "Type": "Feature",
  "Identifier": "mypack:crystal_cluster",
  "FeatureType": "Scatter",
  "Block": "mypack:crystal",
  "CountPerChunk": {
    "Min": 2,
    "Max": 5
  },
  "Placement": "Surface"
}
```

## Cave Generation

### Cave Carver

```json
{
  "Type": "CaveCarver",
  "Identifier": "mypack:large_caves",
  "Radius": {
    "Min": 3,
    "Max": 8
  },
  "Height": {
    "Min": 10,
    "Max": 50
  },
  "Frequency": 0.02,
  "FloodWithWater": false,
  "FloodLevel": 30
}
```

### Cavern System

```json
{
  "Type": "CavernGenerator",
  "Identifier": "mypack:crystal_caverns",
  "Height": {
    "Min": 5,
    "Max": 30
  },
  "Size": "Large",
  "FloorBlock": "mypack:crystal_floor",
  "WallDecorations": [
    { "Block": "mypack:crystal", "Chance": 0.1 }
  ]
}
```

## Dimension Creation

### Custom Dimension

```json
{
  "Type": "Dimension",
  "Identifier": "mypack:shadow_realm",
  "DisplayName": "Shadow Realm",
  "Generator": "mypack:shadow_generator",
  "Sky": {
    "DayColor": "#1a1a2e",
    "NightColor": "#0e0e16",
    "HasSun": false,
    "HasMoon": true
  },
  "Physics": {
    "Gravity": 0.8,
    "AirResistance": 1.0
  },
  "SpawnBiome": "mypack:shadow_plains"
}
```

## Plugin-Based Generation

### Generator Plugin

```java
public class CustomWorldGenerator extends WorldGenerator {
    
    @Override
    public void generateChunk(ChunkData chunk, Random random) {
        int baseHeight = 64;
        
        for (int x = 0; x < 16; x++) {
            for (int z = 0; z < 16; z++) {
                // Calculate height using noise
                double noise = SimplexNoise.noise2D(
                    (chunk.getX() * 16 + x) * 0.01,
                    (chunk.getZ() * 16 + z) * 0.01
                );
                int height = (int) (baseHeight + noise * 20);
                
                // Set blocks
                for (int y = 0; y < height; y++) {
                    if (y == height - 1) {
                        chunk.setBlock(x, y, z, Blocks.GRASS);
                    } else if (y > height - 4) {
                        chunk.setBlock(x, y, z, Blocks.DIRT);
                    } else {
                        chunk.setBlock(x, y, z, Blocks.STONE);
                    }
                }
            }
        }
    }
    
    @Override
    public void populate(Chunk chunk, Random random) {
        // Add trees, ores, structures after initial generation
        if (random.nextFloat() < 0.02) {
            generateTree(chunk, random);
        }
    }
}
```

### Register Generator

```java
@Override
public void onEnable() {
    WorldGeneratorRegistry.register("mypack:custom", CustomWorldGenerator::new);
}
```

## Portals

### Portal Definition

```json
{
  "Type": "Portal",
  "Identifier": "mypack:shadow_portal",
  "FrameBlock": "mypack:shadow_stone",
  "ActivationItem": "mypack:shadow_key",
  "TargetDimension": "mypack:shadow_realm",
  "Animation": {
    "Particles": "mypack:shadow_particles",
    "Sound": "mypack:portal_open"
  }
}
```

### Portal Plugin

```java
@EventHandler
public void onPortalEnter(PortalEnterEvent event) {
    Player player = event.getPlayer();
    Portal portal = event.getPortal();
    
    if (portal.getId().equals("mypack:shadow_portal")) {
        // Custom teleport logic
        Location destination = calculateDestination(player, portal);
        player.teleport(destination);
        event.setCancelled(true);
    }
}
```

## Performance Optimization

1. **Use chunk-level operations** instead of block-by-block
2. **Cache noise values** for repeated access
3. **Defer structure generation** to populate phase
4. **Use appropriate noise scales** (smaller = faster)
5. **Limit feature density** per chunk

## Debugging World Gen

### Commands

```
/worldgen reload - Reload generation configs
/worldgen test <generator> - Test generator output
/worldgen locate <structure> - Find nearest structure
```

### Visualization

Enable debug mode in server config:
```json
{
  "worldgen": {
    "debug": true,
    "showChunkBorders": true,
    "showBiomeBorders": true
  }
}
```
