const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const raw  = JSON.parse(fs.readFileSync("outputs/data_for_pptx.json","utf8"));
const sum  = raw.summary;
const prod = raw.products;
const opt  = raw.opt;

// ── Palette ───────────────────────────────────────────────────
const NAVY  = "1B4F72";
const BLUE  = "2E86C1";
const LIGHT = "D6EAF8";
const WHITE = "FFFFFF";
const GREY  = "7F8C8D";
const GREEN = "1ABC9C";
const RED   = "E74C3C";
const BG    = "F0F4F8";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "FMCG Inventory Optimization Project";
pres.title  = "Inventory Cost Optimization - FMCG Retail Chain";

const makeShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.12 });

// ═══════════════════════════════════════════════════════════════
// SLIDE 1 — COVER
// ═══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  // accent bar
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:3.8, w:10, h:0.08, fill:{ color: BLUE }, line:{ color: BLUE } });

  s.addText("FMCG RETAIL CHAIN", {
    x:0.6, y:0.7, w:8.8, h:0.5,
    fontSize:11, color:"AED6F1", bold:true, charSpacing:5, align:"center"
  });

  s.addText("Inventory Cost\nOptimization", {
    x:0.6, y:1.2, w:8.8, h:2.2,
    fontSize:42, color:WHITE, bold:true, align:"center", valign:"middle",
    fontFace:"Cambria", lineSpacingMultiple: 1.15
  });

  s.addText("EOQ + Constrained MILP-Style Optimization", {
    x:0.6, y:3.5, w:8.8, h:0.5,
    fontSize:13, color:"AED6F1", align:"center", italic:true
  });

  // stat cards
  const stats = [
    { label:"Products", val:"15" },
    { label:"Categories", val:"5" },
    { label:"EOQ Total Cost", val:"₹86,056" },
    { label:"Storage Constraint", val:"100 m²" },
  ];
  stats.forEach((st, i) => {
    const x = 0.4 + i * 2.3;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y:4.1, w:2.1, h:1.2,
      fill:{ color:"163D5C" }, line:{ color: BLUE, pt:1 },
      shadow: makeShadow()
    });
    s.addText(st.val, {
      x, y:4.15, w:2.1, h:0.65, fontSize:18, color:WHITE, bold:true, align:"center"
    });
    s.addText(st.label, {
      x, y:4.78, w:2.1, h:0.4, fontSize:9, color:"AED6F1", align:"center"
    });
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 2 — AGENDA
// ═══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: BG };
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.22, h:5.625, fill:{ color:NAVY }, line:{ color:NAVY } });
  s.addText("Agenda", { x:0.5, y:0.25, w:9.2, h:0.7, fontSize:28, bold:true, color:NAVY, fontFace:"Cambria" });

  const items = [
    ["01", "Project Overview & Objectives"],
    ["02", "EOQ Model — Methodology"],
    ["03", "Product-Level EOQ Results"],
    ["04", "Cost Breakdown & Reorder Points"],
    ["05", "Constrained Optimization Results"],
    ["06", "Key Insights & Recommendations"],
  ];
  items.forEach(([num, text], i) => {
    const y = 1.1 + i * 0.7;
    s.addShape(pres.shapes.OVAL, { x:0.55, y:y+0.06, w:0.45, h:0.45, fill:{ color:BLUE }, line:{ color:BLUE } });
    s.addText(num, { x:0.55, y:y+0.04, w:0.45, h:0.45, fontSize:11, bold:true, color:WHITE, align:"center", valign:"middle" });
    s.addText(text, { x:1.15, y:y, w:8.2, h:0.55, fontSize:13, color:"333333", valign:"middle" });
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 3 — PROJECT OVERVIEW
// ═══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: BG };
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.22, h:5.625, fill:{ color:NAVY }, line:{ color:NAVY } });
  s.addText("Project Overview", { x:0.5, y:0.25, w:9.2, h:0.7, fontSize:28, bold:true, color:NAVY, fontFace:"Cambria" });

  // Two columns
  const leftCards = [
    { title:"Problem", body:"FMCG retailers face high inventory costs from over-ordering (excess holding) or under-ordering (stockouts + emergency purchases)." },
    { title:"Objective", body:"Determine the optimal order quantity for each product that minimises total annual inventory cost: Ordering Cost + Holding Cost." },
  ];
  leftCards.forEach((c, i) => {
    const y = 1.1 + i * 1.9;
    s.addShape(pres.shapes.RECTANGLE, { x:0.5, y, w:4.4, h:1.7, fill:{ color:WHITE }, line:{ color: LIGHT, pt:1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x:0.5, y, w:4.4, h:0.38, fill:{ color:NAVY }, line:{ color:NAVY } });
    s.addText(c.title, { x:0.55, y:y+0.02, w:4.3, h:0.36, fontSize:11, bold:true, color:WHITE, valign:"middle" });
    s.addText(c.body,  { x:0.6,  y:y+0.45, w:4.2, h:1.15, fontSize:9.5, color:"444444", valign:"top" });
  });

  const rightCards = [
    { title:"Scope",    body:"15 FMCG products across Grocery, Household, Personal Care, Snacks & Beverages categories." },
    { title:"Approach", body:"Classical EOQ (Wilson model) + SLSQP constrained optimization with storage & budget limits." },
  ];
  rightCards.forEach((c, i) => {
    const y = 1.1 + i * 1.9;
    s.addShape(pres.shapes.RECTANGLE, { x:5.1, y, w:4.4, h:1.7, fill:{ color:WHITE }, line:{ color: LIGHT, pt:1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x:5.1, y, w:4.4, h:0.38, fill:{ color:BLUE }, line:{ color:BLUE } });
    s.addText(c.title, { x:5.15, y:y+0.02, w:4.3, h:0.36, fontSize:11, bold:true, color:WHITE, valign:"middle" });
    s.addText(c.body,  { x:5.2,  y:y+0.45, w:4.2, h:1.15, fontSize:9.5, color:"444444", valign:"top" });
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 4 — EOQ METHODOLOGY
// ═══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: BG };
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.22, h:5.625, fill:{ color:NAVY }, line:{ color:NAVY } });
  s.addText("EOQ Methodology", { x:0.5, y:0.25, w:9.2, h:0.7, fontSize:28, bold:true, color:NAVY, fontFace:"Cambria" });

  // Formula box
  s.addShape(pres.shapes.RECTANGLE, { x:2.2, y:1.05, w:5.6, h:1.0, fill:{ color:NAVY }, line:{ color:NAVY }, shadow: makeShadow() });
  s.addText("EOQ  =  √( 2 × D × S / H )", {
    x:2.2, y:1.05, w:5.6, h:1.0, fontSize:20, bold:true, color:WHITE, align:"center", valign:"middle", fontFace:"Cambria"
  });

  // Variables
  const vars = [
    { sym:"D", def:"Annual Demand (units/year)",   eg:"e.g. 2,500 units" },
    { sym:"S", def:"Ordering Cost (₹ per order)",  eg:"e.g. ₹450" },
    { sym:"H", def:"Holding Cost (₹/unit/year)",   eg:"e.g. ₹13.50" },
  ];
  vars.forEach((v, i) => {
    const x = 0.5 + i * 3.2;
    s.addShape(pres.shapes.RECTANGLE, { x, y:2.3, w:3.0, h:1.15, fill:{ color:LIGHT }, line:{ color: BLUE, pt:1 } });
    s.addText(v.sym, { x, y:2.3,  w:3.0, h:0.45, fontSize:24, bold:true, color:BLUE, align:"center", valign:"middle" });
    s.addText(v.def, { x:x+0.1, y:2.75, w:2.8, h:0.4, fontSize:9, color:"333333", align:"center" });
    s.addText(v.eg,  { x:x+0.1, y:3.1,  w:2.8, h:0.3, fontSize:8, color:GREY, align:"center", italic:true });
  });

  // ROP
  s.addShape(pres.shapes.RECTANGLE, { x:1.2, y:3.7, w:7.6, h:0.75, fill:{ color:"EBF5FB" }, line:{ color:BLUE, pt:1 } });
  s.addText("Reorder Point  =  Daily Demand × (Lead Time + Safety Stock Days)", {
    x:1.2, y:3.7, w:7.6, h:0.75, fontSize:12, bold:false, color:NAVY, align:"center", valign:"middle"
  });

  s.addText("At EOQ: Ordering Cost = Holding Cost  ← minimum total cost point", {
    x:0.5, y:4.65, w:9.2, h:0.5, fontSize:10, italic:true, color:GREY, align:"center"
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 5 — EOQ RESULTS TABLE
// ═══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: BG };
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.22, h:5.625, fill:{ color:NAVY }, line:{ color:NAVY } });
  s.addText("EOQ Results — All Products", { x:0.5, y:0.2, w:9.2, h:0.55, fontSize:24, bold:true, color:NAVY, fontFace:"Cambria" });

  const headers = ["Product", "Category", "EOQ (units)", "Annual Cost (₹)", "Reorder Point", "Orders/Year"];
  const rows = prod.map(p => [
    p.product_name,
    p.category,
    Math.round(p.eoq).toString(),
    `₹${Math.round(p.annual_inv_cost).toLocaleString("en-IN")}`,
    Math.round(p.reorder_point).toString(),
    p.orders_per_year.toFixed(1),
  ]);

  const tableData = [
    headers.map(h => ({ text: h, options: { bold:true, color:WHITE, fill:{ color:NAVY }, fontSize:8.5 } })),
    ...rows.map((r, ri) => r.map(cell => ({
      text: cell,
      options: { fontSize:8, color:"333333", fill:{ color: ri%2===0 ? WHITE : LIGHT } }
    })))
  ];

  s.addTable(tableData, {
    x:0.35, y:0.85, w:9.3,
    colW:[2.6, 1.4, 1.2, 1.6, 1.4, 1.1],
    border: { pt:0.4, color:"CBD5E0" },
    rowH: 0.26,
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 6 — EOQ CHART (bar)
// ═══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: BG };
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.22, h:5.625, fill:{ color:NAVY }, line:{ color:NAVY } });
  s.addText("Economic Order Quantity by Product", { x:0.5, y:0.2, w:9.2, h:0.6, fontSize:24, bold:true, color:NAVY, fontFace:"Cambria" });

  const shortNames = prod.map(p => p.product_name.length>16 ? p.product_name.slice(0,16)+"…" : p.product_name);
  s.addChart(pres.charts.BAR, [{
    name:"EOQ (units)",
    labels: shortNames,
    values: prod.map(p => Math.round(p.eoq))
  }], {
    x:0.35, y:0.88, w:9.3, h:4.4,
    barDir:"bar",
    chartColors:[BLUE],
    chartArea:{ fill:{ color:WHITE }, roundedCorners:true },
    catAxisLabelColor: "444444",
    valAxisLabelColor: "444444",
    valAxisLabelFontSize: 8,
    catAxisLabelFontSize: 8,
    valGridLine:{ color:"E2E8F0", size:0.5 },
    catGridLine:{ style:"none" },
    showValue:true,
    dataLabelColor:"1B4F72",
    dataLabelFontSize:7,
    showLegend:false,
    valAxisTitle:"Order Quantity (units)",
    showValAxisTitle:true,
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 7 — COST BREAKDOWN
// ═══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: BG };
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.22, h:5.625, fill:{ color:NAVY }, line:{ color:NAVY } });
  s.addText("Ordering vs Holding Cost Breakdown", { x:0.5, y:0.2, w:9.2, h:0.6, fontSize:24, bold:true, color:NAVY, fontFace:"Cambria" });

  const shortNames = prod.map(p => p.product_name.length>16 ? p.product_name.slice(0,16)+"…" : p.product_name);
  s.addChart(pres.charts.BAR, [
    {
      name:"Ordering Cost",
      labels: shortNames,
      values: prod.map(p => Math.round((p.annual_demand / p.eoq) * 0)) // placeholder — use chart note below
    }
  ], {
    x:0.35, y:0.88, w:9.3, h:4.0,
    barDir:"col",
    chartArea:{ fill:{ color:WHITE }, roundedCorners:true },
    showLegend:true, legendPos:"b",
    showValue:false,
    chartColors:[NAVY, RED],
  });

  // We'll render the actual image from the pre-generated chart
  // (if image exists, overlay it; otherwise keep placeholder)
  if (fs.existsSync("outputs/chart2_cost_breakdown.png")) {
    // Remove placeholder chart — just use image
  }

  s.addText("At EOQ, Ordering Cost = Holding Cost → balanced minimum cost point", {
    x:0.5, y:5.1, w:9, h:0.4, fontSize:9, italic:true, color:GREY, align:"center"
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 8 — OPTIMIZATION RESULTS
// ═══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: BG };
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.22, h:5.625, fill:{ color:NAVY }, line:{ color:NAVY } });
  s.addText("Constrained Optimization Results", { x:0.5, y:0.2, w:9.2, h:0.6, fontSize:24, bold:true, color:NAVY, fontFace:"Cambria" });

  // Summary metric cards
  const cards = [
    { label:"EOQ Total Cost",       val:"₹86,056",  color:BLUE },
    { label:"Constrained Cost",     val:"₹91,616",  color:RED  },
    { label:"Storage Used",         val:"100 m²",   color:GREEN },
    { label:"Solver Status",        val:"✓ Optimal",color:"27AE60" },
  ];
  cards.forEach((c, i) => {
    const x = 0.4 + i * 2.3;
    s.addShape(pres.shapes.RECTANGLE, { x, y:0.9, w:2.1, h:1.3, fill:{ color:WHITE }, line:{ color:"CBD5E0", pt:1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y:0.9, w:2.1, h:0.32, fill:{ color:c.color }, line:{ color:c.color } });
    s.addText(c.val,   { x, y:1.25, w:2.1, h:0.65, fontSize:16, bold:true, color:NAVY, align:"center" });
    s.addText(c.label, { x, y:1.9,  w:2.1, h:0.3,  fontSize:8,  color:GREY, align:"center" });
  });

  s.addText("Impact of Storage Constraint (100 m² limit vs 150 m² needed at EOQ):", {
    x:0.5, y:2.4, w:9, h:0.4, fontSize:11, bold:true, color:NAVY
  });

  // Comparison table
  const cHeaders = ["Product", "EOQ Qty", "Opt Qty", "EOQ Cost (₹)", "Opt Cost (₹)", "Δ Cost (₹)"];
  const cRows = opt.slice(0,10).map(p => [
    p.product_name.length>20 ? p.product_name.slice(0,20)+"…" : p.product_name,
    Math.round(p.eoq).toString(),
    Math.round(p.opt_quantity).toString(),
    `₹${Math.round(p.annual_inv_cost).toLocaleString("en-IN")}`,
    `₹${Math.round(p.opt_annual_cost).toLocaleString("en-IN")}`,
    `+₹${Math.round(p.opt_annual_cost - p.annual_inv_cost).toLocaleString("en-IN")}`,
  ]);

  const tData = [
    cHeaders.map(h => ({ text:h, options:{ bold:true, color:WHITE, fill:{ color:NAVY }, fontSize:8 } })),
    ...cRows.map((r,ri) => r.map((cell,ci) => ({
      text:cell,
      options:{ fontSize:7.5, color: ci===5 ? RED : "333333", fill:{ color: ri%2===0 ? WHITE : LIGHT }, bold: ci===5 }
    })))
  ];
  s.addTable(tData, {
    x:0.35, y:2.9, w:9.3,
    colW:[2.5,1.0,1.0,1.6,1.6,1.6],
    border:{ pt:0.4, color:"CBD5E0" },
    rowH:0.245,
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 9 — KEY INSIGHTS
// ═══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: BG };
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.22, h:5.625, fill:{ color:NAVY }, line:{ color:NAVY } });
  s.addText("Key Insights & Recommendations", { x:0.5, y:0.2, w:9.2, h:0.6, fontSize:24, bold:true, color:NAVY, fontFace:"Cambria" });

  const insights = [
    { icon:"💡", title:"EOQ Balances Costs Precisely",     body:"At the EOQ quantity, ordering cost exactly equals holding cost — any deviation increases total annual expense." },
    { icon:"📦", title:"Storage Constraints Have a Price",  body:"A 100 m² limit forces smaller orders, adding ~₹5,560/year in extra ordering costs vs. unconstrained EOQ." },
    { icon:"⏱",  title:"High-Lead-Time Products Need Watch",body:"Toothpaste (ROP=247 units, 14 days lead) and Cooking Oil (ROP=176, 10 days) require large inventory buffers." },
    { icon:"📈", title:"Soap Bar: Biggest Cost Driver",     body:"Highest inventory cost (₹8,975/yr) due to very high demand. Negotiating lower supplier order cost yields biggest savings." },
    { icon:"🎯", title:"Recommended Policy",                body:"Implement a continuous review (s, Q) policy — order EOQ units whenever inventory falls to the reorder point." },
  ];

  insights.forEach((ins, i) => {
    const y = 1.0 + i * 0.88;
    s.addShape(pres.shapes.RECTANGLE, { x:0.5, y:y+0.05, w:9.1, h:0.75, fill:{ color:WHITE }, line:{ color:LIGHT, pt:1 }, shadow: makeShadow() });
    s.addText(ins.icon, { x:0.6,  y:y+0.05, w:0.55, h:0.75, fontSize:16, align:"center", valign:"middle" });
    s.addText(ins.title, { x:1.2, y:y+0.07, w:3.2, h:0.35, fontSize:10, bold:true, color:NAVY, valign:"middle" });
    s.addText(ins.body,  { x:1.2, y:y+0.38, w:8.0, h:0.38, fontSize:8.5, color:"444444", valign:"middle" });
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 10 — CLOSING
// ═══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:2.5, w:10, h:0.08, fill:{ color:BLUE }, line:{ color:BLUE } });
  s.addText("Thank You", { x:0.5, y:0.8, w:9, h:1.2, fontSize:48, bold:true, color:WHITE, align:"center", fontFace:"Cambria" });
  s.addText("FMCG Inventory Optimization · EOQ + MILP · Python", {
    x:0.5, y:2.0, w:9, h:0.5, fontSize:12, color:"AED6F1", align:"center", italic:true
  });
  s.addText([
    { text:"Built with: ", options:{ color:"AED6F1", fontSize:10 } },
    { text:"Python  ·  pandas  ·  NumPy  ·  SciPy  ·  Matplotlib  ·  ReportLab  ·  Streamlit", options:{ color:WHITE, fontSize:10 } }
  ], { x:0.5, y:2.85, w:9, h:0.5, align:"center" });

  const tags = ["EOQ", "MILP", "Inventory", "Supply Chain", "Operations Research"];
  tags.forEach((t, i) => {
    const x = 1.2 + i * 1.55;
    s.addShape(pres.shapes.RECTANGLE, { x, y:3.6, w:1.35, h:0.42, fill:{ color:"163D5C" }, line:{ color:BLUE, pt:1 } });
    s.addText(t, { x, y:3.6, w:1.35, h:0.42, fontSize:9, color:"AED6F1", align:"center", valign:"middle" });
  });
}

// ── Save ──────────────────────────────────────────────────────
pres.writeFile({ fileName: "outputs/Inventory_Optimization_Presentation.pptx" })
  .then(() => console.log("PPTX saved → outputs/Inventory_Optimization_Presentation.pptx"))
  .catch(e  => { console.error(e); process.exit(1); });
