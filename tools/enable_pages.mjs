// Enable GitHub Pages on the repo (source: main, root) and report status.
import https from "node:https";

const token = process.env.DSH_SECRET_GITHUB_TOKEN;
if (!token) { console.log("NO TOKEN"); process.exit(1); }
const owner = "Tai-sura";
const repo = "phy11-projectile-ebook";

function api(method, path, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const req = https.request(
      {
        hostname: "api.github.com",
        path,
        method,
        headers: {
          Authorization: `token ${token}`,
          Accept: "application/vnd.github+json",
          "User-Agent": "dsh-ebook-bot",
          "X-GitHub-Api-Version": "2022-11-28",
          ...(data ? { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(data) } : {}),
        },
      },
      (res) => {
        let out = "";
        res.on("data", (c) => (out += c));
        res.on("end", () => resolve({ status: res.statusCode, body: out }));
      },
    );
    req.on("error", reject);
    if (data) req.write(data);
    req.end();
  });
}

let r = await api("POST", `/repos/${owner}/${repo}/pages`, { source: { branch: "main", path: "/" } });
console.log("enable pages:", r.status, r.status < 300 ? "requested" : r.body.slice(0, 300));

r = await api("GET", `/repos/${owner}/${repo}/pages`);
console.log("pages status:", r.status);
if (r.status === 200) {
  const p = JSON.parse(r.body);
  console.log("html_url:", p.html_url);
  console.log("build:", p.status, p.build_type || "");
}
