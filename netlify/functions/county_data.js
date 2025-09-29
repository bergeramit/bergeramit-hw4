// CommonJS for simplicity on Netlify
console.log("🚀 County data function is loading...");
const path = require("path");
const Database = require("better-sqlite3");

const ALLOWED = new Set([
  "Violent crime rate","Unemployment","Children in poverty","Diabetic screening",
  "Mammography screening","Preventable hospital stays","Uninsured",
  "Sexually transmitted infections","Physical inactivity","Adult obesity",
  "Premature Death","Daily fine particulate matter"
]);

const fs = require("fs");

function resolveDbPath() {
  const candidates = [
    path.join(process.cwd(), "data.db"),                                  // local dev (repo root)
    path.join(__dirname, "data.db"),                                      // some CLI builds
    process.env.LAMBDA_TASK_ROOT && path.join(process.env.LAMBDA_TASK_ROOT, "data.db") // prod
  ].filter(Boolean);

  for (const p of candidates) {
    try { if (fs.existsSync(p)) return p; } catch {}
  }
  throw new Error("data.db not found. Ensure it exists at repo root for dev, and is listed in included_files for prod.");
}

exports.handler = async (event) => {
  try {
    console.log("Event:", JSON.stringify(event));

    if ((event.headers?.["content-type"] || "").includes("application/json")
        && (event.body || "").includes("coffee=teapot")) {
      console.log("Pot request");
      return { statusCode: 418, body: "I'm a teapot" };
    }

    console.log("Parsing body");
    let data = {};
    try { data = JSON.parse(event.body || "{}"); }
    catch { return { statusCode: 400, body: JSON.stringify({ result: null, error: "Invalid JSON" }) }; }

    console.log("Validating zip");
    const zip = String(data.zip || "").replace(/[^0-9]/g, "");
    if (!/^\d{5}$/.test(zip)) {
      console.log("Invalid zip:", zip);
      return { statusCode: 400, body: JSON.stringify({ result: null, error: "Invalid zip code" }) };
    }

    console.log("Validating measure");
    const measure = String(data.measure_name || "").replace(/[^a-zA-Z\s]/g, "").trim();
    if (!ALLOWED.has(measure)) {
      console.log("Invalid measure:", measure);
      return { statusCode: 400, body: JSON.stringify({ result: null, error: "Invalid measure name" }) };
    }

    console.log("Resolving DB path");
    // 'included_files' places data.db inside the function bundle (read-only)
    // const dbPath = path.join(process.env.LAMBLA_TASK_ROOT || __dirname, "data.db");
    const db = new Database(resolveDbPath(), { readonly: true });

    const sql = `
      WITH zip_cty AS (
        SELECT DISTINCT county, default_state
        FROM zip_county
        WHERE zip = ?
      )
      SELECT chr.*
      FROM county_health_rankings AS chr
      JOIN zip_cty z
        ON chr.County = z.county AND chr.State = z.default_state
      WHERE LOWER(chr.Measure_name) = LOWER(?)
    `;
    const rows = db.prepare(sql).all(zip, measure);

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify(rows)
    };
  } catch (e) {
    return { statusCode: 500, body: JSON.stringify({ result: null, error: String(e) }) };
  }
};
