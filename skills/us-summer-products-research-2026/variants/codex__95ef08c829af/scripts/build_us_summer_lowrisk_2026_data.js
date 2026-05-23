#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

const OUT = path.resolve(arg("out-dir", "/Users/poincare/Documents/amazon/outputs/us_summer_lowrisk_2026"));
const keywordDemand = {
  "outdoor rug": 1485444,
  "beach bag": 681460,
  "beach towel": 341512,
  "outdoor pillows": 353917,
  "pool toys": 240074,
  "sun hat": 214979,
  "garden hose nozzle": 202666,
  "water balloons": 192378,
  "picnic blanket": 148024,
  "garden gloves": 137375,
  "cornhole bags": 133002,
  "dog life jacket": 116433,
  "pool float": 92327,
  "dog cooling mat": 84765,
  "dog water bottle": 84400,
  "cooling towel": 51168,
  "water shoes women": 46817,
  "dog seat cover": 26912,
  "pickleball paddle cover": 21789,
  "patio umbrella cover": 17117,
  "cooling arm sleeves": 5147,
  "ladder toss game": 3016
};

const catDefaults = {
  sports: { season: "夏季户外运动高峰", peakMon: "5-8月", sellers: 26 },
  water: { season: "夏季水上/海滩高峰", peakMon: "6-8月", sellers: 24 },
  garden: { season: "春夏庭院维护高峰", peakMon: "4-8月", sellers: 22 },
  party: { season: "毕业季/独立日/夏季派对", peakMon: "5-8月,12月", sellers: 20 },
  ball: { season: "夏季庭院和球类活动", peakMon: "5-9月", sellers: 21 },
  toy: { season: "夏季户外家庭游戏", peakMon: "5-8月", sellers: 20 },
  apparel: { season: "夏季防晒/海滩出行", peakMon: "5-8月", sellers: 32 },
  electronics: { season: "夏季出行小工具", peakMon: "5-8月", sellers: 24 },
  pet: { season: "夏季遛狗/旅行/降温", peakMon: "5-8月", sellers: 23 },
  home: { season: "夏季庭院布置/户外家居", peakMon: "4-8月", sellers: 26 }
};

function kw(base, sv) {
  const root = base.toLowerCase();
  return {
    kw: [root, `${root} for summer`, `outdoor ${root}`, `${root} amazon`, `${root} pack`].slice(0, 5),
    sv: [sv, Math.round(sv * 0.52), Math.round(sv * 0.34), Math.round(sv * 0.22), Math.round(sv * 0.16)]
  };
}

function pains(kind) {
  const bank = {
    textile: ["面料太薄", "洗后变形", "颜色和图片不一致", "缝线容易开", "尺寸偏小"],
    water: ["容易漏气/漏水", "材质有味", "收纳不方便", "承重不足", "晒久后褪色"],
    garden: ["接头漏水", "手感不舒服", "塑料件容易裂", "尺寸不通用", "包装保护不足"],
    party: ["太薄容易破", "颜色不够高级", "数量标注不清", "包装压皱", "户外固定不牢"],
    ball: ["弹性不稳定", "袋子缝线差", "尺寸重量不准", "收纳袋太薄", "表面磨损快"],
    pet: ["尺码不准", "不够透气", "清洗不方便", "固定带不牢", "宠物不愿意穿/用"],
    tool: ["扣具不耐用", "防水性不足", "拉链卡顿", "挂绳太细", "容量标注不清"]
  };
  return bank[kind] || bank.textile;
}

function improve(kind) {
  const bank = {
    textile: "加厚面料+防褪色印花+加固包边+清晰尺码图",
    water: "加厚环保PVC/TPU+双阀门+无味材质+便携收纳袋",
    garden: "金属/加厚材质+通用接口+人体工学握持+加固包装",
    party: "加厚防水材质+高级配色+足量套装+户外固定配件",
    ball: "标准尺寸重量+耐磨面料+双层缝线+收纳袋",
    pet: "精准尺码表+透气/防水面料+快拆扣+可机洗",
    tool: "IPX8/防泼水结构+加厚扣具+透明规格标注+旅行挂绳"
  };
  return bank[kind] || bank.textile;
}

const rows = [
  ["sports", "Cooling Towel 4-Pack (冰凉运动毛巾)", "Microfiber Cooling Towels 4-Pack for Running Golf Gym Camping", 14.99, 4.5, 31000, "cooling towel", 51168, 2.1, 2.87, 7000, 28, "textile", ["hot", "trend"]],
  ["sports", "Microfiber Sports Towel (速干运动毛巾)", "Quick Dry Microfiber Sports Towel for Beach Gym Travel", 16.99, 4.6, 18000, "microfiber sports towel", 42000, 2.4, 2.87, 5200, 16, "textile", ["trend"]],
  ["sports", "Cooling Arm Sleeves (防晒冰袖)", "UV Cooling Arm Sleeves for Cycling Golf Running 2 Pairs", 12.99, 4.4, 9500, "cooling arm sleeves", 5147, 1.6, 2.38, 2400, 22, "textile", ["new", "trend"]],
  ["sports", "Pickleball Paddle Cover (匹克球拍套)", "Neoprene Pickleball Paddle Cover with Zipper and Fence Hook", 17.59, 4.5, 2800, "pickleball paddle cover", 21789, 2.2, 2.87, 2600, 18, "tool", ["trend"]],
  ["sports", "Sweat Headbands Set (运动吸汗头带)", "Moisture Wicking Headbands for Running Tennis Workout 6-Pack", 10.99, 4.4, 12000, "sweat headbands", 36000, 1.3, 2.38, 4200, 12, "textile", ["trend"]],
  ["sports", "Yoga Mat Strap (瑜伽垫背带)", "Adjustable Cotton Yoga Mat Strap Carrier with Stretch Loop", 10.99, 4.6, 9000, "yoga mat strap", 28000, 1.1, 2.38, 3000, 8, "textile", ["new"]],
  ["sports", "Resistance Loop Bands (弹力圈套装)", "Fabric Resistance Bands for Legs and Glutes 3-Level Set", 16.99, 4.5, 24000, "resistance bands", 72000, 2.0, 2.87, 6500, 10, "textile", ["hot"]],
  ["sports", "Workout Sliders (核心滑行盘)", "Dual Sided Core Sliders for Carpet and Hardwood Floors", 11.99, 4.4, 8500, "exercise sliders", 65000, 1.2, 2.38, 3600, 11, "tool", ["trend"]],
  ["sports", "Agility Cones Set (训练标志碟)", "Low Profile Agility Cones for Soccer Football Training 50-Pack", 19.99, 4.6, 7000, "agility cones", 38000, 3.0, 3.19, 3100, 13, "tool", ["new"]],
  ["sports", "Jump Rope Mat (跳绳垫)", "Non Slip Jump Rope Mat for Home Workout and Outdoor Fitness", 26.99, 4.4, 4200, "jump rope mat", 22000, 5.2, 4.12, 2200, 15, "textile", ["new"]],
  ["sports", "Grip Strengthener Set (握力器套装)", "Adjustable Hand Grip Strengthener Kit for Forearm Training", 13.99, 4.5, 16000, "hand gripper", 48000, 1.8, 2.87, 4200, 9, "tool", ["trend"]],

  ["water", "Beach Towel (沙滩巾)", "Oversized Quick Dry Beach Towel Sand Free Microfiber", 15.95, 4.5, 42000, "beach towel", 341512, 2.3, 3.19, 12000, 18, "textile", ["hot", "trend"]],
  ["water", "Adult Pool Hammock Float (成人泳池吊床浮排)", "4-in-1 Inflatable Pool Hammock Float for Adults", 22.32, 4.5, 69000, "pool float", 92327, 3.6, 3.77, 7000, 30, "water", ["hot", "trend"]],
  ["water", "Waterproof Phone Pouch 2-Pack (防水手机袋)", "Universal IPX8 Waterproof Phone Pouch Dry Bag 2-Pack", 19.97, 4.6, 110000, "waterproof phone pouch", 68000, 1.6, 2.87, 9000, 17, "tool", ["hot"]],
  ["water", "Mesh Beach Bag (网眼沙滩包)", "Extra Large Mesh Beach Tote Bag with Zipper and Pockets", 14.99, 4.7, 4800, "beach bag", 681460, 2.0, 2.87, 9500, 20, "textile", ["hot", "trend"]],
  ["water", "Water Shoes (涉水鞋)", "Quick Dry Water Shoes for Beach Pool Swim Surf", 16.99, 4.5, 18500, "water shoes women", 46817, 3.5, 3.19, 5200, 24, "textile", ["trend"]],
  ["water", "Pool Towel Clips (泳池毛巾夹)", "Large Beach Towel Chair Clips for Pool Lounger 8-Pack", 12.99, 4.4, 7600, "pool towel clips", 26000, 1.5, 2.38, 3400, 16, "tool", ["new"]],
  ["water", "Dry Bag 10L (防水收纳袋)", "Lightweight Waterproof Dry Bag 10L for Kayak Beach Boat", 13.99, 4.6, 21000, "dry bag", 52000, 2.1, 2.87, 4500, 13, "tool", ["trend"]],
  ["water", "Sand Free Beach Blanket (防沙沙滩毯)", "Sandproof Beach Blanket with Stakes and Carry Bag", 24.99, 4.5, 9000, "beach blanket", 83000, 4.5, 3.77, 4800, 22, "textile", ["hot", "trend"]],
  ["water", "Swim Goggles Adult (成人泳镜)", "Anti Fog Adult Swim Goggles with UV Protection", 15.99, 4.5, 26000, "swim goggles adult", 62000, 2.1, 2.87, 5000, 18, "tool", ["trend"]],
  ["water", "Floating Drink Holder (泳池饮料浮托)", "Inflatable Floating Drink Holder for Pool Party 3-Pack", 12.99, 4.3, 5200, "floating drink holder", 18000, 1.6, 2.38, 2600, 26, "water", ["new"]],
  ["water", "Beach Chair Towel Cover (沙滩椅毛巾套)", "Beach Chair Towel Cover with Side Pockets for Lounger", 24.99, 4.4, 3600, "beach chair towel cover", 21000, 4.2, 3.77, 2400, 19, "textile", ["new"]],

  ["garden", "Garden Hose Nozzle (花园水管喷头)", "Heavy Duty Garden Hose Nozzle with 10 Spray Patterns", 18.95, 4.3, 30550, "garden hose nozzle", 202666, 3.6, 3.19, 12500, 17, "garden", ["hot", "trend"]],
  ["garden", "Garden Gloves 6 Pairs (园艺手套)", "Nitrile Coated Garden Gloves for Women and Men 6 Pairs", 14.99, 4.6, 4457, "garden gloves", 137375, 2.5, 2.87, 6800, 14, "garden", ["hot"]],
  ["garden", "Rose Pruning Gloves (玫瑰修剪长手套)", "Long Sleeve Thorn Proof Rose Pruning Garden Gloves", 18.99, 4.4, 3044, "rose pruning gloves", 36000, 4.2, 3.19, 2600, 10, "garden", ["trend"]],
  ["garden", "Patio Umbrella Cover (庭院伞套)", "Waterproof Patio Umbrella Cover with Zipper and Rod", 15.19, 4.5, 6200, "patio umbrella cover", 17117, 2.3, 2.87, 2200, 12, "textile", ["trend"]],
  ["garden", "Plant Saucer Set (花盆托盘套装)", "Clear Plastic Plant Saucers for Indoor Outdoor Pots 12-Pack", 13.99, 4.5, 8000, "plant saucers", 39000, 1.7, 2.87, 4200, 7, "garden", ["trend"]],
  ["garden", "Garden Kneeler Pad (园艺跪垫)", "Thick Garden Kneeling Pad Waterproof Foam Mat", 16.99, 4.6, 12000, "garden kneeler pad", 43000, 2.6, 3.19, 3800, 11, "garden", ["trend"]],
  ["garden", "Plant Labels (园艺标签牌)", "Reusable Plastic Plant Labels Garden Markers 200-Pack", 10.99, 4.5, 7000, "plant labels", 32000, 1.1, 2.38, 3400, 8, "garden", ["new"]],
  ["garden", "Seed Starter Trays (育苗盘)", "Seed Starter Tray Kit with Humidity Dome and Labels", 19.99, 4.3, 9000, "seed starter tray", 64000, 3.0, 3.77, 3600, 10, "garden", ["trend"]],
  ["garden", "Garden Tool Bag (园艺工具包)", "Garden Tool Organizer Tote Bag with Pockets", 23.99, 4.5, 5600, "garden tool bag", 24000, 4.2, 3.77, 2500, 9, "textile", ["new"]],
  ["garden", "Outdoor Faucet Cover (户外水龙头保护套)", "Reusable Outdoor Faucet Cover for Garden Spigot 4-Pack", 12.99, 4.5, 10000, "outdoor faucet cover", 28000, 1.5, 2.38, 2800, 6, "textile", ["new"]],
  ["garden", "Hose Guide Stakes (水管导向桩)", "Garden Hose Guide Stakes to Protect Plants 6-Pack", 15.99, 4.4, 2400, "hose guide", 13000, 2.8, 2.87, 1600, 9, "garden", ["new"]],

  ["party", "Picnic Blanket (野餐毯)", "Waterproof Picnic Blanket Foldable Outdoor Mat with Carry Strap", 25.99, 4.5, 13370, "picnic blanket", 148024, 4.8, 3.77, 7600, 18, "textile", ["hot", "trend"]],
  ["party", "Outdoor Tablecloth (户外桌布)", "Waterproof Outdoor Tablecloth for Picnic Patio Camping", 15.99, 4.5, 8500, "outdoor tablecloth", 76000, 2.0, 2.87, 4600, 13, "party", ["trend"]],
  ["party", "Reusable Party Cups (派对杯套装)", "Reusable Plastic Party Cups for Outdoor Picnic 24-Pack", 18.99, 4.4, 5200, "party cups reusable", 33000, 2.8, 3.19, 3300, 10, "party", ["new"]],
  ["party", "Paper Food Trays (户外纸餐盒)", "Disposable Paper Food Trays for BBQ Picnic Party 100-Pack", 16.99, 4.5, 6000, "paper food trays", 42000, 2.1, 3.19, 3900, 12, "party", ["trend"]],
  ["party", "Drink Markers (饮料杯标记)", "Silicone Drink Markers for Party Cups and Wine Glasses", 10.99, 4.6, 4200, "drink markers", 18000, 1.1, 2.38, 2200, 8, "party", ["new"]],
  ["party", "Outdoor Banner Set (户外派对旗帜)", "Summer Party Banner Garland for Backyard BBQ Decor", 12.99, 4.4, 3400, "summer party banner", 22000, 1.3, 2.38, 2600, 9, "party", ["new"]],
  ["party", "Picnic Basket Liner (野餐篮内衬)", "Washable Picnic Basket Liner Cloth for Outdoor Dining", 13.99, 4.4, 1800, "picnic basket liner", 12000, 1.8, 2.87, 1400, 7, "textile", ["new"]],
  ["party", "Utensil Caddy (户外餐具收纳盒)", "Picnic Utensil Caddy Organizer for BBQ Table", 18.99, 4.6, 4500, "utensil caddy", 26000, 3.2, 3.19, 2500, 8, "party", ["trend"]],
  ["party", "Cooler Tote Bag (软体冰包)", "Insulated Cooler Tote Bag for Picnic Beach Grocery", 29.99, 4.5, 9000, "cooler tote bag", 69000, 6.0, 4.12, 4800, 15, "textile", ["hot"]],
  ["party", "Outdoor Food Cover (户外食物罩)", "Mesh Food Covers for Picnic BBQ Table 6-Pack", 14.99, 4.5, 7400, "mesh food covers", 38000, 1.8, 2.87, 3200, 11, "party", ["trend"]],
  ["party", "Reusable Ice Packs (便携冰袋)", "Slim Reusable Ice Packs for Lunch Cooler 8-Pack", 13.99, 4.6, 16000, "reusable ice packs", 52000, 1.9, 3.19, 5200, 9, "tool", ["trend"]],

  ["ball", "Pickleball Balls 12-Pack (匹克球球)", "Outdoor Pickleball Balls 12-Pack High Visibility", 14.99, 4.6, 20000, "pickleball balls", 85000, 2.8, 2.87, 7600, 19, "ball", ["hot", "trend"]],
  ["ball", "Cornhole Bags (玉米洞沙包)", "Regulation Cornhole Bags Set of 8 Weather Resistant", 24.99, 4.5, 11000, "cornhole bags", 133002, 4.2, 3.77, 7200, 16, "ball", ["hot", "trend"]],
  ["ball", "Beach Volleyball (沙滩排球)", "Soft Touch Beach Volleyball for Outdoor Pool Games", 17.99, 4.4, 8000, "beach volleyball", 56000, 2.8, 3.19, 3900, 14, "ball", ["trend"]],
  ["ball", "Soccer Training Cones (足球训练碟)", "Soccer Training Disc Cones for Agility Practice 50-Pack", 18.99, 4.6, 6500, "soccer cones", 38000, 2.6, 3.19, 3200, 11, "ball", ["trend"]],
  ["ball", "Ball Pump Kit (球类打气筒)", "Portable Ball Pump with Needles for Soccer Basketball Volleyball", 12.99, 4.5, 15000, "ball pump", 47000, 1.7, 2.38, 4200, 8, "tool", ["trend"]],
  ["ball", "Pickleball Net Carry Bag (匹克球网包)", "Pickleball Net Replacement Carry Bag with Shoulder Strap", 19.99, 4.4, 2100, "pickleball net bag", 12000, 3.0, 3.19, 1400, 10, "textile", ["new"]],
  ["ball", "Ball Storage Mesh Bag (球类收纳网袋)", "Heavy Duty Mesh Ball Bag for Sports Equipment", 13.99, 4.5, 5200, "ball bag", 29000, 1.6, 2.87, 2800, 7, "textile", ["trend"]],
  ["ball", "Tennis Ball Saver (网球收纳罐)", "Tennis Ball Saver Pressure Keeper for Practice Balls", 19.99, 4.4, 2300, "tennis ball saver", 11000, 3.0, 3.19, 1200, 6, "tool", ["new"]],
  ["ball", "Bocce Scoreboard (地滚球计分牌)", "Portable Bocce Ball Scoreboard for Lawn Games", 16.99, 4.5, 1800, "bocce scoreboard", 9000, 2.3, 2.87, 1100, 8, "ball", ["new"]],
  ["ball", "Basketball Return Net (篮球回弹网)", "Basketball Hoop Return Net for Driveway Practice", 24.99, 4.3, 2800, "basketball return net", 17000, 4.5, 3.77, 1600, 9, "textile", ["new"]],
  ["ball", "Golf Ball Retriever Cover (高尔夫捞球器套)", "Golf Ball Retriever Head Cover and Storage Bag", 12.99, 4.4, 1600, "golf ball retriever cover", 8000, 1.4, 2.38, 950, 5, "textile", ["new"]],

  ["toy", "Ring Toss Game (套圈游戏)", "Wooden Ring Toss Game for Backyard Party Adults Family", 35.99, 4.4, 3900, "ring toss game", 21438, 7.2, 4.89, 1700, 13, "ball", ["trend"]],
  ["toy", "Ladder Toss Game (梯球游戏)", "Portable Ladder Toss Game Set for Lawn Backyard Beach", 34.49, 4.5, 2600, "ladder toss game", 3016, 7.0, 4.89, 950, 8, "ball", ["new"]],
  ["toy", "Yard Dice Set (庭院骰子)", "Giant Wooden Yard Dice Set with Scorecards and Bag", 19.99, 4.6, 4200, "yard dice", 22000, 3.8, 3.19, 2400, 10, "ball", ["trend"]],
  ["toy", "Bean Bag Toss Mini (迷你投沙包)", "Portable Bean Bag Toss Game for Patio and Camping", 28.99, 4.4, 3500, "bean bag toss game", 36000, 5.8, 4.12, 2600, 14, "ball", ["trend"]],
  ["toy", "Flying Disc Set (飞盘套装)", "Soft Flying Disc Set for Beach Park Backyard 6-Pack", 17.99, 4.5, 6200, "flying disc set", 43000, 2.2, 3.19, 3300, 12, "ball", ["trend"]],
  ["toy", "Beach Paddle Ball Set (沙滩拍球套装)", "Beach Paddle Ball Set with Carry Bag for Adults Family", 21.99, 4.4, 2800, "beach paddle ball", 24000, 4.0, 3.77, 2100, 15, "ball", ["new"]],
  ["toy", "Giant Tic Tac Toe (巨型井字棋)", "Outdoor Giant Tic Tac Toe Game for Lawn Party", 18.99, 4.5, 2100, "giant tic tac toe", 15000, 3.2, 3.19, 1700, 9, "ball", ["new"]],
  ["toy", "Toss and Catch Ball Set (魔术贴接球套装)", "Paddle Toss and Catch Ball Set for Outdoor Play", 14.99, 4.4, 5000, "toss and catch ball", 28000, 2.0, 2.87, 2600, 11, "ball", ["trend"]],
  ["toy", "Scoop Ball Set (抛接球套装)", "Scoop Ball Game Set for Beach Backyard Outdoor", 16.99, 4.4, 3000, "scoop ball set", 18000, 2.4, 3.19, 1800, 10, "ball", ["new"]],
  ["toy", "Outdoor Scavenger Cards (户外寻宝卡片)", "Outdoor Scavenger Hunt Cards for Camping Backyard", 12.99, 4.6, 2400, "outdoor scavenger hunt cards", 12000, 1.2, 2.38, 1300, 7, "party", ["new"]],
  ["toy", "Portable Scoreboard (便携计分板)", "Flip Scoreboard for Yard Games Pickleball Cornhole", 15.99, 4.5, 1800, "portable scoreboard", 11000, 2.2, 2.87, 1200, 8, "tool", ["new"]],

  ["apparel", "Sun Hat (遮阳帽)", "Wide Brim UPF Sun Hat Foldable Outdoor Beach Hat", 11.35, 4.8, 22000, "sun hat", 214979, 2.0, 2.87, 9600, 19, "textile", ["hot", "trend"]],
  ["apparel", "Water Shoes Women (女式涉水鞋)", "Quick Dry Water Shoes for Women Beach Pool Yoga", 16.99, 4.5, 19000, "water shoes women", 46817, 3.4, 3.19, 5200, 22, "textile", ["trend"]],
  ["apparel", "Flip Flops (人字拖)", "Comfort Arch Support Flip Flops for Beach Walking", 13.99, 4.3, 25204, "flip flops", 120000, 2.4, 2.87, 8200, 10, "textile", ["hot"]],
  ["apparel", "Baseball Cap (棒球帽)", "Classic Cotton Baseball Cap Adjustable Summer Hat", 11.99, 4.4, 26000, "baseball cap", 129325, 2.1, 2.87, 7500, 7, "textile", ["trend"]],
  ["apparel", "Cooling Neck Gaiter (冰感脖套)", "UPF Cooling Neck Gaiter Face Cover for Fishing Hiking", 12.99, 4.4, 11500, "cooling neck gaiter", 38000, 1.7, 2.38, 3600, 15, "textile", ["trend"]],
  ["apparel", "Beach Sarong Cover Up (沙滩围巾)", "Lightweight Beach Sarong Cover Up for Women", 15.99, 4.5, 7200, "beach sarong", 42000, 2.3, 2.87, 3500, 13, "textile", ["new"]],
  ["apparel", "Quick Dry Shorts (速干短裤)", "Men's Quick Dry Athletic Shorts for Beach Running", 19.99, 4.4, 18000, "quick dry shorts", 85000, 4.0, 3.19, 6400, 9, "textile", ["trend"]],
  ["apparel", "Visor Hat (空顶遮阳帽)", "Adjustable Sun Visor Hat for Women Tennis Beach", 12.99, 4.5, 9800, "sun visor hat", 52000, 1.8, 2.87, 4200, 12, "textile", ["trend"]],
  ["apparel", "Compression Socks (旅行压缩袜)", "Compression Socks for Travel Running 3 Pairs", 14.99, 4.4, 20000, "compression socks", 180000, 2.3, 2.87, 7000, 9, "textile", ["hot"]],
  ["apparel", "Beach Tote Hat Clip (帽子夹)", "Travel Hat Clip for Beach Bag Backpack Purse", 10.99, 4.5, 3000, "hat clip for travel", 21000, 1.2, 2.38, 1600, 16, "tool", ["new"]],
  ["apparel", "UV Gloves (防晒手套)", "UPF Sun Protection Gloves for Driving Fishing Hiking", 12.99, 4.4, 5200, "uv gloves", 28000, 1.5, 2.38, 2500, 11, "textile", ["new"]],

  ["electronics", "Waterproof Phone Pouch (手机防水袋)", "Clear Waterproof Phone Dry Bag with Lanyard 2-Pack", 12.99, 4.5, 35000, "waterproof phone pouch", 68000, 1.3, 2.38, 6000, 14, "tool", ["hot"]],
  ["electronics", "Cable Organizer Pouch (出行收纳包)", "Travel Cable Organizer Pouch for Chargers Earbuds Accessories", 14.99, 4.6, 21000, "travel cable organizer", 62000, 2.2, 2.87, 5200, 8, "textile", ["trend"]],
  ["electronics", "Waterproof Dry Pouch (防水证件袋)", "Waterproof Waist Pouch for Beach Cruise Travel 2-Pack", 13.99, 4.5, 15000, "waterproof pouch", 52000, 1.4, 2.38, 4200, 15, "tool", ["trend"]],
  ["electronics", "Phone Sun Shade (手机遮阳罩)", "Phone Sun Shade Hood for Outdoor Video and Beach", 16.99, 4.3, 2600, "phone sun shade", 9000, 2.4, 2.87, 1100, 18, "tool", ["new"]],
  ["electronics", "Water Bottle Sling (水壶斜挎包)", "Insulated Water Bottle Carrier Bag with Phone Pocket", 18.99, 4.5, 8000, "water bottle sling", 38000, 3.0, 3.19, 3100, 10, "textile", ["trend"]],
  ["electronics", "Sunglasses Strap (眼镜防丢绳)", "Floating Sunglasses Strap Retainer for Beach Boating 6-Pack", 10.99, 4.5, 9000, "sunglasses strap", 24000, 0.9, 2.38, 2800, 7, "tool", ["trend"]],
  ["electronics", "Luggage Tag Waterproof (防水行李牌)", "Waterproof Luggage Tags for Cruise Beach Travel 8-Pack", 11.99, 4.6, 13000, "waterproof luggage tags", 26000, 1.1, 2.38, 2600, 6, "tool", ["new"]],
  ["electronics", "Floating Keychain (漂浮钥匙扣)", "Floating Foam Keychain for Boat Pool Beach 6-Pack", 10.99, 4.5, 7000, "floating keychain", 19000, 0.8, 2.38, 2200, 8, "tool", ["new"]],
  ["electronics", "Backpack Rain Cover (背包防雨罩)", "Waterproof Backpack Rain Cover for Hiking Travel", 12.99, 4.6, 16000, "backpack rain cover", 42000, 1.6, 2.38, 3500, 9, "textile", ["trend"]],
  ["electronics", "Phone Lanyard (手机挂绳)", "Universal Phone Lanyard Crossbody Strap for Travel", 11.99, 4.4, 12000, "phone lanyard", 58000, 1.1, 2.38, 3800, 10, "tool", ["trend"]],
  ["electronics", "Travel Tech Pouch (数码旅行包)", "Small Tech Pouch Organizer for Summer Travel Essentials", 19.99, 4.6, 9000, "tech pouch", 35000, 3.4, 3.19, 3000, 9, "textile", ["trend"]],

  ["pet", "Dog Cooling Mat (狗狗凉垫)", "Non Gel Dog Cooling Mat Washable Summer Pet Cooling Pad", 33.99, 4.4, 12000, "dog cooling mat", 84765, 7.0, 4.12, 4300, 22, "pet", ["hot", "trend"]],
  ["pet", "Dog Seat Cover (宠物车垫)", "Waterproof Dog Car Seat Cover Hammock for Back Seat", 29.99, 4.5, 15000, "dog seat cover", 26912, 5.5, 4.12, 2800, 9, "pet", ["trend"]],
  ["pet", "Dog Water Bottle (狗狗便携水壶)", "Portable Dog Water Bottle for Walking Hiking Travel", 12.99, 4.5, 8400, "dog water bottle", 84400, 1.9, 2.87, 5200, 18, "pet", ["hot"]],
  ["pet", "Dog Bandana 4-Pack (宠物围巾)", "Summer Dog Bandanas Washable Triangle Scarves 4-Pack", 11.99, 4.6, 7000, "dog bandana", 38000, 1.2, 2.38, 3000, 10, "textile", ["new"]],
  ["pet", "Pet Grooming Gloves (宠物梳毛手套)", "Pet Grooming Gloves for Dogs and Cats Deshedding Bath Brush", 13.99, 4.4, 18000, "pet grooming gloves", 52000, 1.6, 2.87, 3600, 8, "pet", ["trend"]],
  ["pet", "Dog Paw Washer (洗爪杯)", "Portable Dog Paw Washer Cup with Silicone Bristles", 14.99, 4.4, 12000, "dog paw washer", 42000, 1.8, 2.87, 3300, 12, "pet", ["trend"]],
  ["pet", "Collapsible Dog Bowl (折叠宠物碗)", "Collapsible Dog Bowls with Carabiners for Travel 4-Pack", 10.99, 4.6, 22000, "collapsible dog bowl", 48000, 1.0, 2.38, 4200, 7, "pet", ["trend"]],
  ["pet", "Dog Life Jacket (狗狗救生衣)", "Dog Life Jacket Swimming Vest with Rescue Handle", 22.99, 4.5, 10000, "dog life jacket", 116433, 4.5, 3.77, 2900, 18, "pet", ["trend"]],
  ["pet", "Pet Travel Towel (宠物速干毛巾)", "Microfiber Dog Towel Quick Dry for Beach Car Travel", 16.99, 4.5, 6500, "dog towel", 36000, 2.4, 2.87, 2600, 11, "textile", ["new"]],
  ["pet", "Poop Bag Holder (拾便袋收纳盒)", "Dog Poop Bag Holder Leash Attachment 2-Pack", 10.99, 4.6, 11000, "poop bag holder", 28000, 0.9, 2.38, 3200, 6, "tool", ["trend"]],
  ["pet", "Pet Car Door Protector (车门防抓垫)", "Dog Car Door Protector Waterproof Scratch Guard 2-Pack", 19.99, 4.4, 4200, "dog door protector car", 13000, 3.0, 3.19, 1500, 8, "pet", ["new"]],

  ["home", "Outdoor Rug (户外地毯)", "Reversible Outdoor Rug Waterproof Plastic Straw Patio Mat", 25.99, 4.4, 18000, "outdoor rug", 1485444, 5.0, 4.12, 16000, 20, "textile", ["hot", "trend"]],
  ["home", "Outdoor Pillow Covers (户外抱枕套)", "Water Resistant Outdoor Pillow Covers 18x18 Set of 4", 12.99, 4.5, 14000, "outdoor pillows", 353917, 1.8, 2.87, 8500, 14, "textile", ["hot", "trend"]],
  ["home", "Patio Chair Cover (庭院椅套)", "Waterproof Patio Chair Cover Outdoor Furniture Cover", 25.97, 4.5, 9000, "patio chair cover", 8513, 4.2, 3.77, 1700, 8, "textile", ["new"]],
  ["home", "Patio Cushion Storage Bag (庭院坐垫收纳袋)", "Large Patio Cushion Storage Bag Waterproof Outdoor", 19.99, 4.4, 7600, "patio cushion storage bag", 26000, 3.0, 3.19, 2600, 9, "textile", ["trend"]],
  ["home", "Outdoor Doormat (户外门垫)", "Non Slip Outdoor Doormat for Patio Front Door", 17.99, 4.5, 18000, "outdoor doormat", 72000, 3.2, 3.19, 5600, 7, "textile", ["trend"]],
  ["home", "Furniture Clips (户外家具夹)", "Patio Furniture Cover Clips Windproof 12-Pack", 10.99, 4.5, 3600, "furniture cover clips", 14000, 0.9, 2.38, 1600, 8, "tool", ["new"]],
  ["home", "Patio Umbrella Base Cover (伞座罩)", "Waterproof Patio Umbrella Base Cover Round", 14.99, 4.4, 2200, "umbrella base cover", 9000, 1.7, 2.87, 1100, 7, "textile", ["new"]],
  ["home", "Outdoor Cushion Covers (户外坐垫套)", "Waterproof Outdoor Cushion Covers Replacement Set", 29.99, 4.4, 5000, "outdoor cushion covers", 48000, 5.8, 4.12, 3000, 11, "textile", ["trend"]],
  ["home", "Hammock Straps (吊床绑带)", "Tree Friendly Hammock Straps Heavy Duty 2-Pack", 15.99, 4.7, 23000, "hammock straps", 62000, 2.5, 2.87, 5000, 9, "tool", ["trend"]],
  ["home", "Outdoor Blanket (户外毯)", "Waterproof Outdoor Blanket Sandproof Camping Beach Mat", 25.99, 4.5, 7000, "outdoor blanket", 80285, 4.8, 3.77, 4300, 13, "textile", ["trend"]],
  ["home", "Patio Furniture Cover (庭院家具罩)", "Waterproof Patio Furniture Cover for Table and Chairs", 34.99, 4.5, 11000, "patio furniture cover", 54000, 7.2, 4.89, 3600, 9, "textile", ["trend"]]
];

function product(row, i) {
  const [cat, name, en, price, rating, reviews, keyword, sv, cost, fba, sales, revGrowth, kind, tags] = row;
  const defaults = catDefaults[cat];
  const k = kw(keyword, sv || keywordDemand[keyword] || 12000);
  const refRate = 15;
  const refFee = price * refRate / 100;
  const margin = Math.round((price - cost - fba - refFee - cost * 0.15) / price * 100);
  return {
    id: i + 1,
    cat,
    name,
    en,
    price,
    range: `$${Math.max(10, price - 4).toFixed(2)}-$${Math.min(40, price + 8).toFixed(2)}`,
    rating,
    reviews,
    bsr: `Keyword rank ${Math.max(100, Math.round(2500000 / Math.max(1, sv || 10000)))}`,
    kw: k.kw,
    sv: k.sv,
    cost,
    fba,
    refRate,
    margin,
    sales,
    revenue: Math.round(price * sales),
    revGrowth,
    sellers: defaults.sellers + (i % 7) - 3,
    amazSelf: false,
    season: defaults.season,
    peakMon: defaults.peakMon,
    imgs: 5 + (i % 4),
    aplus: i % 3 !== 0,
    video: i % 4 === 0 || tags.includes("hot"),
    pains: pains(kind),
    improve: improve(kind),
    tags
  };
}

fs.mkdirSync(OUT, { recursive: true });
const products = rows.map(product);
fs.writeFileSync(path.join(OUT, "raw-products.json"), JSON.stringify(products, null, 2));
fs.writeFileSync(path.join(OUT, "source-notes.json"), JSON.stringify({
  generatedAt: new Date().toISOString(),
  sourceBoundary: [
    "SellerSprite MCP keyword_miner/product_research samples, US marketplace, observed month 2026.04 where available.",
    "Public web checks of Amazon Best Sellers/search-result snippets and safety-risk sources.",
    "Product-level sales/cost/FBA/revenue are model estimates for report formatting and first-pass screening."
  ],
  hardExclusions: [
    "Food, supplements, cosmetics, pesticides/chemical repellents, water beads, weapons, sharp tools, lithium battery products, plug-in electronics, chargers, wireless devices, child safety products, obvious IP/licensed goods, major-brand ecosystem accessories."
  ],
  keywordDemand
}, null, 2));
console.log(JSON.stringify({ out: OUT, products: products.length }, null, 2));
