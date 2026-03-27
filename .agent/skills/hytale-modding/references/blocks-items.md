# Blocks & Items Reference

Detailed guide for creating custom blocks and items in Hytale packs.

## Block Creation

### Basic Block Structure

Create a JSON file in `Server/Blocks/`:

```json
{
  "Type": "Block",
  "Identifier": "mypack:my_block",
  "DisplayName": "My Custom Block",
  "Category": "Building",
  "Hardness": 1.0,
  "BlastResistance": 1.0,
  "Model": "Common/Models/Blocks/my_block.bbmodel",
  "Texture": "Common/Textures/Blocks/my_block.png"
}
```

### Top-Level Properties

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `TranslationProperties.Name` | string | Translation key for block name | `"server.Example_Block.name"` |
| `MaxStack` | int | Maximum stack size in inventory | `100` |
| `Icon` | path | Path to inventory icon | `"Icons/ItemsGenerated/Example_Block.png"` |
| `Categories` | array | Creative menu categories | `["Blocks.Rocks"]` |
| `PlayerAnimationsId` | string | Animation set when placing | `"Block"` |
| `Set` | string | Block set identifier | `"Rock_Stone"` |

### BlockType Properties

| Property | Type | Description | Values |
|----------|------|-------------|--------|
| `Material` | string | Block material type | `"Solid"`, `"Liquid"`, `"Gas"` |
| `DrawType` | string | Rendering method | `"Cube"`, `"Cross"`, `"Model"` |
| `Group` | string | Block group for behavior | `"Stone"`, `"Wood"`, `"Dirt"` |
| `Flags` | object | Special block flags | `{}` |
| `ParticleColor` | string | Color of break particles | `"#aeae8c"` |
| `BlockSoundSetId` | string | Sound set for interactions | `"Stone"`, `"Wood"`, `"Grass"` |
| `BlockBreakingDecalId` | string | Breaking animation overlay | `"Breaking_Decals_Rock"` |

### Gathering Properties

Defines how the block is harvested (tool type, tool tier, drop table).

### Texture Properties

Different textures per side (for blocks like grass):
```json
{
  "TextureTop": "grass_top.png",
  "TextureSide": "grass_side.png", 
  "TextureBottom": "dirt.png"
}
```

## Block States

### State Change Interactions

Create blocks with toggle behavior (on/off, open/closed):

```json
{
  "Interactions": {
    "Use": {
      "Type": "ChangeState",
      "Changes": {
        "On": "Off",
        "Off": "On"
      }
    }
  },
  "States": {
    "On": {
      "Model": "lamp_on.bbmodel",
      "Luminance": 15
    },
    "Off": {
      "Model": "lamp_off.bbmodel",
      "Luminance": 0
    }
  }
}
```

### Advanced State Features

Add sounds, animations, and particles per state:

```json
{
  "Type": "Block",
  "Identifier": "mypack:lamp",
  "States": {
    "lit": {
      "Type": "Boolean",
      "Default": false
    }
  },
  "Properties": {
    "lit=false": {
      "Luminance": 0,
      "Texture": "Common/Textures/Blocks/lamp_off.png"
    },
    "lit=true": {
      "Luminance": 15,
      "Texture": "Common/Textures/Blocks/lamp_on.png"
    }
  }
}
```

### Block Animations

Create `.blockyanim` files for animated blocks:

```json
{
  "Type": "BlockAnimation",
  "Target": "mypack:animated_block",
  "Frames": [
    { "Texture": "frame1.png", "Duration": 0.1 },
    { "Texture": "frame2.png", "Duration": 0.1 },
    { "Texture": "frame3.png", "Duration": 0.1 }
  ],
  "Loop": true
}
```

## Item Creation

### Basic Item

Create a JSON file in `Server/Items/`:

```json
{
  "Type": "Item",
  "Identifier": "mypack:my_item",
  "DisplayName": "My Custom Item",
  "Category": "Tools",
  "MaxStackSize": 64,
  "Model": "Common/Models/Items/my_item.bbmodel",
  "Texture": "Common/Textures/Items/my_item.png"
}
```

### Item Properties

| Property | Type | Description |
|----------|------|-------------|
| `MaxStackSize` | int | Stack limit (1-64) |
| `Durability` | int | Durability value |
| `AttackDamage` | float | Weapon damage |
| `AttackSpeed` | float | Attack speed modifier |
| `EquipSlot` | string | Armor slot (head, chest, legs, feet) |

### Tool Item

```json
{
  "Type": "Item",
  "Identifier": "mypack:super_pickaxe",
  "DisplayName": "Super Pickaxe",
  "Category": "Tools",
  "MaxStackSize": 1,
  "Durability": 500,
  "ToolType": "Pickaxe",
  "MiningSpeed": 2.0,
  "AttackDamage": 5.0
}
```

### Consumable Item

```json
{
  "Type": "Item",
  "Identifier": "mypack:health_potion",
  "DisplayName": "Health Potion",
  "Category": "Consumables",
  "MaxStackSize": 16,
  "Consumable": {
    "Duration": 1.0,
    "Effects": [
      { "Type": "Heal", "Value": 10 }
    ]
  }
}
```

## Creative Menu Categories

### Default Categories

- Building
- Decoration
- Nature
- Tools
- Weapons
- Armor
- Consumables
- Materials
- Miscellaneous

### Custom Categories

Create in `Server/Categories/`:

```json
{
  "Type": "ItemCategory",
  "Identifier": "mypack:custom_category",
  "DisplayName": "My Category",
  "Icon": "Common/Textures/UI/category_icon.png",
  "SortOrder": 100
}
```

### Subcategories

```json
{
  "Type": "ItemCategory",
  "Identifier": "mypack:sub_category",
  "DisplayName": "Sub Category",
  "Parent": "mypack:custom_category",
  "SortOrder": 1
}
```

## Blockbench Modeling

### Setup

1. Install [Blockbench](https://blockbench.net/)
2. Use "Generic Model" format for Hytale
3. Enable grid snapping for proper alignment

### Export Settings

- Format: `.bbmodel` (native)
- Textures: PNG, power-of-2 dimensions recommended
- UV mapping: Per-face or atlas

### Animation Export

Export animations as `.bbmodelanimation` for entity/mob animations.

## File Paths

### Pack Location

```
%AppData%/Hytale/UserData/Packs/YourPackName/
```

### Exploring Base Game Assets

1. Open Hytale launcher
2. Settings → Open Directory
3. Navigate to `install/release/package/game/latest`
4. Extract `Assets.zip` to explore structure

## Translations

Create translations in `Server/Translations/`:

```json
{
  "en-US": {
    "block.mypack.my_block": "My Custom Block",
    "item.mypack.my_item": "My Custom Item"
  },
  "pt-BR": {
    "block.mypack.my_block": "Meu Bloco Customizado",
    "item.mypack.my_item": "Meu Item Customizado"
  }
}
```

## Recipes

### Crafting Recipe

Create in `Server/Recipes/`:

```json
{
  "Type": "CraftingRecipe",
  "Identifier": "mypack:my_item_recipe",
  "Pattern": [
    "AAA",
    " B ",
    " B "
  ],
  "Ingredients": {
    "A": "hytale:iron_ingot",
    "B": "hytale:stick"
  },
  "Result": {
    "Item": "mypack:my_item",
    "Count": 1
  }
}
```

### Shapeless Recipe

```json
{
  "Type": "CraftingRecipe",
  "Identifier": "mypack:shapeless_recipe",
  "Shapeless": true,
  "Ingredients": [
    "hytale:red_dye",
    "hytale:white_wool"
  ],
  "Result": {
    "Item": "mypack:red_wool",
    "Count": 1
  }
}
```
