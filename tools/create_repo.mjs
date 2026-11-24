// Create the GitHub repo through the REST API (Node's TLS works where schannel fails).
import https from "node:https";

const token = process.env.DSH_SECRET_GITHUB_TOKEN;
if (!token) { console.log("NO TOKEN"); process.exit(1); }

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

const me = await api("GET", "/user");
if (me.status !== 200) { console.log("auth failed", me.status); process.exit(1); }
const login = JSON.parse(me.body).login;
console.log("login:", login);

const name = "phy11-projectile-ebook";
const made = await api("POST", "/user/repos", {
  name,
  description: "S4 Physics Ch11 Projectile Motion - interactive e-book reader",
  private: false,
  has_issues: true,
  auto_init: false,
});
console.log("create:", made.status, made.status === 201 ? "created" : made.body.slice(0, 160));
console.log("url:", `https://${login}.github.io/${name}/reader.html?book=phy11`);
